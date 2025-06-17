from datetime import timedelta
from django.utils import timezone

def check_duel_expired(duel):
    if duel.started_at and duel.is_active:
        now = timezone.now()
        if now > duel.started_at + timedelta(minutes=15):
            duel.is_active = False
            duel.save()
