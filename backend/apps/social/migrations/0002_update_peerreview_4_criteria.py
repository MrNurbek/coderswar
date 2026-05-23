from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0001_initial'),
    ]

    operations = [
        # PeerReview: ad_score va kr_score o'chirish
        migrations.RemoveField(model_name='peerreview', name='ad_score'),
        migrations.RemoveField(model_name='peerreview', name='kr_score'),

        # PeerReview: validator yangilash
        migrations.AlterField(
            model_name='peerreview',
            name='ko_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(30)],
                help_text='Kognitiv (0–30)',
            ),
        ),
        migrations.AlterField(
            model_name='peerreview',
            name='fa_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(35)],
                help_text='Faoliyatli (0–35)',
            ),
        ),
        migrations.AlterField(
            model_name='peerreview',
            name='re_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                validators=[django.core.validators.MaxValueValidator(20)],
                help_text='Refleksiv-baholovchi (0–20)',
            ),
        ),
    ]
