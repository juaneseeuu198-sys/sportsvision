"""
Punto de entrada para SportsVision (.exe Windows / binario Linux).
Conecta a la base de datos central de Railway si existe db_config.txt al lado del ejecutable.
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
    r"""Carpeta de datos del usuario: %APPDATA%\SportsVision en Windows / ~/.sportsvision en Linux."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    else:
        base = os.path.expanduser('~')
    path = os.path.join(base, 'SportsVision')
    os.makedirs(path, exist_ok=True)
    return path


def cargar_env():
    """Carga .env desde al lado del ejecutable si existe."""
    env_path = os.path.join(exe_dir(), '.env')
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            print(f"[CONFIG] Variables cargadas desde {env_path}")
        except ImportError:
            # Cargar manualmente si dotenv no está disponible
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip())


def setup_database():
    """
    Prioridad de conexión:
    1. DATABASE_URL ya definida en entorno (variable de sistema)
    2. db_config.txt al lado del ejecutable  ← NUEVO
    3. db_config.txt bakeado dentro del .exe
    4. SQLite local en AppData
    """
    # 1. Variable de entorno ya definida
    if os.environ.get('DATABASE_URL'):
        print(f"[DB] Usando DATABASE_URL del entorno")
        return None

    # 2. db_config.txt externo (al lado del .exe)
    external_config = os.path.join(exe_dir(), 'db_config.txt')
    if os.path.exists(external_config):
        with open(external_config, 'r', encoding='utf-8') as f:
            db_url = f.read().strip()
        if db_url:
            os.environ['DATABASE_URL'] = db_url
            print(f"[DB] Conectado a Railway PostgreSQL (db_config.txt externo)")
            return None

    # 3. db_config.txt dentro del .exe
    internal_config = os.path.join(meipass(), 'db_config.txt')
    if os.path.exists(internal_config):
        with open(internal_config, 'r', encoding='utf-8') as f:
            db_url = f.read().strip()
        if db_url:
            os.environ['DATABASE_URL'] = db_url
            print(f"[DB] Conectado a Railway PostgreSQL (db_config.txt interno)")
            return None

    # 4. SQLite local
    data_dir  = user_data_dir()
    db_dest   = os.path.join(data_dir, 'db.sqlite3')
    db_origen = os.path.join(meipass(), 'db.sqlite3')
    if not os.path.exists(db_dest) and os.path.exists(db_origen):
        shutil.copy2(db_origen, db_dest)
    print(f"[DB] Usando SQLite local: {db_dest}")
    return db_dest


def main():
    # Cargar .env primero (credenciales de Gmail, etc.)
    cargar_env()

    internal = meipass()
    os.chdir(internal)

    db_path = setup_database()

    if db_path:
        os.environ['SPORTSVISION_DB'] = db_path

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsvision.settings')

    import django
    django.setup()

    from django.core.management import call_command

    print("Aplicando migraciones...")
    call_command('migrate', verbosity=0, interactive=False)

    print("\n" + "="*50)
    print("  SportsVision — Iniciando servidor...")
    print("  URL: http://127.0.0.1:8000")
    print("  Cierra esta ventana para apagar.")
    print("="*50 + "\n")

    def abrir_navegador():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:8000')

    threading.Thread(target=abrir_navegador, daemon=True).start()

    call_command('runserver', '127.0.0.1:8000', '--noreload')


if __name__ == '__main__':
    main()
