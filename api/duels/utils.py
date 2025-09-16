from datetime import timedelta
from django.utils import timezone

def check_duel_expired(duel):
    if duel.started_at and duel.is_active:
        now = timezone.now()
        if now > duel.started_at + timedelta(minutes=15):
            duel.is_active = False
            duel.save()


def check_duel_completion(duel):
    """
    Duel yakunlanishini tekshiradi:
    - Agar ishtirokchilardan biri 3 ta topshiriqni ham bajarsa → duel tugaydi, g‘olib aniqlanadi.
    """
    if not duel.is_active:
        return

    creator_completed = DuelAssignment.objects.filter(duel=duel, user=duel.creator, is_completed=True).count()
    opponent_completed = DuelAssignment.objects.filter(duel=duel, user=duel.opponent, is_completed=True).count()

    if creator_completed == 3:
        duel.is_active = False
        duel.winner = duel.creator
        duel.save()

    elif opponent_completed == 3:
        duel.is_active = False
        duel.winner = duel.opponent
        duel.save()