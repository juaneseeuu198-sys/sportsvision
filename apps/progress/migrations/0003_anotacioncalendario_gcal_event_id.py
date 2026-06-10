from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0002_medicioncorporal_anotacioncalendario'),
    ]

    operations = [
        migrations.AddField(
            model_name='anotacioncalendario',
            name='gcal_event_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='ID del evento en Google Calendar',
                max_length=200,
            ),
        ),
    ]
