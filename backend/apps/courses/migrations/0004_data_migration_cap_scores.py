"""
0004 — Eski ball'larni yangi chegaraga moslash (data migration)

0002 migratsiyasida:
  fa_score  max = 35  (eski tizim)
  re_score  max = 20  (eski tizim)

0003 migratsiyasida:
  fa_score  max = 20  (yangi, avtomatik qism)
  re_score  max = 10  (yangi, avtomatik qism)

Agar DB'da eski qiymatlar mavjud bo'lsa, yangi maksimumdan oshib ketadi.
Bu RunPython orqali ularni cheklaydi.
"""

from django.db import migrations


def cap_existing_scores(apps, schema_editor):
    from django.db.models import F

    TopicScore = apps.get_model('courses', 'TopicScore')

    # fa_score: eski max 35 → yangi max 20
    updated_fa = TopicScore.objects.filter(fa_score__gt=20).update(fa_score=20)

    # re_score: eski max 20 → yangi max 10
    updated_re = TopicScore.objects.filter(re_score__gt=10).update(re_score=10)

    # total_score ni qayta hisoblash — cap'dan keyin yangi qiymat bilan sinxronlashtirish
    # (fa_project_score + re_peer_score 0003 migratsiyasida qo'shilgan, shuning uchun mavjud)
    TopicScore.objects.update(
        total_score=(
            F('mo_score') + F('ko_score')
            + F('fa_score') + F('fa_project_score')
            + F('re_score') + F('re_peer_score')
        )
    )

    if updated_fa or updated_re:
        print(
            f'\n  ✓ Cap: fa_score capped for {updated_fa} records, '
            f're_score capped for {updated_re} records. '
            f'total_score recalculated for all.'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_teacher_grading_fields'),
    ]

    operations = [
        migrations.RunPython(cap_existing_scores, migrations.RunPython.noop),
    ]
