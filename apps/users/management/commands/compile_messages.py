from django.core.management.base import BaseCommand
from pathlib import Path


class Command(BaseCommand):
    help = "Compile .po translation files to .mo using polib (no msgfmt needed)"

    def handle(self, *args, **kwargs):
        try:
            import polib
        except ImportError:
            self.stdout.write(self.style.WARNING("polib not installed, skipping .mo compilation"))
            return

        locale_dir = Path(__file__).resolve().parents[5] / 'locale'
        compiled = 0
        for po_path in locale_dir.glob('*/LC_MESSAGES/django.po'):
            mo_path = po_path.with_suffix('.mo')
            try:
                po = polib.pofile(str(po_path))
                po.save_as_mofile(str(mo_path))
                compiled += 1
                self.stdout.write(f"  Compiled {po_path.parts[-3]}: {len(po)} strings")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error compiling {po_path}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Compiled {compiled} translation files"))
