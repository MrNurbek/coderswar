from rest_framework import serializers
from apps.users.serializers import UserMiniSerializer
from apps.users.models import User
from .models import PeerReview, Notification, ActivityLog, Message


# ─── PeerReview ───────────────────────────────────────────────────────────────

class PeerReviewSerializer(serializers.ModelSerializer):
    reviewer     = UserMiniSerializer(read_only=True)
    reviewee     = UserMiniSerializer(read_only=True)
    total_score  = serializers.ReadOnlyField()
    topic_title  = serializers.CharField(source='topic_score.topic.title', read_only=True)
    topic_number = serializers.IntegerField(source='topic_score.topic.number', read_only=True)

    class Meta:
        model  = PeerReview
        fields = (
            'id', 'reviewer', 'reviewee', 'topic_score',
            'topic_title', 'topic_number',
            'mo_score', 'ko_score', 'fa_score', 're_score',
            'total_score', 'comment', 'star_rating', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        limits = {'mo_score': 15, 'ko_score': 30, 'fa_score': 35, 're_score': 20}
        for field, limit in limits.items():
            val = attrs.get(field)
            if val is not None and val > limit:
                raise serializers.ValidationError({field: f'Maksimal: {limit}'})
        return attrs


class PeerReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PeerReview
        fields = (
            'topic_score',
            'mo_score', 'ko_score', 'fa_score', 're_score',
            'comment', 'star_rating',
        )

    def validate_topic_score(self, value):
        """Faqat tugatilgan mavzular baholanishi mumkin."""
        if not value.is_completed:
            raise serializers.ValidationError('Bu mavzu hali tugatilmagan.')
        return value

    def validate(self, attrs):
        request = self.context['request']
        topic_score = attrs['topic_score']

        # O'zini o'zi baholay olmasin
        if topic_score.student == request.user:
            raise serializers.ValidationError('O\'zingizni baholay olmaysiz.')

        # Allaqachon baholan bo'lsa
        if PeerReview.objects.filter(
            reviewer=request.user, topic_score=topic_score
        ).exists():
            raise serializers.ValidationError('Siz bu mavzuni allaqachon baholagansiz.')

        return attrs


# ─── Notification ─────────────────────────────────────────────────────────────

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ('id', 'title', 'message', 'notif_type', 'is_read', 'link', 'created_at')
        read_only_fields = ('id', 'created_at')


# ─── ActivityLog ─────────────────────────────────────────────────────────────

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ActivityLog
        fields = ('id', 'activity_type', 'date', 'detail', 'created_at')
        read_only_fields = ('id', 'created_at')


class StreakSerializer(serializers.Serializer):
    """Streak ma'lumotlari."""
    current_streak = serializers.IntegerField()
    max_streak     = serializers.IntegerField()
    last_active    = serializers.DateField(allow_null=True)
    activity_heatmap = serializers.DictField()  # {date_str: count}


# ─── Message ─────────────────────────────────────────────────────────────────

class MessageSerializer(serializers.ModelSerializer):
    sender    = UserMiniSerializer(read_only=True)
    recipient = UserMiniSerializer(read_only=True)
    topic_title = serializers.CharField(source='related_topic.title', read_only=True, allow_null=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = (
            'id', 'sender', 'recipient', 'subject', 'body',
            'msg_type', 'related_topic', 'topic_title',
            'parent', 'reply_count', 'is_read', 'created_at',
        )
        read_only_fields = ('id', 'created_at', 'is_read')

    def get_reply_count(self, obj):
        return obj.replies.count()


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Message
        fields = ('recipient', 'subject', 'body', 'msg_type', 'related_topic', 'parent')

    def validate(self, attrs):
        request  = self.context['request']
        sender   = request.user
        recipient = attrs['recipient']

        if sender == recipient:
            raise serializers.ValidationError('O\'zingizga xabar yubora olmaysiz.')

        allowed = self._check_permission(sender.role, recipient.role)
        if not allowed:
            raise serializers.ValidationError(
                f'{sender.get_role_display()} {recipient.get_role_display()}ga xabar yubora olmaydi.'
            )
        return attrs

    @staticmethod
    def _check_permission(sender_role, recipient_role):
        R = User.Role
        rules = {
            R.STUDENT:    {R.TEACHER, R.ADMIN, R.SUPERADMIN},
            R.TEACHER:    {R.STUDENT, R.ADMIN, R.SUPERADMIN},
            R.ADMIN:      {R.STUDENT, R.TEACHER, R.ADMIN, R.SUPERADMIN},
            R.SUPERADMIN: {R.STUDENT, R.TEACHER, R.ADMIN, R.SUPERADMIN},
        }
        return recipient_role in rules.get(sender_role, set())


class MessageReplySerializer(serializers.ModelSerializer):
    """Javob yozish uchun — faqat body talab qilinadi."""
    class Meta:
        model  = Message
        fields = ('body',)


class RecipientSerializer(serializers.ModelSerializer):
    """Xabar yuborish uchun qabul qiluvchilar ro'yxati."""
    full_name  = serializers.SerializerMethodField()
    role_label = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model  = User
        fields = ('id', 'full_name', 'role', 'role_label', 'email')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
