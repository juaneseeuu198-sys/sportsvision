from django.urls import path
from . import views

urlpatterns = [
    path('nueva/', views.paso3_ejercicios, name='paso3_ejercicios'),
    path('set-filtros/', views.set_filtros, name='set_filtros'),
    path('mis-rutinas/', views.mis_rutinas, name='mis_rutinas'),
    path('auto/', views.auto_generador, name='auto_generador'),
    path('entrenar/<int:rutina_id>/', views.iniciar_entrenamiento, name='iniciar_entrenamiento'),
    path('finalizar/<int:entrenamiento_id>/', views.finalizar_entrenamiento, name='finalizar_entrenamiento'),
    path('eliminar/<int:rutina_id>/', views.eliminar_rutina, name='eliminar_rutina'),
    path('plan-semanal/', views.plan_semanal, name='plan_semanal'),
    path('plan-semanal/generar/', views.generar_plan_auto, name='generar_plan_auto'),
    path('plan-semanal/recomendado/', views.aplicar_plan_recomendado, name='plan_recomendado'),
    path('<int:rutina_id>/pdf/', views.descargar_rutina_pdf, name='descargar_rutina_pdf'),
    path('entrenamiento/<int:entrenamiento_id>/autoguardar/', views.autoguardar_serie, name='autoguardar_serie'),
]
