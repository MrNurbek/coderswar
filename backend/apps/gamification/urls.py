from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DuelViewSet, ClanViewSet, ClanWarViewSet,
    LeaderboardView, ClanLeaderboardView,
    BadgeListView, MyBadgesView,
    InventoryView, EquipItemView, EquippedBonusView,
)

router = DefaultRouter()
router.register('duels',     DuelViewSet,    basename='duel')
router.register('clans',     ClanViewSet,    basename='clan')
router.register('clan-wars', ClanWarViewSet, basename='clan-war')

urlpatterns = [
    path('leaderboard/',           LeaderboardView.as_view(),      name='leaderboard'),
    path('leaderboard/clans/',     ClanLeaderboardView.as_view(),  name='clan_leaderboard'),
    path('badges/',                BadgeListView.as_view(),        name='badge_list'),
    path('badges/mine/',           MyBadgesView.as_view(),         name='my_badges'),
    # Inventory
    path('inventory/',             InventoryView.as_view(),        name='inventory'),
    path('inventory/<int:pk>/equip/', EquipItemView.as_view(),     name='equip_item'),
    path('inventory/equipped/',    EquippedBonusView.as_view(),    name='equipped_bonus'),
    path('', include(router.urls)),
]
