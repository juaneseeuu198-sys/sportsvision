from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userprofile_genero_userprofile_nivel'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='limitaciones',
            field=models.JSONField(blank=True, default=list, help_text='Lista de condiciones físicas o limitaciones del usuario'),
        ),
    ]
