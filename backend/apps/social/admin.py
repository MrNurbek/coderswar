from django.contrib import admin
from .models import PeerReview, Notification, ActivityLog, Message


@admin.register(PeerReview)
class PeerReviewAdmin(admin.ModelAdmin):
    list_display  = ('reviewer', 'reviewee', 'topic_score', 'total_score', 'star_rating', 'created_at')
    list_filter   = ('star_rating',)
    search_fields = ('reviewer__username', 'reviewee__username')
    readonly_fields = ('created_at',)

    def total_score(self, obj):
        return obj.total_score
    total_score.short_description = 'Jami ball'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'notif_type', 'is_read', 'created_at')
    list_filter   = ('notif_type', 'is_read')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)

    actions = ['mark_all_read']

    @admin.action(description='Barcha tanlanganlarni o\'qilgan deb belgilash')
    def mark_all_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} ta bildirishnoma o\'qildi.')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display  = ('user', 'activity_type', 'date', 'created_at')
    list_filter   = ('activity_type', 'date')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    ordering      = ('-date', '-created_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display   = ('sender', 'recipient', 'subject', 'msg_type', 'is_read', 'created_at')
    list_filter    = ('msg_type', 'is_read')
    search_fields  = ('sender__username', 'recipient__username', 'subject')
    readonly_fields = ('created_at',)
    list_editable  = ('is_read',)
    raw_id_fields  = ('sender', 'recipient', 'related_topic', 'parent')
