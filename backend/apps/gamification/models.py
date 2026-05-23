import random
from django.db import models


# ─── Equipment (Qurol-Aslahalar) ─────────────────────────────────────────────

class Equipment(models.Model):
    """Qurol va aslahalar ta'rifi."""

    class Type(models.TextChoices):
        WEAPON = 'weapon', 'Qurol'
        ARMOR  = 'armor',  'Zirh'
        RING   = 'ring',   'Uzuk'
        BOOTS  = 'boots',  'Etik'
        HELMET = 'helmet', 'Dubulg\'a'
        SHIELD = 'shield', 'Qalqon'

    class Rarity(models.TextChoices):
        COMMON    = 'common',    'Oddiy'
        RARE      = 'rare',      'Noyob'
        EPIC      = 'epic',      'Epic'
        LEGENDARY = 'legendary', 'Afsonaviy'

    RARITY_COLORS = {
        'common':    '#94a3b8',
        'rare':      '#4299e1',
        'epic':      '#a855f7',
        'legendary': '#ffd700',
    }

    name          = models.CharField(max_length=100)
    icon          = models.CharField(max_length=10)
    image_path    = models.CharField(max_length=200, blank=True, help_text='Frontend static rasmi: /static/frontend/img/equipment/...')
    eq_type       = models.CharField(max_length=10, choices=Type.choices)
    rarity        = models.CharField(max_length=10, choices=Rarity.choices, default=Rarity.COMMON)
    attack_bonus  = models.SmallIntegerField(default=0,  help_text='Duelda qo\'shimcha ball % (g\'olib)')
    defense_bonus = models.SmallIntegerField(default=0,  help_text='Duelda yo\'qotish % kamayadi (mag\'lub)')
    description   = models.CharField(max_length=200, blank=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['rarity', 'eq_type', 'name']

    def __str__(self):
        return f'{self.icon} {self.name} ({self.rarity})'

    @property
    def color(self):
        return self.RARITY_COLORS.get(self.rarity, '#94a3b8')


class UserEquipment(models.Model):
    """Foydalanuvchi inventari."""
    user        = models.ForeignKey('users.User',   on_delete=models.CASCADE, related_name='inventory')
    equipment   = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='owners')
    is_equipped = models.BooleanField(default=False)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-acquired_at']

    def __str__(self):
        status = '(kiyilgan)' if self.is_equipped else ''
        return f'{self.user} — {self.equipment} {status}'

    @classmethod
    def equip(cls, user, item_id):
        """Bir slot uchun faqat bitta narsa kiyilishi mumkin."""
        ue = cls.objects.select_related('equipment').get(id=item_id, user=user)
        slot = ue.equipment.eq_type
        # Avvalgi kiyilganini yechib qo'yamiz
        cls.objects.filter(user=user, equipment__eq_type=slot, is_equipped=True).update(is_equipped=False)
        ue.is_equipped = True
        ue.save(update_fields=['is_equipped'])
        return ue

    @classmethod
    def unequip(cls, user, item_id):
        cls.objects.filter(id=item_id, user=user).update(is_equipped=False)

    @classmethod
    def get_equipped_bonuses(cls, user):
        """Foydalanuvchining kiyilgan jihozlaridan umumiy bonus."""
        items = cls.objects.filter(user=user, is_equipped=True).select_related('equipment')
        attack  = sum(i.equipment.attack_bonus  for i in items)
        defense = sum(i.equipment.defense_bonus for i in items)
        return attack, defense


# ─── Drop Logic ───────────────────────────────────────────────────────────────

# Har bir (level, category) uchun: [drop_chance, common%, rare%, epic%, legendary%]
DROP_TABLE = {
    ('beginner',     'exercise'): (0.15, 70, 25,  5,  0),
    ('intermediate', 'exercise'): (0.20, 55, 35,  9,  1),
    ('advanced',     'exercise'): (0.25, 40, 40, 17,  3),
    ('beginner',     'project'):  (0.35, 50, 35, 12,  3),
    ('intermediate', 'project'):  (0.45, 35, 40, 20,  5),
    ('advanced',     'project'):  (0.55, 20, 40, 30, 10),
}


def roll_equipment_drop(user, task_level: str, task_category: str):
    """
    Topshiriq o'tganda random qurol/aslaha tushiradi.
    Agar tushsa — UserEquipment yaratib, qaytaradi. Aks holda None.
    """
    config = DROP_TABLE.get((task_level, task_category))
    if not config:
        return None

    drop_chance, w_common, w_rare, w_epic, w_legendary = config

    # Tushyaptimi?
    if random.random() > drop_chance:
        return None

    # Qanday rarity?
    rarity = random.choices(
        ['common', 'rare', 'epic', 'legendary'],
        weights=[w_common, w_rare, w_epic, w_legendary],
        k=1,
    )[0]

    items = list(Equipment.objects.filter(rarity=rarity, is_active=True))
    if not items:
        return None

    chosen = random.choice(items)
    ue = UserEquipment.objects.create(user=user, equipment=chosen)
    return ue


class Duel(models.Model):
    """Ikki talaba o'rtasidagi real-vaqt musobaqasi."""

    class DuelType(models.TextChoices):
        ALGORITHMIC = 'algorithmic', 'Algoritmik'
        DEBUG       = 'debug',       'Debug'
        COMPLEX     = 'complex',     'Kompleks'

    class Status(models.TextChoices):
        WAITING     = 'waiting',     'Kutilmoqda'
        IN_PROGRESS = 'in_progress', 'Davom etmoqda'
        COMPLETED   = 'completed',   'Yakunlandi'
        CANCELLED   = 'cancelled',   'Bekor qilindi'

    challenger        = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='duels_challenged'
    )
    opponent          = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='duels_opposed', null=True, blank=True
    )
    task              = models.ForeignKey('courses.Task', on_delete=models.SET_NULL, null=True)
    duel_type         = models.CharField(max_length=15, choices=DuelType.choices, default=DuelType.ALGORITHMIC)
    status            = models.CharField(max_length=15, choices=Status.choices, default=Status.WAITING)
    winner            = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='duels_won'
    )
    challenger_code   = models.TextField(blank=True)
    opponent_code     = models.TextField(blank=True)
    challenger_score  = models.PositiveSmallIntegerField(default=0)
    opponent_score    = models.PositiveSmallIntegerField(default=0)
    rating_reward     = models.PositiveSmallIntegerField(default=15)
    room_id           = models.CharField(max_length=50, unique=True)
    started_at        = models.DateTimeField(null=True, blank=True)
    ended_at          = models.DateTimeField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.challenger} vs {self.opponent} [{self.status}]'

    def finish(self, winner_user, loser_user):
        """
        Dualni yakunlash — equipment bonuslari hisobga olinadi.
        G'olib: +rating_reward * (1 + attack_bonus/100)
        Mag'lub: -rating_reward * (1 - defense_bonus/100)  (min 0)
        """
        from apps.users.models import StudentProfile

        win_atk, _   = UserEquipment.get_equipped_bonuses(winner_user)
        _, los_def   = UserEquipment.get_equipped_bonuses(loser_user)

        base = self.rating_reward
        win_pts  = round(base * (1 + win_atk / 100))
        lose_pts = max(0, round(base * (1 - los_def / 100)))

        # G'olib
        try:
            wp = StudentProfile.objects.get(user=winner_user)
            wp.rating_score = wp.rating_score + win_pts
            wp.duels_won    = getattr(wp, 'duels_won', 0) + 1
            wp.save(update_fields=['rating_score', 'duels_won'])
        except StudentProfile.DoesNotExist:
            pass

        # Mag'lub
        try:
            lp = StudentProfile.objects.get(user=loser_user)
            lp.rating_score = max(0, lp.rating_score - lose_pts)
            lp.save(update_fields=['rating_score'])
        except StudentProfile.DoesNotExist:
            pass

        from django.utils import timezone as tz
        self.winner   = winner_user
        self.status   = self.Status.COMPLETED
        self.ended_at = tz.now()
        self.save(update_fields=['winner', 'status', 'ended_at'])

        # Badge tekshiruvi — duels_won shart
        try:
            from apps.gamification.services import check_and_award_badges
            check_and_award_badges(winner_user)
        except Exception:
            pass

        return win_pts, lose_pts


class Clan(models.Model):
    """Talabalar klani."""
    name         = models.CharField(max_length=100)
    tag          = models.CharField(max_length=10, unique=True, help_text='[ALC]')
    emblem       = models.CharField(max_length=10, default='🏰')
    description  = models.TextField(blank=True)
    leader       = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, related_name='led_clans'
    )
    rating_score = models.PositiveIntegerField(default=0)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating_score']

    def __str__(self):
        return f'{self.name} {self.tag}'


class ClanMembership(models.Model):
    """Klan a'zoligi."""

    class Role(models.TextChoices):
        LEADER  = 'leader',  'Lider'
        OFFICER = 'officer', 'Ofitser'
        MEMBER  = 'member',  "A'zo"

    clan      = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='memberships')
    user      = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='clan_memberships')
    role      = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('clan', 'user')

    def __str__(self):
        return f'{self.user} → {self.clan} ({self.role})'


class ClanWar(models.Model):
    """Klanlar o'rtasidagi musobaqa."""

    class Status(models.TextChoices):
        SCHEDULED   = 'scheduled',   'Rejalashtirilgan'
        IN_PROGRESS = 'in_progress', 'Davom etmoqda'
        COMPLETED   = 'completed',   'Yakunlandi'
        CANCELLED   = 'cancelled',   'Bekor qilindi'

    class WarType(models.TextChoices):
        ALGORITHMIC = 'algorithmic', 'Algoritmik'
        DEBUG       = 'debug',       'Debug'
        COMPLEX     = 'complex',     'Kompleks'

    clan1        = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='wars_as_clan1')
    clan2        = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='wars_as_clan2')
    war_type     = models.CharField(max_length=15, choices=WarType.choices, default=WarType.ALGORITHMIC)
    status       = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    winner       = models.ForeignKey(
        Clan, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='wars_won'
    )
    clan1_score  = models.PositiveSmallIntegerField(default=0)
    clan2_score  = models.PositiveSmallIntegerField(default=0)
    scheduled_at = models.DateTimeField()
    started_at   = models.DateTimeField(null=True, blank=True)
    ended_at     = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.clan1} vs {self.clan2} [{self.status}]'


class ClanChat(models.Model):
    """Klan ichki chati."""
    clan       = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='messages')
    user       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='clan_messages')
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user} → {self.clan}: {self.message[:40]}'


class Badge(models.Model):
    """Platforma nishonlari."""

    class BadgeType(models.TextChoices):
        STREAK      = 'streak',      'Streak'
        PERFORMANCE = 'performance', 'Natija'
        SOCIAL      = 'social',      'Ijtimoiy'
        ACHIEVEMENT = 'achievement', 'Yutuq'
        SPECIAL     = 'special',     'Maxsus'

    name        = models.CharField(max_length=100)
    description = models.TextField()
    icon        = models.CharField(max_length=10, default='🏅')
    badge_type  = models.CharField(max_length=15, choices=BadgeType.choices)
    condition   = models.JSONField(default=dict, help_text='{"streak_days": 7}')
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.icon} {self.name}'


class UserBadge(models.Model):
    """Foydalanuvchiga berilgan nishon."""
    user      = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='badges')
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f'{self.user} — {self.badge}'
