from django.contrib import admin
from .models import Rutina, EjercicioRutina, Entrenamiento, SerieEntrenamiento


class EjercicioRutinaInline(admin.TabularInline):
    model = EjercicioRutina
    extra = 1


@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'usuario', 'nivel', 'es_auto_generada', 'total_ejercicios', 'creada_en']
    list_filter = ['nivel', 'es_auto_generada']
    search_fields = ['nombre', 'usuario__username']
    inlines = [EjercicioRutinaInline]


class SerieInline(admin.TabularInline):
    model = SerieEntrenamiento
    extra = 0
    readonly_fields = ['creada_en']


@admin.register(Entrenamiento)
class EntrenamientoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre', 'iniciado_en', 'completado', 'peso_total']
    list_filter = ['completado']
    inlines = [SerieInline]
