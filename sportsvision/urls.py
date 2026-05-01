from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.landing, name='landing'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('usuarios/', include('apps.users.urls')),
    path('rutinas/', include('apps.routines.urls')),
    path('ejercicios/', include('apps.exercises.urls')),
    path('herramientas/', include('apps.tools.urls')),
    path('progreso/', include('apps.progress.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
