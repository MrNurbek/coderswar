from datetime import date, timedelta
from django.db import models
from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import PeerReview, Notification, ActivityLog, Message
from .serializers import (
    PeerReviewSerializer, PeerReviewCreateSerializer,
    NotificationSerializer, ActivityLogSerializer, StreakSerializer,
    MessageSerializer, MessageCreateSerializer, MessageReplySerializer, RecipientSerializer,
)


# ─── PeerReview ───────────────────────────────────────────────────────────────

class PeerReviewQueueView(generics.ListAPIView):
    """
    Baholanishi kerak bo'lgan mavzular ro'yxati.
    Joriy foydalanuvchi baholamagan, boshqa talabalarning tugatilgan mavzulari.
    """
    serializer_class   = PeerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from apps.courses.models import TopicScore
        user = self.request.user

        # Allaqachon baholangan topic_score idlari
        already_reviewed = PeerReview.objects.filter(
            reviewer=user
        ).values_list('topic_score_id', flat=True)

        return TopicScore.objects.filter(
            is_completed=True,
        ).exclude(
            student=user,
        ).exclude(
            id__in=already_reviewed,
        ).select_related('student', 'topic').order_by('?')[:20]  # tasodifiy 20 ta

    def list(self, request, *args, **kwargs):
        from apps.courses.serializers import TopicScoreSerializer
        qs = self.get_queryset()
        return Response(TopicScoreSerializer(qs, many=True).data)


class PeerReviewCreateView(generics.CreateAPIView):
    serializer_class   = PeerReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        topic_score = serializer.validated_data['topic_score']
        review = serializer.save(
            reviewer=self.request.user,
            reviewee=topic_score.student,
        )

        # Re (reflektiv) balini oshirish — baholovchiga +2 ball
        self._reward_reviewer(review)

        # Bildirishnoma yuborish
        self._notify_reviewee(review)

        # Badge tekshiruvi — peer_reviews shart
        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(self.request.user)
        except Exception:
            pass

    def _reward_reviewer(self, review):
        try:
            from apps.courses.models import TopicScore
            ts = TopicScore.objects.get(
                student=self.request.user,
                topic=review.topic_score.topic,
            )
            ts.re_score = min(10, ts.re_score + 2)
            ts.save()
        except Exception:
            pass

    def _notify_reviewee(self, review):
        topic_title = review.topic_score.topic.title
        Notification.objects.create(
            user=review.reviewee,
            title='Peer Review olindi',
            message=(
                f'{review.reviewer.get_full_name()} siz bajargan '
                f'"{topic_title}" mavzusini baholadi. '
                f'Umumiy ball: {review.total_score}/90'
            ),
            notif_type=Notification.NotifType.PEER_REVIEW,
        )


class PeerReviewListView(generics.ListAPIView):
    """Foydalanuvchi bergan yoki olgan reviewlar."""
    serializer_class   = PeerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        direction = self.request.query_params.get('direction', 'given')  # given | received
        user = self.request.user
        if direction == 'received':
            return PeerReview.objects.filter(reviewee=user).select_related(
                'reviewer', 'reviewee', 'topic_score__topic'
            )
        return PeerReview.objects.filter(reviewer=user).select_related(
            'reviewer', 'reviewee', 'topic_score__topic'
        )


class PeerReviewLeaderboardView(generics.ListAPIView):
    """Ko'p review bergan talabalar."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        from apps.users.serializers import UserMiniSerializer
        from apps.users.models import User

        qs = (
            PeerReview.objects
            .values('reviewer')
            .annotate(review_count=Count('id'))
            .order_by('-review_count')[:20]
        )

        result = []
        for i, item in enumerate(qs):
            try:
                user = User.objects.get(id=item['reviewer'])
                result.append({
                    'rank':         i + 1,
                    'user':         UserMiniSerializer(user).data,
                    'review_count': item['review_count'],
                })
            except User.DoesNotExist:
                pass

        return Response(result)


# ─── Notification ─────────────────────────────────────────────────────────────

class NotificationListView(generics.ListAPIView):
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['notif_type', 'is_read']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Barcha bildirishnomalarni o'qilgan deb belgilash."""
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked': count})

    def patch(self, request, pk):
        """Bitta bildirishnomani o'qilgan deb belgilash."""
        try:
            notif = Notification.objects.get(id=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(status=404)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notif).data)


# ─── ActivityLog & Streak ────────────────────────────────────────────────────

class ActivityLogView(generics.ListAPIView):
    serializer_class   = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id', self.request.user.id)
        return ActivityLog.objects.filter(user_id=user_id).order_by('-date')[:365]


class StreakView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id=None):
        from apps.users.models import StudentProfile
        uid = user_id or request.user.id

        try:
            profile = StudentProfile.objects.get(user_id=uid)
        except StudentProfile.DoesNotExist:
            return Response({'detail': 'Profil topilmadi.'}, status=404)

        # Heatmap — so'nggi 365 kun
        today = date.today()
        start = today - timedelta(days=364)
        logs  = (
            ActivityLog.objects
            .filter(user_id=uid, date__gte=start)
            .values('date')
            .annotate(count=Count('id'))
        )
        heatmap = {str(row['date']): row['count'] for row in logs}

        data = {
            'current_streak':    profile.current_streak,
            'max_streak':        profile.max_streak,
            'last_active':       profile.last_active,
            'activity_heatmap':  heatmap,
        }
        return Response(StreakSerializer(data).data)


class LogActivityView(APIView):
    """Faollikni qayd etish (login, mavzu ko'rish, va h.k.)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        activity_type = request.data.get('activity_type', ActivityLog.ActivityType.LOGIN)
        detail        = request.data.get('detail', {})
        today         = date.today()

        ActivityLog.objects.get_or_create(
            user=request.user,
            activity_type=activity_type,
            date=today,
            defaults={'detail': detail},
        )

        # Streak yangilash
        self._update_streak(request.user, today)
        return Response({'detail': 'Faollik qayd etildi.'})

    def _update_streak(self, user, today):
        from apps.users.models import StudentProfile
        try:
            profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            return

        last = profile.last_active
        if last == today:
            return  # Bugun allaqachon qayd etilgan

        streak_grew = False
        if last == today - timedelta(days=1):
            profile.current_streak += 1
            streak_grew = True
        else:
            profile.current_streak = 1  # Streak uzildi
            streak_grew = True

        profile.max_streak  = max(profile.max_streak, profile.current_streak)
        profile.last_active = today
        profile.save(update_fields=['current_streak', 'max_streak', 'last_active'])

        # Streak oshsa — faol mavzuga +1 MO ball (max 5 jami)
        if streak_grew:
            self._award_streak_mo(user)

        # Badge tekshiruvi — streak_days shartlari
        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(user)
        except Exception:
            pass

    @staticmethod
    def _award_streak_mo(user):
        """
        Login streaki oshganda eng so'nggi faol mavzuga +1 MO ball berish.
        MO_LOGIN_MAX = 5 — bir mavzu uchun jami maksimal.
        """
        from apps.courses.models import TopicScore, Topic
        try:
            # Eng so'nggi yangilangan, tugatilmagan mavzuni topish
            ts = (
                TopicScore.objects
                .filter(student=user, mo_score__lt=Topic.MAX_MO)
                .order_by('-updated_at')
                .first()
            )
            if not ts:
                return

            # MO_LOGIN_MAX = 5 — login qismi uchun chegara
            login_mo_given = max(0, ts.mo_score - Topic.MO_CONTENT_MAX)
            if login_mo_given >= Topic.MO_LOGIN_MAX:
                return

            ts.mo_score = min(Topic.MAX_MO, ts.mo_score + 1)
            ts.save(update_fields=['mo_score'])

            # Bildiruv (faqat streak ≥ 3 dan boshlab — kamroq shovqin)
            try:
                profile = user.student_profile
                if profile.current_streak >= 3:
                    Notification.objects.create(
                        user=user,
                        title=f'{profile.current_streak} kunlik streak! 🔥',
                        message=(
                            f'Ketma-ket {profile.current_streak} kun faolsiz. '
                            f'"{ts.topic.title}" mavzusiga +1 MO ball qo\'shildi!'
                        ),
                        notif_type='system',
                    )
            except Exception:
                pass

        except Exception:
            pass


# ─── Message ─────────────────────────────────────────────────────────────────

class MessageInboxView(generics.ListAPIView):
    """Kiruvchi xabarlar (qabul qilingan)."""
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = None

    def get_queryset(self):
        qs = Message.objects.filter(
            recipient=self.request.user, parent__isnull=True
        ).select_related('sender', 'recipient', 'related_topic')
        msg_type = self.request.query_params.get('msg_type')
        if msg_type:
            qs = qs.filter(msg_type=msg_type)
        return qs


class MessageSentView(generics.ListAPIView):
    """Chiquvchi xabarlar (yuborilgan)."""
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = None

    def get_queryset(self):
        return Message.objects.filter(
            sender=self.request.user, parent__isnull=True
        ).select_related('sender', 'recipient', 'related_topic')


class MessageDetailView(generics.RetrieveAPIView):
    """Xabar va javoblari."""
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient', 'related_topic')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.recipient == request.user and not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])
        replies = instance.replies.select_related('sender', 'recipient').all()
        data = self.get_serializer(instance).data
        data['replies'] = MessageSerializer(replies, many=True).data
        return Response(data)


class MessageCreateView(generics.CreateAPIView):
    """Yangi xabar yuborish."""
    serializer_class   = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        msg = serializer.save(sender=self.request.user)
        self._notify(msg)

    def _notify(self, msg):
        type_labels = {
            'complaint':    'Shikoyat',
            'question':     'Savol',
            'advisory':     'Tavsiya',
            'announcement': "E'lon",
            'general':      'Xabar',
        }
        label = type_labels.get(msg.msg_type, 'Xabar')
        Notification.objects.create(
            user=msg.recipient,
            title=f'Yangi {label}: {msg.subject[:60]}',
            message=(
                f'{msg.sender.get_full_name()} sizga xabar yubordi. '
                f'Mavzu: {msg.subject[:80]}'
            ),
            notif_type=Notification.NotifType.SYSTEM,
            link='/messages.html',
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(MessageSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)


class MessageReplyView(generics.CreateAPIView):
    """Xabarga javob yozish."""
    serializer_class   = MessageReplySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        parent = generics.get_object_or_404(Message, pk=self.kwargs['pk'])
        user   = self.request.user
        if parent.sender != user and parent.recipient != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Bu xabarga javob yubora olmaysiz.')
        reply_to = parent.sender if parent.sender != user else parent.recipient
        msg = serializer.save(
            sender=user,
            recipient=reply_to,
            parent=parent,
            subject=f'Re: {parent.subject}',
        )
        Notification.objects.create(
            user=reply_to,
            title=f'Xabarga javob: {parent.subject[:60]}',
            message=f'{user.get_full_name()} xabarga javob yozdi.',
            notif_type=Notification.NotifType.SYSTEM,
            link='/messages.html',
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(MessageSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)


class MessageReadView(APIView):
    """Xabarni o'qilgan deb belgilash."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            msg = Message.objects.get(pk=pk, recipient=request.user)
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        msg.is_read = True
        msg.save(update_fields=['is_read'])
        return Response({'ok': True})


class MessageUnreadCountView(APIView):
    """O'qilmagan xabarlar soni."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread': count})


class MessageRecipientsView(APIView):
    """Xabar yuborish mumkin bo'lgan qabul qiluvchilar ro'yxati."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.users.models import User, GroupMembership
        user = request.user
        R    = User.Role

        if user.role in (R.ADMIN, R.SUPERADMIN):
            qs = User.objects.exclude(pk=user.pk).filter(is_active=True)
        elif user.role == R.TEACHER:
            student_ids = GroupMembership.objects.filter(
                group__teacher=user
            ).values_list('student_id', flat=True)
            qs = User.objects.filter(is_active=True).filter(
                Q(id__in=student_ids) |
                Q(role__in=[R.ADMIN, R.SUPERADMIN])
            ).exclude(pk=user.pk)
        else:
            teacher_ids = GroupMembership.objects.filter(
                student=user
            ).values_list('group__teacher_id', flat=True)
            qs = User.objects.filter(is_active=True).filter(
                Q(id__in=teacher_ids) |
                Q(role__in=[R.ADMIN, R.SUPERADMIN])
            ).exclude(pk=user.pk)

        return Response(RecipientSerializer(qs, many=True).data)
