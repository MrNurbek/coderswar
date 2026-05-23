from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        # TopicScore: ad_score va kr_score o'chirish
        migrations.RemoveField(model_name='topicscore', name='ad_score'),
        migrations.RemoveField(model_name='topicscore', name='kr_score'),

        # TopicScore: validator yangilash
        migrations.AlterField(
            model_name='topicscore',
            name='mo_score',
            field=models.PositiveSmallIntegerField(
                default=0, validators=[django.core.validators.MaxValueValidator(15)]
            ),
        ),
        migrations.AlterField(
            model_name='topicscore',
            name='ko_score',
            field=models.PositiveSmallIntegerField(
                default=0, validators=[django.core.validators.MaxValueValidator(30)]
            ),
        ),
        migrations.AlterField(
            model_name='topicscore',
            name='fa_score',
            field=models.PositiveSmallIntegerField(
                default=0, validators=[django.core.validators.MaxValueValidator(35)]
            ),
        ),
        migrations.AlterField(
            model_name='topicscore',
            name='re_score',
            field=models.PositiveSmallIntegerField(
                default=0, validators=[django.core.validators.MaxValueValidator(20)]
            ),
        ),
    ]
