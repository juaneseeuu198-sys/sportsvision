from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.http import JsonResponse
from apps.users import views as user_views


def app_version(request):
    return JsonResponse({
        'version_code': settings.APP_VERSION_CODE,
        'version_name': settings.APP_VERSION_NAME,
        'apk_url': f"{settings.FRONTEND_URL}/static/app/SportsVision.apk",
    })

urlpatterns = [
    # ── PWA ───────────────────────────────────────────────────────────────────
    path('manifest.json', TemplateView.as_view(
        template_name='pwa/manifest.json',
        content_type='application/json',
    ), name='manifest'),
    path('sw.js', TemplateView.as_view(
        template_name='pwa/sw.js',
        content_type='application/javascript',
    ), name='sw'),

    path('api/version/', app_version, name='app_version'),
    path('i18n/', include('django.conf.urls.i18n')),  # set_language
    path('admin/', admin.site.urls),
    path('', user_views.landing, name='landing'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('usuarios/', include('apps.users.urls')),
    path('rutinas/', include('apps.routines.urls')),
    path('ejercicios/', include('apps.exercises.urls')),
    path('herramientas/', include('apps.tools.urls')),
    path('progreso/', include('apps.progress.urls')),

    # ── Recuperación de contraseña ─────────────────────────────────────────────
    path('usuarios/recuperar/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/emails/password_reset_email.html',
             subject_template_name='users/emails/password_reset_subject.txt',
             success_url='/usuarios/recuperar/enviado/',
         ),
         name='password_reset'),

    path('usuarios/recuperar/enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html',
         ),
         name='password_reset_done'),

    path('usuarios/recuperar/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/usuarios/recuperar/listo/',
         ),
         name='password_reset_confirm'),

    path('usuarios/recuperar/listo/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html',
         ),
         name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
