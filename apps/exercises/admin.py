from django.contrib import admin
from .models import Ejercicio, GrupoMuscular, Equipo


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono']


@admin.register(GrupoMuscular)
class GrupoMuscularAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug']
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'grupo_muscular', 'nivel']
    list_filter = ['grupo_muscular', 'nivel', 'equipos']
    search_fields = ['nombre']
    filter_horizontal = ['equipos']
