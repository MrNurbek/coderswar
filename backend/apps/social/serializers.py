from rest_framework import serializers
from apps.users.serializers import UserMiniSerializer
from .models import PeerReview, Notification, ActivityLog


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
            'ko_score', 'fa_score', 're_score',
            'total_score', 'comment', 'star_rating', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        limits = {'ko_score': 30, 'fa_score': 35, 're_score': 20}
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
            'ko_score', 'fa_score', 're_score',
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
