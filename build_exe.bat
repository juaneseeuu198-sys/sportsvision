@echo off
echo ============================================
echo  Construyendo SportsVision.exe ...
echo ============================================

REM Instalar dependencias necesarias
pip install pyinstaller --quiet

REM Recolectar archivos estáticos
python manage.py collectstatic --noinput --clear

REM Construir el .exe (archivo único)
pyinstaller ^
  --name "SportsVision" ^
  --onefile ^
  --console ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "staticfiles;staticfiles" ^
  --add-data "apps;apps" ^
  --add-data "sportsvision;sportsvision" ^
  --add-data "db.sqlite3;." ^
  --hidden-import "django.contrib.admin" ^
  --hidden-import "django.contrib.auth" ^
  --hidden-import "django.contrib.contenttypes" ^
  --hidden-import "django.contrib.sessions" ^
  --hidden-import "django.contrib.messages" ^
  --hidden-import "django.contrib.staticfiles" ^
  --hidden-import "django.template.backends.django" ^
  --hidden-import "apps.users" ^
  --hidden-import "apps.routines" ^
  --hidden-import "apps.exercises" ^
  --hidden-import "apps.tools" ^
  --hidden-import "apps.progress" ^
  --hidden-import "PIL" ^
  launcher.py

echo.
echo ============================================
echo  Listo! El ejecutable esta en: dist\SportsVision.exe
echo  Solo distribuye ese archivo .exe
echo ============================================
pause
