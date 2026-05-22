from __future__ import annotations

import shutil
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
    help = 'Copia imágenes de static/images/ a media/ y las asigna a cada ejercicio.'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true',
                            help='Sobreescribe imágenes ya asignadas.')

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        static_base: Path = settings.BASE_DIR / 'static' / 'images'
        media_img: Path = settings.MEDIA_ROOT / 'ejercicios'
        media_gif: Path = settings.MEDIA_ROOT / 'ejercicios' / 'gifs'
        media_img.mkdir(parents=True, exist_ok=True)
        media_gif.mkdir(parents=True, exist_ok=True)

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

            if img_src.exists() and (overwrite or not ej.imagen):
                dest = media_img / f'{slug}.jpg'
                shutil.copy2(img_src, dest)
                ej.imagen = f'ejercicios/{slug}.jpg'
                changed = True

            if gif_src.exists() and (overwrite or not ej.gif):
                dest = media_gif / f'{slug}.gif'
                shutil.copy2(gif_src, dest)
                ej.gif = f'ejercicios/gifs/{slug}.gif'
                changed = True

            if changed:
                ej.save(update_fields=['imagen', 'gif'])
                updated += 1
                self.stdout.write(f'  OK {ej.nombre}')
            elif not img_src.exists() and not gif_src.exists():
                not_found += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nListo. Actualizados: {updated} | Ya tenían imagen: {skipped} | Sin archivo: {not_found}'
        ))
