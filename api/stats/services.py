# stats/services.py
from django.db.models import Sum, Count, Value, IntegerField
from django.db.models import Case, When
from apps.mainquest.models import UserProgress, Topic
from apps.userapp.models import User

COMPLETION_POINTS = 22
MAX_POINTS = {1: 15 * COMPLETION_POINTS, 2: 11 * COMPLETION_POINTS, 3: 19 * COMPLETION_POINTS}

def semester_case_expression():
    return Case(
        When(topic__order__gte=1,  topic__order__lte=15, then=Value(1)),
        When(topic__order__gte=16, topic__order__lte=26, then=Value(2)),
        When(topic__order__gte=27, topic__order__lte=45, then=Value(3)),
        default=Value(0),
        output_field=IntegerField(),
    )

def semester_topic_counts():
    return {
        1: Topic.objects.filter(order__gte=1, order__lte=15).count(),
        2: Topic.objects.filter(order__gte=16, order__lte=26).count(),
        3: Topic.objects.filter(order__gte=27, order__lte=45).count(),
    }

def semester_points_global():
    # Umumiy (barcha foydalanuvchilardan) semestr yig'indilari
    qs = (UserProgress.objects
          .filter(is_completed=True)
          .annotate(sem=semester_case_expression())
          .exclude(sem=0)
          .values('sem')
          .annotate(points=Sum('score'), completed=Count('id')))

    data = {
        1: {'points': 0, 'completed': 0, 'max_points': MAX_POINTS[1], 'progress_pct': 0.0},
        2: {'points': 0, 'completed': 0, 'max_points': MAX_POINTS[2], 'progress_pct': 0.0},
        3: {'points': 0, 'completed': 0, 'max_points': MAX_POINTS[3], 'progress_pct': 0.0},
    }
    for row in qs:
        s = row['sem']
        if s in data:
            pts = row['points'] or 0
            data[s]['points'] = pts
            data[s]['completed'] = row['completed'] or 0
            data[s]['progress_pct'] = round(100 * pts / data[s]['max_points'], 1)
    return data

def per_user_semester_points(filters=None):
    """
    Har bir foydalanuvchi uchun semestr bo‘yicha ballar va jami.
    filters = {'otm': 'TerDU', 'course': 1, 'group': '101', 'role': 'talaba', 'q': 'email yoki ism'}
    """
    base = (UserProgress.objects
            .filter(is_completed=True)
            .annotate(sem=semester_case_expression())
            .exclude(sem=0))

    # Foydalanuvchi bo‘yicha filtrlar (agar kerak bo‘lsa)
    if filters:
        # qidiruv (email/ism/familiya)
        q = filters.get('q')
        if q:
            base = base.filter(
                models.Q(user__email__icontains=q) |
                models.Q(user__first_name__icontains=q) |
                models.Q(user__last_name__icontains=q)
            )
        otm = filters.get('otm')
        if otm:
            base = base.filter(user__otm=otm)
        course = filters.get('course')
        if course:
            base = base.filter(user__course=course)
        group = filters.get('group')
        if group:
            base = base.filter(user__group=group)
        role = filters.get('role')
        if role:
            base = base.filter(user__role=role)

    qs = (base.values('user_id', 'user__first_name', 'user__last_name', 'user__email', 'user__rating', 'sem')
              .annotate(points=Sum('score'), completed=Count('id')))

    # Pivot: user -> sem1/sem2/sem3
    users = {}
    for row in qs:
        uid = row['user_id']
        if uid not in users:
            users[uid] = {
                'first_name': row['user__first_name'] or '',
                'last_name': row['user__last_name'] or '',
                'email': row['user__email'],
                'rating': row['user__rating'] or 0,
                'sem1_points': 0, 'sem2_points': 0, 'sem3_points': 0,
                'sem1_completed': 0, 'sem2_completed': 0, 'sem3_completed': 0,
            }
        sem = row['sem']
        pts = row['points'] or 0
        cnt = row['completed'] or 0
        if sem == 1:
            users[uid]['sem1_points'] = pts
            users[uid]['sem1_completed'] = cnt
        elif sem == 2:
            users[uid]['sem2_points'] = pts
            users[uid]['sem2_completed'] = cnt
        elif sem == 3:
            users[uid]['sem3_points'] = pts
            users[uid]['sem3_completed'] = cnt

    # Hisoblangan maydonlar
    rows = []
    for uid, u in users.items():
        total = u['sem1_points'] + u['sem2_points'] + u['sem3_points']
        rows.append({
            'name': f"{u['first_name']} {u['last_name']}".strip() or u['email'],
            'email': u['email'],
            'rating': u['rating'],
            'sem1_points': u['sem1_points'],
            'sem2_points': u['sem2_points'],
            'sem3_points': u['sem3_points'],
            'total_points': total,
            'sem1_pct': round(100 * u['sem1_points'] / MAX_POINTS[1], 1) if MAX_POINTS[1] else 0.0,
            'sem2_pct': round(100 * u['sem2_points'] / MAX_POINTS[2], 1) if MAX_POINTS[2] else 0.0,
            'sem3_pct': round(100 * u['sem3_points'] / MAX_POINTS[3], 1) if MAX_POINTS[3] else 0.0,
        })

    # Umumiy ball bo‘yicha kamayish tartibida
    rows.sort(key=lambda x: x['total_points'], reverse=True)
    return rows
