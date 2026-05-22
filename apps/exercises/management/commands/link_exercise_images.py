from __future__ import annotations

import unicodedata
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.exercises.models import Ejercicio

GRUPO_FOLDER = {
    'abdomen':     'abdomen',
    'antebrazos':  'antebrazo',
    'biceps':      'biseps',
    'cardio':      'cardio',
    'core':        'core',
    'espalda':     'Espalda',
    'gluteos':     'gluteos',
    'hombros':     'hombros',
    'movilidad':   'movilidad',
    'pantorrillas':'pantorrilas',
    'pecho':       'pecho',
    'piernas':     'piernas',
    'triceps':     'triceps',
}


def _slug(name: str) -> str:
    sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    return ''.join(
        c if c.isalnum() else '_'
        for c in sin_tildes.lower().replace(' ', '_').replace('-', '_')
        if c.isalnum() or c == '_'
    ).strip('_')


class Command(BaseCommand):
    help = 'Asigna imagen_static/gif_static a cada ejercicio usando rutas de /static/images/.'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true',
                            help='Sobreescribe rutas ya asignadas.')

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        static_base: Path = settings.BASE_DIR / 'static' / 'images'

        updated = skipped = not_found = 0

        for ej in Ejercicio.objects.select_related('grupo_muscular').all():
            if not ej.grupo_muscular:
                not_found += 1
                continue

            folder = GRUPO_FOLDER.get(ej.grupo_muscular.slug)
            if not folder:
                not_found += 1
                continue

            slug = _slug(ej.nombre)
            img_src = static_base / folder / f'{slug}.jpg'
            gif_src = static_base / folder / 'gif' / f'{slug}.gif'

            changed = False

            if img_src.exists() and (overwrite or not ej.imagen_static):
                ej.imagen_static = f'images/{folder}/{slug}.jpg'
                changed = True

            if gif_src.exists() and (overwrite or not ej.gif_static):
                ej.gif_static = f'images/{folder}/gif/{slug}.gif'
                changed = True

            if changed:
                ej.save(update_fields=['imagen_static', 'gif_static'])
                updated += 1
            elif not img_src.exists() and not gif_src.exists():
                not_found += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Listo. Actualizados: {updated} | Ya tenian imagen: {skipped} | Sin archivo: {not_found}'
        ))
