from django.urls import path
from .views import (
    PeerReviewQueueView, PeerReviewCreateView, PeerReviewListView,
    PeerReviewLeaderboardView,
    NotificationListView, NotificationMarkReadView,
    ActivityLogView, StreakView, LogActivityView,
)

urlpatterns = [
    # Peer Review
    path('peer-review/queue/',        PeerReviewQueueView.as_view(),       name='pr_queue'),
    path('peer-review/create/',       PeerReviewCreateView.as_view(),      name='pr_create'),
    path('peer-review/',              PeerReviewListView.as_view(),        name='pr_list'),
    path('peer-review/leaderboard/',  PeerReviewLeaderboardView.as_view(), name='pr_leaderboard'),

    # Notifications
    path('notifications/',            NotificationListView.as_view(),      name='notif_list'),
    path('notifications/read-all/',   NotificationMarkReadView.as_view(),  name='notif_read_all'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notif_read_one'),

    # Activity & Streak
    path('activity/',                 ActivityLogView.as_view(),           name='activity_mine'),
    path('activity/<int:user_id>/',   ActivityLogView.as_view(),           name='activity_user'),
    path('streak/',                   StreakView.as_view(),                name='streak_mine'),
    path('streak/<int:user_id>/',     StreakView.as_view(),                name='streak_user'),
    path('activity/log/',             LogActivityView.as_view(),           name='activity_log'),
]
