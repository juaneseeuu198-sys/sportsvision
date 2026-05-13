from django.urls import path
from . import views

urlpatterns = [
    path('auth/',                    views.auth_choice,               name='auth_choice'),
    # Registro en 3 pasos
    path('registro/',                views.iniciar_registro,          name='iniciar_registro'),
    path('registro/verificar/',      views.confirmar_email_registro,  name='confirmar_email_registro'),
    path('registro/completar/',      views.registro,                  name='registro'),
    path('bienvenido/',              views.bienvenido,                name='bienvenido'),
    path('login/',          views.login_view,         name='login'),
    path('logout/',         views.logout_view,        name='logout'),
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
    path('admin-pro/banear/<int:user_id>/',         views.banear_usuario,            name='banear_usuario'),
    path('admin-pro/sancionar/<int:user_id>/',      views.sancionar_usuario,         name='sancionar_usuario'),
    path('admin-pro/verificar-password/',           views.verificar_password_admin,  name='verificar_password_admin'),

    # Privacidad del usuario
    path('privacidad/',                              views.privacidad,           name='privacidad'),
    path('privacidad/conectar/',                     views.conectar_profesional, name='conectar_profesional'),
    path('privacidad/permisos/<int:relacion_id>/',   views.actualizar_permisos,  name='actualizar_permisos'),
    path('privacidad/revocar/<int:relacion_id>/',    views.revocar_profesional,  name='revocar_profesional'),

    path('terminos/', views.terminos_condiciones, name='terminos_condiciones'),
    # Google OAuth
    path('auth/google/',                  views.google_login,             name='google_login'),
    path('auth/google/callback/',         views.google_callback,          name='google_callback'),
    path('auth/google/completar-perfil/', views.completar_perfil_google,  name='completar_perfil_google'),
]
