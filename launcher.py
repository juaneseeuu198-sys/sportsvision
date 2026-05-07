"""
Punto de entrada para SportsVision (.exe Windows / binario Linux).
Conecta a la base de datos central de Railway y carga credenciales desde .env.
"""
import os
import sys
import threading
import webbrowser
import time
import shutil


def exe_dir():
    """Carpeta donde vive el ejecutable (o el script en desarrollo)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def meipass():
    """Carpeta donde PyInstaller extrae archivos internos del .exe."""
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def user_data_dir():
    r"""Datos del usuario: %APPDATA%\SportsVision en Windows, ~/.SportsVision en Linux."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    else:
        base = os.path.expanduser('~')
    path = os.path.join(base, 'SportsVision')
    os.makedirs(path, exist_ok=True)
    return path


def _leer_env_file(path):
    """Carga variables de un archivo .env sin necesitar python-dotenv."""
    try:
        from dotenv import load_dotenv
        load_dotenv(path, override=False)
        return
    except ImportError:
        pass
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k, v = k.strip(), v.strip()
                if k and k not in os.environ:
                    os.environ[k] = v


def cargar_env():
    """
    Carga variables de entorno en orden de prioridad:
    1. Variables ya definidas en el sistema (máxima prioridad, no se sobreescriben)
    2. .env externo al lado del ejecutable
    3. .env interno (bakeado dentro del .exe)
    """
    # .env externo (al lado del .exe)
    ext = os.path.join(exe_dir(), '.env')
    if os.path.exists(ext):
        _leer_env_file(ext)
        print(f"[CONFIG] .env externo cargado: {ext}")

    # .env interno (bundleado en el .exe por PyInstaller)
    interno = os.path.join(meipass(), '.env')
    if os.path.exists(interno) and interno != ext:
        _leer_env_file(interno)
        print(f"[CONFIG] .env interno cargado")


def setup_database():
    """
    Prioridad de conexión:
    1. DATABASE_URL ya en el entorno (de cargar_env o del sistema)
    2. db_config.txt externo (al lado del .exe)
    3. db_config.txt interno (bakeado en el .exe)
    4. SQLite local en AppData
    """
    # 1. Ya definida
    if os.environ.get('DATABASE_URL'):
        print("[DB] PostgreSQL Railway (variable de entorno)")
        return None

    # 2. db_config.txt externo
    ext = os.path.join(exe_dir(), 'db_config.txt')
    if os.path.exists(ext):
        db_url = open(ext, 'r', encoding='utf-8').read().strip()
        if db_url:
            os.environ['DATABASE_URL'] = db_url
            print("[DB] PostgreSQL Railway (db_config.txt externo)")
            return None

    # 3. db_config.txt interno
    interno = os.path.join(meipass(), 'db_config.txt')
    if os.path.exists(interno):
        db_url = open(interno, 'r', encoding='utf-8').read().strip()
        if db_url:
            os.environ['DATABASE_URL'] = db_url
            print("[DB] PostgreSQL Railway (db_config.txt interno)")
            return None

    # 4. SQLite local
    data_dir  = user_data_dir()
    db_dest   = os.path.join(data_dir, 'db.sqlite3')
    db_origen = os.path.join(meipass(), 'db.sqlite3')
    if not os.path.exists(db_dest) and os.path.exists(db_origen):
        shutil.copy2(db_origen, db_dest)
    print(f"[DB] SQLite local: {db_dest}")
    return db_dest


def main():
    # 1. Cargar credenciales (.env)
    cargar_env()

    internal = meipass()
    os.chdir(internal)

    # 2. Configurar base de datos
    db_path = setup_database()
    if db_path:
        os.environ['SPORTSVISION_DB'] = db_path

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsvision.settings')

    # 3. Iniciar Django
    import django
    django.setup()

    from django.core.management import call_command
    print("Aplicando migraciones...")
    call_command('migrate', verbosity=0, interactive=False)

    print("\n" + "="*52)
    print("  SportsVision")
    db_tipo = "PostgreSQL Railway" if os.environ.get('DATABASE_URL') else "SQLite local"
    print(f"  Base de datos: {db_tipo}")
    print("  URL: http://127.0.0.1:8000")
    print("  Cierra esta ventana para apagar.")
    print("="*52 + "\n")

    def abrir_navegador():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:8000')

    threading.Thread(target=abrir_navegador, daemon=True).start()
    call_command('runserver', '127.0.0.1:8000', '--noreload')


if __name__ == '__main__':
    main()
