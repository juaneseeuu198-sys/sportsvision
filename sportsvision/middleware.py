from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages


class SuspensionMiddleware:
    """Bloquea el acceso a usuarios baneados o con sanción activa en cada request."""

    RUTAS_PUBLICAS = {
        '/usuarios/login/',
        '/usuarios/logout/',
        '/usuarios/registro/',
        '/usuarios/registro/verificar/',
        '/usuarios/registro/completar/',
        '/usuarios/auth/',
        '/',
        '/manifest.json',
        '/sw.js',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path

            # Permitir siempre rutas públicas y estáticas
            if path.startswith('/static/') or path.startswith('/media/'):
                return self.get_response(request)
            if path in self.RUTAS_PUBLICAS:
                return self.get_response(request)

            # Usuario baneado (is_active=False)
            if not request.user.is_active:
                logout(request)
                messages.error(request, 'Tu cuenta ha sido baneada. Contacta al administrador.')
                return redirect('login')

            # Usuario con sanción temporal activa
            try:
                profile = request.user.profile
                if profile.suspendido_hasta and profile.suspendido_hasta > timezone.now():
                    hasta = profile.suspendido_hasta.strftime('%d/%m/%Y %H:%M')
                    logout(request)
                    messages.error(request, f'Tu cuenta está suspendida hasta el {hasta}.')
                    return redirect('login')
            except Exception:
                pass

        return self.get_response(request)
