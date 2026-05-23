"""
Badge avtomatik berish servisi.
check_and_award_badges(user) — badge shartlarini tekshirib, yangilarini beradi.
"""


def check_and_award_badges(user):
    """
    Foydalanuvchining barcha badge shartlarini tekshiradi va
    yangi badge'larni beradi. Qaytaradi: yangi berilgan UserBadge list.
    """
    from .models import Badge, UserBadge

    badges  = Badge.objects.filter(is_active=True)
    already = set(UserBadge.objects.filter(user=user).values_list('badge_id', flat=True))
    awarded = []

    for badge in badges:
        if badge.id in already:
            continue
        if _check_condition(user, badge.condition):
            ub = UserBadge.objects.create(user=user, badge=badge)
            awarded.append(ub)
            _notify_badge(user, badge)

    return awarded


def _check_condition(user, condition: dict) -> bool:
    """Badge shartini tekshiradi. True → foydalanuvchi shartni bajardi."""
    if not condition:
        return False

    from apps.users.models import StudentProfile
    from apps.courses.models import TopicScore, Submission
    from apps.social.models import PeerReview
    from .models import Duel

    # ── Student profil ──
    try:
        profile = StudentProfile.objects.get(user=user)
    except StudentProfile.DoesNotExist:
        profile = None

    # topics_completed: N → N ta mavzuni tugatgan
    if 'topics_completed' in condition:
        count = TopicScore.objects.filter(student=user, is_completed=True).count()
        if count < condition['topics_completed']:
            return False

    # streak_days: N → ketma-ket N kun faol
    if 'streak_days' in condition:
        if not profile or profile.current_streak < condition['streak_days']:
            return False

    # submissions: N → N ta muvaffaqiyatli submission
    if 'submissions' in condition:
        count = Submission.objects.filter(student=user, status='passed').count()
        if count < condition['submissions']:
            return False

    # duels_won: N → N ta duelda g'alaba
    if 'duels_won' in condition:
        count = Duel.objects.filter(winner=user).count()
        if count < condition['duels_won']:
            return False

    # peer_reviews: N → N ta peer review bergan
    if 'peer_reviews' in condition:
        count = PeerReview.objects.filter(reviewer=user).count()
        if count < condition['peer_reviews']:
            return False

    # module_completed: N → N-chi modul to'liq tugatilgan
    if 'module_completed' in condition:
        from apps.courses.models import Module, Topic
        module_num = condition['module_completed']
        try:
            module       = Module.objects.get(number=module_num)
            topic_count  = Topic.objects.filter(module=module, is_active=True).count()
            completed    = TopicScore.objects.filter(
                student=user, topic__module=module, is_completed=True
            ).count()
            if topic_count == 0 or completed < topic_count:
                return False
        except Module.DoesNotExist:
            return False

    # level: "titan" → profil darajasi
    if 'level' in condition:
        if not profile or profile.level != condition['level']:
            return False

    # perfect_score: 1 → biror mavzudan 100/100
    if 'perfect_score' in condition:
        if not TopicScore.objects.filter(student=user, total_score=100).exists():
            return False

    # runtime_ms_max: N → N ms dan tez muvaffaqiyatli submission
    if 'runtime_ms_max' in condition:
        if not Submission.objects.filter(
            student=user, status='passed',
            runtime_ms__lte=condition['runtime_ms_max'],
        ).exists():
            return False

    # login_first: true → tizimda ro'yxatdan o'tgan bo'lsa yetarli
    if condition.get('login_first'):
        pass  # user mavjud bo'lgani uchun har doim True

    # clan_wars: N — ClanWar implement qilingandan keyin
    if 'clan_wars' in condition:
        from .models import ClanWar
        from .models import ClanMembership
        try:
            membership = ClanMembership.objects.filter(user=user).first()
            if not membership:
                return False
            clan = membership.clan
            count = ClanWar.objects.filter(
                status='completed'
            ).filter(
                __import__('django.db.models', fromlist=['Q']).Q(clan1=clan) |
                __import__('django.db.models', fromlist=['Q']).Q(clan2=clan)
            ).count()
            if count < condition['clan_wars']:
                return False
        except Exception:
            return False

    # clan_war_mvp: 1 — MVP tizimi implement bo'lsa
    if 'clan_war_mvp' in condition:
        return False  # Hozircha MVP tizimi yo'q

    return True


def _notify_badge(user, badge):
    """Badge olganlik haqida bildiruv yaratish."""
    try:
        from apps.social.models import Notification
        Notification.objects.create(
            user=user,
            title=f'{badge.icon} Yangi nishon qo\'lga kiritildi!',
            message=f'"{badge.name}" nishoniga ega bo\'ldingiz! {badge.description}',
            notif_type='badge',
            link='/profile.html',
        )
    except Exception:
        pass


# ── Qanday chaqiriladi ────────────────────────────────────────────────────────
#
#  Streak yangilanganida (LogActivityView._update_streak):
#    check_and_award_badges(user)
#
#  TopicScore saqlanganda (TopicScore.save → recalculate):
#    check_and_award_badges(user)
#
#  Submission passed bo'lganda (tasks.py submit_to_judge0):
#    check_and_award_badges(user)
#
#  Duel tugaganda (Duel.finish):
#    check_and_award_badges(winner_user)
#
#  Peer review yaratilganda (PeerReviewCreateView.perform_create):
#    check_and_award_badges(reviewer)
#
#  Birinchi login (RegisterView):
#    check_and_award_badges(user)
