from datetime import date, timedelta
from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import PeerReview, Notification, ActivityLog
from .serializers import (
    PeerReviewSerializer, PeerReviewCreateSerializer,
    NotificationSerializer, ActivityLogSerializer, StreakSerializer,
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
        elif last == today - timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1  # Streak uzildi

        profile.max_streak  = max(profile.max_streak, profile.current_streak)
        profile.last_active = today
        profile.save(update_fields=['current_streak', 'max_streak', 'last_active'])

        # Badge tekshiruvi — streak_days shartlari
        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(user)
        except Exception:
            pass
