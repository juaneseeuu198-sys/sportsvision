from django.urls import path
from . import views

urlpatterns = [
    path('auth/',           views.auth_choice,   name='auth_choice'),
    path('registro/',       views.registro,      name='registro'),
    path('login/',          views.login_view,    name='login'),
    path('logout/',         views.logout_view,   name='logout'),
    path('perfil/',         views.perfil,        name='perfil'),
    path('perfil/editar/',  views.editar_perfil, name='editar_perfil'),
]
