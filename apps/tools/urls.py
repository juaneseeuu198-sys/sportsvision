from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.herramientas,            name='herramientas'),
    path('calorias/',                               views.calculadora_calorias,    name='calculadora_calorias'),
    path('imc/',                                    views.calculadora_imc,         name='calculadora_imc'),
    path('plan-nutricional/',                       views.plan_nutricional,        name='plan_nutricional'),
    # Mis Dietas
    path('mis-dietas/',                             views.mis_dietas,              name='mis_dietas'),
    # Cálculo de calorías
    path('mis-dietas/guardar/',                     views.guardar_dieta,           name='guardar_dieta'),
    path('mis-dietas/eliminar/<int:dieta_id>/',     views.eliminar_dieta,          name='eliminar_dieta'),
    path('mis-dietas/activar/<int:dieta_id>/',      views.activar_dieta,           name='activar_dieta'),
    # Plan nutricional
    path('mis-dietas/guardar-plan/',                views.guardar_plan_nutricional, name='guardar_plan_nutricional'),
    path('mis-dietas/eliminar-plan/<int:plan_id>/', views.eliminar_plan,           name='eliminar_plan'),
    path('mis-dietas/activar-plan/<int:plan_id>/',  views.activar_plan,            name='activar_plan'),
    # FitBot
    path('asistente/',                              views.chatbot,                 name='chatbot'),
    # PDF downloads
    path('mis-dietas/<int:plan_id>/pdf/',           views.descargar_dieta_pdf,     name='descargar_dieta_pdf'),
]
