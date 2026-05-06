from django.urls import path
from . import views

urlpatterns = [
    path('auth/',           views.auth_choice,   name='auth_choice'),
    path('registro/',       views.registro,      name='registro'),
    path('login/',          views.login_view,    name='login'),
    path('logout/',         views.logout_view,   name='logout'),
    path('perfil/',                   views.perfil,          name='perfil'),
    path('perfil/editar/',            views.editar_perfil,   name='editar_perfil'),
    path('perfil/eliminar-avatar/',   views.eliminar_avatar, name='eliminar_avatar'),

    # Solicitud de profesional (usuario normal)
    path('profesional/solicitar/',             views.solicitar_profesional, name='solicitar_profesional'),
    path('profesional/activar/',               views.activar_profesional,   name='activar_profesional'),
    # Panel profesional
    path('profesional/dashboard/',             views.profesional_dashboard, name='profesional_dashboard'),
    path('profesional/cliente/<int:user_id>/', views.profesional_cliente,   name='profesional_cliente'),
    path('profesional/regenerar-codigo/',      views.regenerar_codigo,      name='regenerar_codigo'),
    # Admin Pro
    path('admin-pro/',                              views.admin_pro_dashboard,       name='admin_pro_dashboard'),
    path('admin-pro/usuario/<int:user_id>/',               views.admin_ver_usuario,    name='admin_ver_usuario'),
    path('admin-pro/usuario/<int:user_id>/crear-rutina/', views.admin_crear_rutina,   name='admin_crear_rutina'),
    path('admin-pro/revisar/<int:solicitud_id>/',         views.revisar_solicitud,    name='revisar_solicitud'),
    path('admin-pro/revocar/<int:user_id>/',        views.revocar_profesional_admin, name='revocar_profesional_admin'),

    # Privacidad del usuario
    path('privacidad/',                              views.privacidad,           name='privacidad'),
    path('privacidad/conectar/',                     views.conectar_profesional, name='conectar_profesional'),
    path('privacidad/permisos/<int:relacion_id>/',   views.actualizar_permisos,  name='actualizar_permisos'),
    path('privacidad/revocar/<int:relacion_id>/',    views.revocar_profesional,  name='revocar_profesional'),
]
