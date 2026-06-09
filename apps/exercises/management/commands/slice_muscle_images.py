"""
Corta muscle_grid.jpg en imágenes individuales por grupo muscular.

Uso:
    python manage.py slice_muscle_images

Requiere que static/img/muscle_grid.jpg exista previamente.
La cuadrícula es 10 columnas × 3 filas = 30 celdas.
"""

from django.core.management.base import BaseCommand
from pathlib import Path
from PIL import Image

# Mapeo: slug -> (columna, fila) en la cuadrícula 10×3 (base 0)
GRID_MAPPING = {
    'pecho':        (0, 0),
    'hombros':      (2, 0),
    'biceps':       (4, 0),
    'triceps':      (5, 0),
    'antebrazos':   (6, 0),
    'abdomen':      (2, 1),
    'espalda':      (8, 2),
    'gluteos':      (8, 1),
    'piernas':      (2, 2),
    'pantorrillas': (6, 2),
    'core':         (4, 1),
    'cardio':       (9, 2),
    'movilidad':    (1, 1),
}

COLS = 10
ROWS = 3


class Command(BaseCommand):
    help = 'Corta muscle_grid.jpg en imágenes individuales por músculo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--grid', default='static/img/muscle_grid.jpg',
            help='Ruta a la imagen de cuadrícula'
        )
        parser.add_argument(
            '--out', default='static/img/muscles',
            help='Carpeta de salida'
        )
        parser.add_argument(
            '--cols', type=int, default=COLS,
            help='Número de columnas en la cuadrícula'
        )
        parser.add_argument(
            '--rows', type=int, default=ROWS,
            help='Número de filas en la cuadrícula'
        )

    def handle(self, *args, **options):
        grid_path = Path(options['grid'])
        out_dir = Path(options['out'])

        if not grid_path.exists():
            self.stderr.write(self.style.ERROR(
                f'No se encontró {grid_path}\n'
                'Guarda la imagen de referencia en esa ruta e intenta de nuevo.'
            ))
            return

        out_dir.mkdir(parents=True, exist_ok=True)

        img = Image.open(grid_path).convert('RGBA')
        W, H = img.size
        cols = options['cols']
        rows = options['rows']
        cw = W // cols   # ancho de celda
        ch = H // rows   # alto de celda

        self.stdout.write(
            f'Imagen: {W}×{H}px → celda: {cw}×{ch}px ({cols} cols, {rows} filas)'
        )

        saved = 0
        for slug, (col, row) in GRID_MAPPING.items():
            x0 = col * cw
            y0 = row * ch
            x1 = x0 + cw
            y1 = y0 + ch
            cell = img.crop((x0, y0, x1, y1))

            # Fondo negro para que el blanco del body_map destaque
            bg = Image.new('RGBA', cell.size, (18, 18, 46, 255))
            bg.paste(cell, mask=cell if cell.mode == 'RGBA' else None)

            out_path = out_dir / f'{slug}.png'
            bg.convert('RGB').save(out_path, 'PNG', optimize=True)
            saved += 1
            self.stdout.write(f'  ✓ {slug} → col={col}, row={row} → {out_path}')

        self.stdout.write(self.style.SUCCESS(
            f'\n{saved} imágenes guardadas en {out_dir}/'
        ))
        self.stdout.write(
            '\nSi algún músculo muestra el área equivocada, ajusta '
            'GRID_MAPPING en este archivo y vuelve a ejecutar el comando.'
        )
