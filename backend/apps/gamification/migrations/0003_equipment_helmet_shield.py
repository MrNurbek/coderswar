from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamification', '0002_equipment_image_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='eq_type',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('weapon', 'Qurol'),
                    ('armor',  'Zirh'),
                    ('ring',   'Uzuk'),
                    ('boots',  'Etik'),
                    ('helmet', "Dubulg'a"),
                    ('shield', 'Qalqon'),
                ],
            ),
        ),
    ]
