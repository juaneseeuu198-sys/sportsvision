from django.db import migrations


GRUPOS = [
    ("Pecho",         "pecho"),
    ("Espalda",       "espalda"),
    ("Hombros",       "hombros"),
    ("Bíceps",        "biceps"),
    ("Tríceps",       "triceps"),
    ("Piernas",       "piernas"),
    ("Glúteos",       "gluteos"),
    ("Abdomen",       "abdomen"),
    ("Core",          "core"),
    ("Pantorrillas",  "pantorrillas"),
    ("Antebrazos",    "antebrazos"),
    ("Cardio",        "cardio"),
    ("Movilidad",     "movilidad"),
]

EQUIPOS = [
    ("banco",           "🪑"),
    ("peso_corporal",   "🤸"),
    ("disco",           "💿"),
    ("mancuernas",      "🏋️"),
    ("barra",           "🏋️"),
    ("barra_dominadas", "🧗"),
    ("kettlebell",      "🔔"),
    ("banda",           "🟣"),
]


def seed_equipos_y_grupos(apps, schema_editor):
    GrupoMuscular = apps.get_model("exercises", "GrupoMuscular")
    Equipo        = apps.get_model("exercises", "Equipo")

    for nombre, slug in GRUPOS:
        GrupoMuscular.objects.get_or_create(slug=slug, defaults={"nombre": nombre})

    for nombre, icono in EQUIPOS:
        Equipo.objects.get_or_create(nombre=nombre, defaults={"icono": icono})


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("exercises", "0002_ejercicio_duracion_minutos"),
    ]

    operations = [
        migrations.RunPython(seed_equipos_y_grupos, noop),
    ]
