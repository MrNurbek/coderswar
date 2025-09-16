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
    """
    Shartlar:
    - Kimdir 3 ta topshiriqni bajarsa → duel tugaydi, o‘sha g‘olib.
    - Agar 15 daqiqa o‘tib ketgan bo‘lsa → ko‘proq bajargan g‘olib.
    - Agar ikkalasi ham 3 ta bajargan bo‘lsa → 3-topshirig‘ini oldin tugatgan g‘olib (updated_at ga qarab).
    - Durang bo‘lsa → duel tugaydi, g‘olib yo‘q.
    """
    # Opponent hali ulanmagan bo‘lsa, yakunlashga shoshilmaymiz
    if duel.opponent is None:
        return

    with transaction.atomic():
        # Duelni lock qilamiz — parallel submitlarda ikki marta tugamasin
        DuelModel = type(duel)
        duel_locked = DuelModel.objects.select_for_update().get(pk=duel.pk)

        # Allaqachon tugagan bo‘lsa — chiqamiz
        if not duel_locked.is_active:
            return

        start_time = duel_locked.started_at or duel_locked.created_at
        if not start_time:
            # Har ehtimolga qarshi: start_time bo‘lmasa ham tekshiruvni hozircha to‘xtatamiz
            return

        time_over = (timezone.now() - start_time) >= timedelta(minutes=15)

        # Hisob-kitoblar
        qs_creator = DuelAssignment.objects.filter(
            duel=duel_locked, user=duel_locked.creator, is_completed=True
        ).order_by('updated_at', 'id')  # updated_at bo‘lsa yaxshi
        qs_opponent = DuelAssignment.objects.filter(
            duel=duel_locked, user=duel_locked.opponent, is_completed=True
        ).order_by('updated_at', 'id')

        creator_completed = qs_creator.count()
        opponent_completed = qs_opponent.count()

        winner = None
        loser = None

        # 1) Kimdir 3 ta bajarib bo‘lsa, boshqasi 3 ga yetmagan bo‘lsa
        if creator_completed >= 3 and opponent_completed < 3:
            winner, loser = duel_locked.creator, duel_locked.opponent
        elif opponent_completed >= 3 and creator_completed < 3:
            winner, loser = duel_locked.opponent, duel_locked.creator

        # 2) Ikkalasi ham 3 tadan bajargan bo‘lsa — kim 3-chi topshiriqni oldin tugatgan?
        elif creator_completed >= 3 and opponent_completed >= 3:
            # 3-chi tugagan vaqtni topamiz (3-index: 0,1,2)
            def third_time(qs):
                # updated_at maydoni yo‘q bo‘lsa, created_at yoki id tartibini ishlatadi
                times = list(qs.values_list('updated_at', flat=True)[:3])
                return times[2] if len(times) >= 3 else None

            c_t3 = third_time(qs_creator)
            o_t3 = third_time(qs_opponent)

            if c_t3 and o_t3:
                if c_t3 < o_t3:
                    winner, loser = duel_locked.creator, duel_locked.opponent
                elif o_t3 < c_t3:
                    winner, loser = duel_locked.opponent, duel_locked.creator
                else:
                    # Bir xil vaqtga tushgan g‘oyat kam holat — durang
                    duel_locked.is_active = False
                    if hasattr(duel_locked, 'ended_at'):
                        duel_locked.ended_at = timezone.now()
                    duel_locked.winner = None
                    duel_locked.save()
                    return
            else:
                # Vaqtlarni aniqlay olmasak, 15 daqiqa qoidasi yoki tenglikka o‘tamiz
                if time_over:
                    if creator_completed > opponent_completed:
                        winner, loser = duel_locked.creator, duel_locked.opponent
                    elif opponent_completed > creator_completed:
                        winner, loser = duel_locked.opponent, duel_locked.creator
                    else:
                        duel_locked.is_active = False
                        if hasattr(duel_locked, 'ended_at'):
                            duel_locked.ended_at = timezone.now()
                        duel_locked.winner = None
                        duel_locked.save()
                        return
                else:
                    # Hali vaqt bor — davom etaversin
                    return

        # 3) Vaqt tugagan, lekin hech kim 3 ga yetmagan — ko‘proq bajargan yutadi
        elif time_over:
            if creator_completed > opponent_completed:
                winner, loser = duel_locked.creator, duel_locked.opponent
            elif opponent_completed > creator_completed:
                winner, loser = duel_locked.opponent, duel_locked.creator
            else:
                duel_locked.is_active = False
                if hasattr(duel_locked, 'ended_at'):
                    duel_locked.ended_at = timezone.now()
                duel_locked.winner = None
                duel_locked.save()
                return
        else:
            # Hech biri 3 ga yetmagan va vaqt ham tugamagan — davom
            return

        # ——— G‘olib/maglub aniq bo‘lsa ———
        if winner and loser:
            # Mag‘lubning jami balli (earned_points) dan 1% — xavfsiz agregat
            loser_total = AssignmentStatus.objects.filter(user=loser)\
                .aggregate(total=Sum('earned_points'))['total'] or 0
            bonus = round(loser_total * 0.01)

            # Winner.rating ni thread-safe yangilaymiz
            type(winner).objects.filter(pk=winner.pk).update(rating=F('rating') + bonus)

            duel_locked.is_active = False
            if hasattr(duel_locked, 'ended_at'):
                duel_locked.ended_at = timezone.now()
            duel_locked.winner = winner
            duel_locked.save()
# def check_duel_completion(duel):
#     # Har ikki user uchun bajarilgan topshiriqlar sonini topamiz
#     def completed_count(user):
#         return DuelAssignment.objects.filter(
#             duel=duel, user=user,
#             is_completed=True
#         ).count()
#
#     creator_completed = completed_count(duel.creator)
#     opponent_completed = completed_count(duel.opponent)
#
#     # Duel hali boshlanmagan bo‘lishi mumkin
#     if not duel.started_at:
#         return
#
#     duel_duration = timezone.now() - duel.started_at
#     time_over = duel_duration >= timedelta(minutes=15)
#
#     winner = None
#     loser = None
#
#     # 1. Kimdir 3 ta topshiriqni bajarib bo‘lsa
#     if creator_completed == 3 and opponent_completed < 3:
#         winner, loser = duel.creator, duel.opponent
#     elif opponent_completed == 3 and creator_completed < 3:
#         winner, loser = duel.opponent, duel.creator
#     # 2. 15 daqiqa o‘tib ketgan va kimdir ko‘proq topshiriq bajargan bo‘lsa
#     elif time_over:
#         if creator_completed > opponent_completed:
#             winner, loser = duel.creator, duel.opponent
#         elif opponent_completed > creator_completed:
#             winner, loser = duel.opponent, duel.creator
#         else:
#             # Durang holat
#             duel.is_active = False
#             duel.ended_at = timezone.now()
#             duel.save()
#             return
#
#     # G‘olib va mag‘lub aniqlangan bo‘lsa
#     if winner and loser:
#         # Mag‘lubning umumiy earned_points ni topamiz
#         loser_total = AssignmentStatus.objects.filter(
#             user=loser
#         ).aggregate(total=Sum('earned_points'))['total'] or 0
#
#         bonus = round(loser_total * 0.01)
#
#         # G‘olibga qo‘shamiz
#         winner.rating += bonus
#         winner.save()
#
#         # Duelni yopamiz
#         duel.is_active = False
#         duel.ended_at = timezone.now()
#         duel.winner = winner
#         duel.save()
