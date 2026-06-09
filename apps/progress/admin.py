from django.contrib import admin
from .models import RegistroPeso


@admin.register(RegistroPeso)
class RegistroPesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'peso', 'fecha']
    list_filter = ['fecha']
