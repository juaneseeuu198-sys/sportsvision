"""
Punto de entrada para SportsVision (.exe Windows / binario Linux).
SIEMPRE conecta a Railway PostgreSQL — sin fallback local.
"""
import os
import sys
import threading
import webbrowser
import time
import socket


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
    ext = os.path.join(exe_dir(), '.env')
    if os.path.exists(ext):
        _leer_env_file(ext)
    interno = os.path.join(meipass(), '.env')
    if os.path.exists(interno) and interno != ext:
        _leer_env_file(interno)


def obtener_database_url():
    if os.environ.get('DATABASE_URL'):
        return os.environ['DATABASE_URL']
    for base in (exe_dir(), meipass()):
        path = os.path.join(base, 'db_config.txt')
        if os.path.exists(path):
            url = open(path, encoding='utf-8').read().strip()
            if url:
                return url
    return None


def esperar_servidor(host='127.0.0.1', port=8000, timeout=30):
    """Espera hasta que el servidor esté escuchando, luego abre el navegador."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                webbrowser.open(f'http://{host}:{port}')
                return
        except OSError:
            time.sleep(0.2)
    # Fallback si no responde en tiempo
    webbrowser.open(f'http://{host}:{port}')


def hay_migraciones_pendientes():
    """Devuelve True solo si hay migraciones sin aplicar."""
    try:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        return bool(plan)
    except Exception:
        return True  # En caso de error, ejecutar migraciones por seguridad


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
    # En el exe siempre corre en localhost
    os.environ['FRONTEND_URL'] = 'http://127.0.0.1:8000'
    os.chdir(meipass())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsvision.settings')

    import django
    django.setup()

    # Verificar conexión
    try:
        from django.db import connection
        connection.ensure_connection()
    except Exception as e:
        print("=" * 55)
        print("  ERROR: No se pudo conectar a la base de datos.")
        print("  Verifica tu conexión a internet.")
        print(f"  Detalle: {e}")
        print("=" * 55)
        input("Presiona Enter para salir...")
        sys.exit(1)

    # Solo migrar si hay cambios pendientes
    from django.core.management import call_command
    if hay_migraciones_pendientes():
        print("Aplicando migraciones...")
        call_command('migrate', verbosity=0, interactive=False)

    print("\n" + "=" * 52)
    print("  SportsVision")
    print("  Base de datos: Railway PostgreSQL OK")
    print("  URL: http://127.0.0.1:8000")
    print("  Cierra esta ventana para apagar.")
    print("=" * 52 + "\n")

    # Abrir navegador cuando el servidor esté listo (sin sleep fijo)
    threading.Thread(
        target=esperar_servidor,
        daemon=True
    ).start()

    call_command('runserver', '127.0.0.1:8000', '--noreload')


if __name__ == '__main__':
    main()
