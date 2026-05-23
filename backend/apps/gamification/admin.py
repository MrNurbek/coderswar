from django.contrib import admin
from .models import Duel, Clan, ClanMembership, ClanWar, ClanChat, Badge, UserBadge


@admin.register(Duel)
class DuelAdmin(admin.ModelAdmin):
    list_display  = ('challenger', 'opponent', 'duel_type', 'status', 'winner',
                     'challenger_score', 'opponent_score', 'created_at')
    list_filter   = ('status', 'duel_type')
    search_fields = ('challenger__username', 'opponent__username', 'room_id')
    readonly_fields = ('room_id', 'created_at', 'started_at', 'ended_at')


class ClanMembershipInline(admin.TabularInline):
    model  = ClanMembership
    extra  = 0
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)


@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display  = ('name', 'tag', 'emblem', 'leader', 'rating_score', 'is_active', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('name', 'tag')
    list_editable = ('is_active',)
    inlines       = [ClanMembershipInline]
    readonly_fields = ('created_at',)


@admin.register(ClanMembership)
class ClanMembershipAdmin(admin.ModelAdmin):
    list_display  = ('user', 'clan', 'role', 'joined_at')
    list_filter   = ('role', 'clan')
    search_fields = ('user__username', 'clan__name')


@admin.register(ClanWar)
class ClanWarAdmin(admin.ModelAdmin):
    list_display  = ('clan1', 'clan2', 'war_type', 'status', 'winner',
                     'clan1_score', 'clan2_score', 'scheduled_at')
    list_filter   = ('status', 'war_type')
    search_fields = ('clan1__name', 'clan2__name')


@admin.register(ClanChat)
class ClanChatAdmin(admin.ModelAdmin):
    list_display  = ('user', 'clan', 'message', 'created_at')
    list_filter   = ('clan',)
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display  = ('icon', 'name', 'badge_type', 'is_active')
    list_filter   = ('badge_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display  = ('user', 'badge', 'earned_at')
    list_filter   = ('badge__badge_type',)
    search_fields = ('user__username', 'badge__name')
    readonly_fields = ('earned_at',)
