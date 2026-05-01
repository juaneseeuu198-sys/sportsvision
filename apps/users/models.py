from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    edad = models.PositiveIntegerField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True, help_text="Peso en kg")
    altura = models.FloatField(null=True, blank=True, help_text="Altura en cm")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"
