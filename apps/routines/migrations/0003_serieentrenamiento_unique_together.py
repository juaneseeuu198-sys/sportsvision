from django.db import migrations


def eliminar_series_duplicadas(apps, schema_editor):
    SerieEntrenamiento = apps.get_model('routines', 'SerieEntrenamiento')
    db = schema_editor.connection.alias

    # Buscar grupos duplicados: misma (entrenamiento, ejercicio, numero_serie)
    seen = {}
    for serie in SerieEntrenamiento.objects.using(db).order_by('entrenamiento_id', 'ejercicio_id', 'numero_serie', '-creada_en'):
        key = (serie.entrenamiento_id, serie.ejercicio_id, serie.numero_serie)
        if key in seen:
            # Eliminar el duplicado más antiguo (éste, porque ordenamos -creada_en)
            serie.delete()
        else:
            seen[key] = serie.id


class Migration(migrations.Migration):

    dependencies = [
        ('routines', '0002_plandia'),
    ]

    operations = [
        migrations.RunPython(eliminar_series_duplicadas, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name='serieentrenamiento',
            unique_together={('entrenamiento', 'ejercicio', 'numero_serie')},
        ),
    ]
