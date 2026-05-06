"""
Punto de entrada para el ejecutable único de SportsVision.
La base de datos se guarda en AppData del usuario para que persista entre ejecuciones.
"""
import os
import sys
import threading
import webbrowser
import time
import shutil


def meipass():
    """Carpeta donde PyInstaller extrae los archivos internos del .exe."""
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def user_data_dir():
    r"""Carpeta de datos del usuario: %APPDATA%\SportsVision en Windows."""
    appdata = os.environ.get('APPDATA') or os.path.expanduser('~')
    path = os.path.join(appdata, 'SportsVision')
    os.makedirs(path, exist_ok=True)
    return path


def setup_database():
    """
    La BD necesita estar fuera del .exe para ser escribible.
    Si no existe en AppData, copia la inicial que viene dentro del exe.
    """
    data_dir  = user_data_dir()
    db_dest   = os.path.join(data_dir, 'db.sqlite3')
    db_origen = os.path.join(meipass(), 'db.sqlite3')

    if not os.path.exists(db_dest) and os.path.exists(db_origen):
        shutil.copy2(db_origen, db_dest)

    return db_dest


def main():
    internal = meipass()
    os.chdir(internal)

    db_path = setup_database()

    # Apuntar la BD a AppData del usuario
    os.environ['SPORTSVISION_DB'] = db_path
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsvision.settings')

    import django
    django.setup()

    from django.core.management import call_command

    print("Iniciando SportsVision...")
    call_command('migrate', verbosity=0, interactive=False)

    def abrir_navegador():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:8000')

    threading.Thread(target=abrir_navegador, daemon=True).start()

    print("Servidor en http://127.0.0.1:8000  —  cierra esta ventana para apagar.")
    call_command('runserver', '127.0.0.1:8000', '--noreload')


if __name__ == '__main__':
    main()
