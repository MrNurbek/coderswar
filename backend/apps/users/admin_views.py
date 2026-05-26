import time
from django.contrib.auth import get_user_model
from django.db import connection
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()

_ADMIN_ROLES = ('admin', 'superadmin')


def _require_admin(request):
    """Returns 403 Response if not admin, else None."""
    role = getattr(request.user, 'role', None)
    if role not in _ADMIN_ROLES:
        return Response({'detail': "Ruxsat yo'q."}, status=403)
    return None


def _get_psutil_stats():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            'cpu': round(cpu, 1),
            'ram': {
                'percent': round(mem.percent, 1),
                'used_gb': round(mem.used / 1024**3, 2),
                'total_gb': round(mem.total / 1024**3, 2),
            },
            'disk': {
                'percent': round(disk.percent, 1),
                'used_gb': round(disk.used / 1024**3, 1),
                'total_gb': round(disk.total / 1024**3, 1),
            },
        }
    except Exception:
        return {'cpu': None, 'ram': None, 'disk': None}


def _check_db():
    try:
        t0 = time.monotonic()
        with connection.cursor() as cur:
            cur.execute('SELECT 1')
        return {'status': 'ok', 'latency_ms': round((time.monotonic() - t0) * 1000, 1)}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def _check_redis():
    try:
        import redis as redis_lib
        redis_url = settings.CHANNEL_LAYERS.get('default', {}).get('CONFIG', {}).get(
            'hosts', [None]
        )[0]
        if redis_url is None:
            redis_url = 'redis://localhost:6379/0'
        t0 = time.monotonic()
        r = redis_lib.from_url(redis_url if isinstance(redis_url, str) else 'redis://localhost:6379/0')
        r.ping()
        info = r.info('memory')
        latency = round((time.monotonic() - t0) * 1000, 1)
        return {
            'status': 'ok',
            'latency_ms': latency,
            'used_memory': info.get('used_memory_human', '?'),
            'used_memory_bytes': info.get('used_memory', 0),
            'maxmemory_bytes': info.get('maxmemory', 0),
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def _check_judge0():
    try:
        import requests as req
        judge0_url = getattr(settings, 'JUDGE0_URL', None)
        if not judge0_url:
            return {'status': 'unknown'}
        t0 = time.monotonic()
        r = req.get(judge0_url.rstrip('/') + '/system_info', timeout=3)
        latency = round((time.monotonic() - t0) * 1000, 1)
        if r.status_code == 200:
            return {'status': 'ok', 'latency_ms': latency}
        return {'status': 'warn', 'code': r.status_code}
    except Exception:
        return {'status': 'error'}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def server_status_view(request):
    err = _require_admin(request)
    if err:
        return err
    resources = _get_psutil_stats()
    db = _check_db()
    redis = _check_redis()
    judge0 = _check_judge0()

    redis_pct = None
    if redis.get('status') == 'ok' and redis.get('maxmemory_bytes') and redis.get('used_memory_bytes'):
        redis_pct = round(redis['used_memory_bytes'] / redis['maxmemory_bytes'] * 100, 1)

    return Response({
        'resources': resources,
        'services': {
            'database': db,
            'redis': {**redis, 'memory_percent': redis_pct},
            'judge0': judge0,
            'api': {'status': 'ok'},
        },
        'platform': {
            'python_version': _safe_import_version('sys', lambda m: m.version.split()[0]),
            'django_version': _safe_import_version('django', lambda m: m.__version__),
            'drf_version': _safe_import_version('rest_framework', lambda m: m.VERSION_STRING),
        }
    })


def _safe_import_version(module, getter):
    try:
        import importlib
        m = importlib.import_module(module)
        return getter(m)
    except Exception:
        return '?'


# ── System logs endpoint ──────────────────────────────────────────────────────

LEVEL_MAP = {'INFO': 'info', 'WARN': 'warn', 'ERROR': 'error', 'SUCCESS': 'success'}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_logs_view(request):
    err = _require_admin(request)
    if err:
        return err
    level_filter = request.GET.get('level', '').upper()
    page = max(1, int(request.GET.get('page', 1)))
    page_size = 20

    logs = []

    # 1. Recent submissions
    try:
        from apps.courses.models import Submission
        subs = (
            Submission.objects
            .select_related('user')
            .order_by('-submitted_at')[:30]
        )
        for s in subs:
            ok = s.status == 'accepted'
            fail = s.status in ['wrong_answer', 'error', 'time_limit_exceeded', 'compilation_error']
            level = 'success' if ok else ('error' if fail else 'info')
            name = ''
            if s.user:
                name = s.user.get_full_name() or s.user.username
            logs.append({
                'level': level,
                'type': 'submission',
                'icon': 'li-submit',
                'emoji': '💻',
                'message': (
                    f'Submission #{s.id} — <strong>{name or "Noma\'lum"}</strong> '
                    f'{"✅ qabul qilindi" if ok else "❌ rad etildi" if fail else "⏳ tekshirilmoqda"}'
                ),
                'time': s.submitted_at.isoformat() if s.submitted_at else None,
            })
    except Exception:
        pass

    # 2. Recent user registrations
    try:
        new_users = User.objects.order_by('-date_joined')[:15]
        for u in new_users:
            role_label = {'student': 'Talaba', 'teacher': "O'qituvchi", 'admin': 'Admin'}.get(u.role, u.role)
            logs.append({
                'level': 'info',
                'type': 'register',
                'icon': 'li-register',
                'emoji': '👤',
                'message': f'Yangi ro\'yxat: <strong>{u.get_full_name() or u.username}</strong> ({role_label})',
                'time': u.date_joined.isoformat(),
            })
    except Exception:
        pass

    # 3. Recent notifications as system events
    try:
        from apps.social.models import Notification
        notifs = Notification.objects.order_by('-created_at')[:20]
        type_conf = {
            'badge':       ('success', 'li-badge',    '🏅'),
            'duel':        ('info',    'li-system',   '⚔️'),
            'clan':        ('info',    'li-system',   '🏰'),
            'peer_review': ('info',    'li-submit',   '📝'),
            'system':      ('warn',    'li-system',   '⚙️'),
            'topic':       ('success', 'li-submit',   '📚'),
            'teacher':     ('info',    'li-register', '👨‍🏫'),
        }
        for n in notifs:
            lv, icon, emoji = type_conf.get(n.notif_type, ('info', 'li-system', '🔔'))
            logs.append({
                'level': lv,
                'type': 'notification',
                'icon': icon,
                'emoji': emoji,
                'message': n.message or 'Tizim bildirishnomasi',
                'time': n.created_at.isoformat() if n.created_at else None,
            })
    except Exception:
        pass

    # Sort by time descending
    logs.sort(key=lambda x: x.get('time') or '', reverse=True)

    # Stats before filtering
    stats = {
        'info':    sum(1 for l in logs if l['level'] == 'info'),
        'warn':    sum(1 for l in logs if l['level'] == 'warn'),
        'error':   sum(1 for l in logs if l['level'] == 'error'),
        'success': sum(1 for l in logs if l['level'] == 'success'),
    }

    # Level filter
    if level_filter in LEVEL_MAP:
        target = LEVEL_MAP[level_filter]
        logs = [l for l in logs if l['level'] == target]

    total = len(logs)
    start = (page - 1) * page_size

    return Response({
        'count': total,
        'stats': stats,
        'results': logs[start:start + page_size],
    })
