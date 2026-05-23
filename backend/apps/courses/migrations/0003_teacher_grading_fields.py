"""
0003 — O'qituvchi baholash maydonlari

Yangiliklar:
  - TopicScore.fa_project_score  (o'qituvchi: loyiha, max 10)
  - TopicScore.re_peer_score     (o'qituvchi: peer-review, max 10)
  - TopicScore.ko_score          validator: 30 → 35
  - TopicScore.fa_score          validator: 35 → 20  (avtomatik qism)
  - TopicScore.re_score          validator: 20 → 10  (avtomatik qism)
"""

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_update_scoring_4_criteria'),
    ]

    operations = [

        # ── Yangi maydonlar ────────────────────────────────────────────────────
        migrations.AddField(
            model_name='topicscore',
            name='fa_project_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(10)],
                help_text="O'qituvchi: loyiha baholash (max 10)"
            ),
        ),
        migrations.AddField(
            model_name='topicscore',
            name='re_peer_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(10)],
                help_text="O'qituvchi: peer-review sifati (max 10)"
            ),
        ),

        # ── Validator yangilash ────────────────────────────────────────────────
        migrations.AlterField(
            model_name='topicscore',
            name='ko_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(35)],
            ),
        ),
        migrations.AlterField(
            model_name='topicscore',
            name='fa_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(20)],
                help_text='Avtomatik FA: topshiriq + kontent (max 20)',
            ),
        ),
        migrations.AlterField(
            model_name='topicscore',
            name='re_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(10)],
                help_text='Avtomatik RE: refleksiya jurnali (max 10)',
            ),
        ),
    ]
