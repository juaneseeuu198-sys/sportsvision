"""
Punto de entrada para SportsVision (.exe Windows / binario Linux).
SIEMPRE conecta a Railway PostgreSQL — sin fallback local.
"""
import os
import sys
import threading
import webbrowser
import time


def exe_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def meipass():
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


def _leer_env_file(path):
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
    # 1. .env externo (al lado del .exe, tiene prioridad)
    ext = os.path.join(exe_dir(), '.env')
    if os.path.exists(ext):
        _leer_env_file(ext)

    # 2. .env interno (bakeado en el .exe)
    interno = os.path.join(meipass(), '.env')
    if os.path.exists(interno) and interno != ext:
        _leer_env_file(interno)


def obtener_database_url():
    """
    Busca DATABASE_URL en orden de prioridad.
    Retorna la URL o None si no se encuentra.
    """
    # 1. Variable de entorno ya definida (cargada desde .env)
    if os.environ.get('DATABASE_URL'):
        return os.environ['DATABASE_URL']

    # 2. db_config.txt externo
    ext = os.path.join(exe_dir(), 'db_config.txt')
    if os.path.exists(ext):
        url = open(ext, encoding='utf-8').read().strip()
        if url:
            return url

    # 3. db_config.txt interno
    interno = os.path.join(meipass(), 'db_config.txt')
    if os.path.exists(interno):
        url = open(interno, encoding='utf-8').read().strip()
        if url:
            return url

    return None


def main():
    cargar_env()

    db_url = obtener_database_url()

    if not db_url:
        print("=" * 55)
        print("  ERROR: No se encontró la URL de la base de datos.")
        print("  Coloca un archivo db_config.txt al lado del .exe")
        print("  con la URL de Railway PostgreSQL.")
        print("=" * 55)
        input("Presiona Enter para salir...")
        sys.exit(1)

    os.environ['DATABASE_URL'] = db_url

    os.chdir(meipass())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsvision.settings')

    import django
    django.setup()

    # Verificar conexión a Railway antes de continuar
    try:
        from django.db import connection
        connection.ensure_connection()
        print("[DB] ✓ Conectado a Railway PostgreSQL")
    except Exception as e:
        print("=" * 55)
        print(f"  ERROR: No se pudo conectar a la base de datos.")
        print(f"  Verifica tu conexión a internet.")
        print(f"  Detalle: {e}")
        print("=" * 55)
        input("Presiona Enter para salir...")
        sys.exit(1)

    from django.core.management import call_command
    print("Aplicando migraciones...")
    call_command('migrate', verbosity=0, interactive=False)

    print("\n" + "=" * 52)
    print("  SportsVision")
    print("  Base de datos: Railway PostgreSQL ✓")
    print("  URL: http://127.0.0.1:8000")
    print("  Cierra esta ventana para apagar.")
    print("=" * 52 + "\n")

    threading.Thread(
        target=lambda: (time.sleep(2), webbrowser.open('http://127.0.0.1:8000')),
        daemon=True
    ).start()

    call_command('runserver', '127.0.0.1:8000', '--noreload')


if __name__ == '__main__':
    main()
