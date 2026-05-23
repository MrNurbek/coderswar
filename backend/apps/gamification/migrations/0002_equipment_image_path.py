from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='image_path',
            field=models.CharField(
                blank=True,
                max_length=200,
                help_text='Frontend static rasmi: /static/frontend/img/equipment/...'
            ),
        ),
    ]
