from django.db import models
from django.contrib.auth.models import User


class RegistroPeso(models.Model):
    """Registro histórico del peso del usuario."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pesos')
    peso    = models.FloatField()
    fecha   = models.DateField(auto_now_add=True)
    notas   = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Registro de Peso"
        verbose_name_plural = "Registros de Peso"

    def __str__(self):
        return f"{self.usuario.username} - {self.peso}kg - {self.fecha}"


class AnotacionCalendario(models.Model):
    """Marca un día como descanso o día de trabajo planeado (reemplaza localStorage)."""
    TIPO_CHOICES = [
        ('descanso', 'Descanso'),
        ('planeado', 'Día planeado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anotaciones_calendario')
    fecha   = models.DateField()
    tipo    = models.CharField(max_length=10, choices=TIPO_CHOICES)

    class Meta:
        unique_together = ['usuario', 'fecha']
        ordering = ['-fecha']
        verbose_name = "Anotación de Calendario"
        verbose_name_plural = "Anotaciones de Calendario"

    def __str__(self):
        return f"{self.usuario.username} — {self.fecha} — {self.tipo}"


class MedicionCorporal(models.Model):
    """Medidas corporales del usuario registradas con el tiempo."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mediciones')
    fecha   = models.DateField(auto_now_add=True)
    peso    = models.FloatField(null=True, blank=True, help_text="kg")
    cintura = models.FloatField(null=True, blank=True, help_text="cm")
    cadera  = models.FloatField(null=True, blank=True, help_text="cm")
    pecho   = models.FloatField(null=True, blank=True, help_text="cm")
    brazo   = models.FloatField(null=True, blank=True, help_text="cm")
    muslo   = models.FloatField(null=True, blank=True, help_text="cm")
    notas   = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Medición Corporal"
        verbose_name_plural = "Mediciones Corporales"

    def __str__(self):
        return f"{self.usuario.username} — {self.fecha}"
