from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_progreso, name='calendario_progreso'),
]
