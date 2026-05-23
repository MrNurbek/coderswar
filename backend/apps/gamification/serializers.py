from rest_framework import serializers
from apps.users.serializers import UserMiniSerializer
from .models import Duel, Clan, ClanMembership, ClanWar, ClanChat, Badge, UserBadge, Equipment, UserEquipment  # noqa


# ─── Equipment ───────────────────────────────────────────────────────────────

class EquipmentSerializer(serializers.ModelSerializer):
    color = serializers.ReadOnlyField()

    class Meta:
        model  = Equipment
        fields = ('id', 'name', 'icon', 'image_path', 'eq_type', 'rarity', 'color',
                  'attack_bonus', 'defense_bonus', 'description')


class UserEquipmentSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(read_only=True)

    class Meta:
        model  = UserEquipment
        fields = ('id', 'equipment', 'is_equipped', 'acquired_at')


# ─── Badge ────────────────────────────────────────────────────────────────────

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Badge
        fields = ('id', 'name', 'description', 'icon', 'badge_type', 'condition', 'is_active')


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)

    class Meta:
        model  = UserBadge
        fields = ('id', 'badge', 'earned_at')


# ─── Duel ────────────────────────────────────────────────────────────────────

class DuelSerializer(serializers.ModelSerializer):
    challenger          = UserMiniSerializer(read_only=True)
    opponent            = UserMiniSerializer(read_only=True)
    winner              = UserMiniSerializer(read_only=True)
    task_title          = serializers.CharField(source='task.title',          read_only=True, default='')
    challenger_username = serializers.CharField(source='challenger.username', read_only=True, default='')
    opponent_username   = serializers.CharField(source='opponent.username',   read_only=True, default='')
    winner_username     = serializers.CharField(source='winner.username',     read_only=True, default='')

    class Meta:
        model  = Duel
        fields = (
            'id', 'challenger', 'challenger_username',
            'opponent', 'opponent_username',
            'task', 'task_title',
            'duel_type', 'status',
            'winner', 'winner_username',
            'challenger_score', 'opponent_score',
            'rating_reward', 'room_id',
            'started_at', 'ended_at', 'created_at',
        )
        read_only_fields = (
            'id', 'status', 'winner', 'challenger_score', 'opponent_score',
            'room_id', 'started_at', 'ended_at', 'created_at',
        )


class DuelCreateSerializer(serializers.Serializer):
    """Duel yaratish — task ixtiyoriy (tanlansa o'sha, yo'q bo'lsa random)."""
    task      = serializers.IntegerField(required=False, allow_null=True)
    duel_type = serializers.ChoiceField(
        choices=['algorithmic', 'debugging', 'optimization'],
        default='algorithmic',
        required=False,
    )


# ─── Clan ────────────────────────────────────────────────────────────────────

class ClanMembershipSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model  = ClanMembership
        fields = ('id', 'user', 'role', 'joined_at')
        read_only_fields = ('id', 'joined_at')


class ClanSerializer(serializers.ModelSerializer):
    leader       = UserMiniSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    my_role      = serializers.SerializerMethodField()

    class Meta:
        model  = Clan
        fields = (
            'id', 'name', 'tag', 'emblem', 'description',
            'leader', 'rating_score', 'is_active',
            'member_count', 'my_role', 'created_at',
        )
        read_only_fields = ('id', 'rating_score', 'is_active', 'created_at')

    def get_member_count(self, obj):
        return obj.memberships.count()

    def get_my_role(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        try:
            m = obj.memberships.get(user=request.user)
            return m.role
        except ClanMembership.DoesNotExist:
            return None


class ClanDetailSerializer(ClanSerializer):
    members = ClanMembershipSerializer(source='memberships', many=True, read_only=True)

    class Meta(ClanSerializer.Meta):
        fields = ClanSerializer.Meta.fields + ('members',)


# ─── ClanWar ─────────────────────────────────────────────────────────────────

class ClanWarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ClanWar
        fields = ('clan2', 'war_type', 'scheduled_at')


class ClanWarSerializer(serializers.ModelSerializer):
    clan1  = ClanSerializer(read_only=True)
    clan2  = ClanSerializer(read_only=True)
    winner = ClanSerializer(read_only=True)

    class Meta:
        model  = ClanWar
        fields = (
            'id', 'clan1', 'clan2', 'war_type', 'status', 'winner',
            'clan1_score', 'clan2_score', 'scheduled_at', 'started_at', 'ended_at',
        )
        read_only_fields = ('id', 'status', 'winner', 'clan1_score', 'clan2_score',
                            'started_at', 'ended_at')


# ─── ClanChat ────────────────────────────────────────────────────────────────

class ClanChatSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model  = ClanChat
        fields = ('id', 'user', 'message', 'created_at')
        read_only_fields = ('id', 'created_at')


class ClanChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ClanChat
        fields = ('message',)
