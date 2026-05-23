"""
Celery konfiguratsiyasi — Coders War platformasi.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('coderswar')

# Django settings'dan Celery konfiguratsiyasini o'qish
app.config_from_object('django.conf:settings', namespace='CELERY')

# Barcha app'lardan tasks.py fayllarini avtomatik topish
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
