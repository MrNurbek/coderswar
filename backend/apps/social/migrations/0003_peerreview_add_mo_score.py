from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_update_peerreview_4_criteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='peerreview',
            name='mo_score',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Motivatsion (0–15)',
                validators=[django.core.validators.MaxValueValidator(15)],
            ),
        ),
    ]
