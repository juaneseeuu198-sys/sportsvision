from django.contrib import admin
from .models import CalculoCaloria


@admin.register(CalculoCaloria)
class CalculoCaloriaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'genero', 'edad', 'peso', 'tmb', 'getd', 'calculado_en']
    list_filter = ['genero', 'nivel_actividad', 'objetivo']
