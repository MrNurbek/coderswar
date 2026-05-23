from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class PeerReview(models.Model):
    """Talabaning boshqa talaba kodini baholashi (Peer Review)."""

    reviewer      = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='peer_reviews_given'
    )
    reviewee      = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='peer_reviews_received'
    )
    topic_score   = models.ForeignKey(
        'courses.TopicScore', on_delete=models.CASCADE, related_name='peer_reviews'
    )

    # 3 ta mezon (Mo — o'qituvchi, Re — peer review uchun alohida)
    ko_score = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(30)], help_text='Kognitiv (0–30)'
    )
    fa_score = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(35)], help_text='Faoliyatli (0–35)'
    )
    re_score = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(20)], help_text='Refleksiv-baholovchi (0–20)'
    )

    comment    = models.TextField()
    star_rating = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'topic_score')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reviewer} → {self.reviewee} | {self.topic_score.topic}'

    @property
    def total_score(self):
        return self.ko_score + self.fa_score + self.re_score


class Notification(models.Model):
    """Foydalanuvchi bildirishnomalari."""

    class NotifType(models.TextChoices):
        SYSTEM      = 'system',      'Tizim'
        DUEL        = 'duel',        'Duel'
        CLAN        = 'clan',        'Klan'
        PEER_REVIEW = 'peer_review', 'Peer Review'
        BADGE       = 'badge',       'Nishon'
        TOPIC       = 'topic',       'Mavzu'
        TEACHER     = 'teacher',     "O'qituvchi"

    user      = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title     = models.CharField(max_length=200)
    message   = models.TextField()
    notif_type = models.CharField(max_length=15, choices=NotifType.choices, default=NotifType.SYSTEM)
    is_read   = models.BooleanField(default=False)
    link      = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} | {self.title}'


class ActivityLog(models.Model):
    """Foydalanuvchi kunlik faollik yozuvi (streak uchun)."""

    class ActivityType(models.TextChoices):
        LOGIN      = 'login',      'Kirish'
        TOPIC      = 'topic',      'Mavzu'
        SUBMISSION = 'submission', 'Kod topshirish'
        DUEL       = 'duel',       'Duel'
        REVIEW     = 'review',     'Review'

    user          = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=15, choices=ActivityType.choices)
    date          = models.DateField()
    detail        = models.JSONField(default=dict, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        indexes = [models.Index(fields=['user', 'date'])]

    def __str__(self):
        return f'{self.user} | {self.activity_type} | {self.date}'
