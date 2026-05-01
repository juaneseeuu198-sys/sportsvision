from django.db import models
from django.contrib.auth.models import User


class RegistroPeso(models.Model):
    """Registro histórico del peso del usuario."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pesos')
    peso = models.FloatField()
    fecha = models.DateField(auto_now_add=True)
    notas = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Registro de Peso"
        verbose_name_plural = "Registros de Peso"

    def __str__(self):
        return f"{self.usuario.username} - {self.peso}kg - {self.fecha}"
