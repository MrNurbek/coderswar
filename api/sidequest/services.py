# apps/gear/services.py
from collections import defaultdict
from apps.sidequest.models import GearItem, UserGear
from django.db import transaction



QUALITY_ORDER = {"basic": 1, "medium": 2, "rare": 3}

@transaction.atomic
def equip_best_gears_for_user(user):
    """
    Har bir gear type bo‘yicha eng kuchli (quality -> obtained_at tiebreaker) ni tanlaydi,
    tanlanganlarini is_equipped=True, qolganlarini is_equipped=False qiladi.
    """
    user_gears = (
        UserGear.objects
        .select_related("gear")
        .filter(user=user)
        .order_by("gear__type", "-obtained_at")  # tiebreaker uchun foydali
    )
    if not user_gears.exists():
        return []

    best_by_type = {}  # type -> UserGear
    for ug in user_gears:
        g = ug.gear
        t = g.type
        prev = best_by_type.get(t)
        if prev is None:
            best_by_type[t] = ug
            continue

        # quality bo‘yicha solishtirish
        cur_q = QUALITY_ORDER.get(g.quality, 0)
        prev_q = QUALITY_ORDER.get(prev.gear.quality, 0)
        if (cur_q > prev_q) or (cur_q == prev_q and ug.obtained_at > prev.obtained_at):
            best_by_type[t] = ug

    to_equip_ids = {ug.id for ug in best_by_type.values()}

    # Avval hammasini yechamiz
    UserGear.objects.filter(user=user, is_equipped=True).exclude(id__in=to_equip_ids).update(is_equipped=False)
    # Keyin eng yaxshilarni kiydiramiz
    UserGear.objects.filter(user=user).filter(id__in=to_equip_ids).exclude(is_equipped=True).update(is_equipped=True)

    # Qaytarish uchun tanlanganlar ro‘yxati
    return list(best_by_type.values())
