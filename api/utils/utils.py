from django.utils import timezone
from datetime import timedelta
from apps.duels.models import DuelAssignment
from apps.mainquest.models import AssignmentStatus
from django.db.models import Sum


def check_duel_end(duel):
    def get_completed_count(user):
        assignments = duel.duel_assignments.filter(user=user).values_list('assignment_id', flat=True)
        return AssignmentStatus.objects.filter(user=user, assignment_id__in=assignments, is_completed=True).count()

    c_done = get_completed_count(duel.creator)
    o_done = get_completed_count(duel.opponent)

    now = timezone.now()
    time_passed = (now - duel.started_at).total_seconds() if duel.started_at else 0

    if c_done == 3 and o_done < 3:
        declare_winner(duel, duel.creator, duel.opponent)
    elif o_done == 3 and c_done < 3:
        declare_winner(duel, duel.opponent, duel.creator)
    elif time_passed >= 900:
        if c_done > o_done:
            declare_winner(duel, duel.creator, duel.opponent)
        elif o_done > c_done:
            declare_winner(duel, duel.opponent, duel.creator)
        else:
            duel.is_active = False
            duel.save()


def declare_winner(duel, winner, loser):
    duel.winner = winner
    duel.is_active = False
    duel.save()

    if loser:
        rating_taken = int(loser.rating * 0.01)
        winner.rating += rating_taken
        winner.save()
        loser.rating -= rating_taken
        loser.save()


def check_duel_completion(duel):
    # Har ikki user uchun bajarilgan topshiriqlar sonini topamiz
    def completed_count(user):
        return DuelAssignment.objects.filter(
            duel=duel, user=user,
            is_completed=True
        ).count()

    creator_completed = completed_count(duel.creator)
    opponent_completed = completed_count(duel.opponent)

    # Duel hali boshlanmagan bo‘lishi mumkin
    if not duel.started_at:
        return

    duel_duration = timezone.now() - duel.started_at
    time_over = duel_duration >= timedelta(minutes=15)

    winner = None
    loser = None

    # 1. Kimdir 3 ta topshiriqni bajarib bo‘lsa
    if creator_completed == 3 and opponent_completed < 3:
        winner, loser = duel.creator, duel.opponent
    elif opponent_completed == 3 and creator_completed < 3:
        winner, loser = duel.opponent, duel.creator
    # 2. 15 daqiqa o‘tib ketgan va kimdir ko‘proq topshiriq bajargan bo‘lsa
    elif time_over:
        if creator_completed > opponent_completed:
            winner, loser = duel.creator, duel.opponent
        elif opponent_completed > creator_completed:
            winner, loser = duel.opponent, duel.creator
        else:
            # Durang holat
            duel.is_active = False
            duel.ended_at = timezone.now()
            duel.save()
            return

    # G‘olib va mag‘lub aniqlangan bo‘lsa
    if winner and loser:
        # Mag‘lubning umumiy earned_points ni topamiz
        loser_total = AssignmentStatus.objects.filter(
            user=loser
        ).aggregate(total=Sum('earned_points'))['total'] or 0

        bonus = round(loser_total * 0.01)

        # G‘olibga qo‘shamiz
        winner.rating += bonus
        winner.save()

        # Duelni yopamiz
        duel.is_active = False
        duel.ended_at = timezone.now()
        duel.winner = winner
        duel.save()
