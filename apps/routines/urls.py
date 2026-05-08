from django.urls import path
from . import views

urlpatterns = [
    path('nueva/paso1/', views.paso1_equipo, name='paso1_equipo'),
    path('nueva/paso2/', views.paso2_musculos, name='paso2_musculos'),
    path('nueva/paso3/', views.paso3_ejercicios, name='paso3_ejercicios'),
    path('set-filtros/', views.set_filtros, name='set_filtros'),
    path('mis-rutinas/', views.mis_rutinas, name='mis_rutinas'),
    path('auto/', views.auto_generador, name='auto_generador'),
    path('entrenar/<int:rutina_id>/', views.iniciar_entrenamiento, name='iniciar_entrenamiento'),
    path('finalizar/<int:entrenamiento_id>/', views.finalizar_entrenamiento, name='finalizar_entrenamiento'),
    path('eliminar/<int:rutina_id>/', views.eliminar_rutina, name='eliminar_rutina'),
    path('plan-semanal/', views.plan_semanal, name='plan_semanal'),
    path('plan-semanal/generar/', views.generar_plan_auto, name='generar_plan_auto'),
    path('plan-semanal/recomendado/', views.aplicar_plan_recomendado, name='plan_recomendado'),
]
