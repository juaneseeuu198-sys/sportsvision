from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_progreso, name='calendario_progreso'),
    path('anotar/', views.anotar_dia, name='anotar_dia'),
    path('gcal/sync/', views.gcal_sync_all, name='gcal_sync_all'),
]
