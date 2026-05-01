from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ejercicios, name='ejercicios_lista'),
    path('<int:pk>/', views.detalle_ejercicio, name='ejercicio_detalle'),
]
