from django.db import models
from django.contrib.auth.models import User


class CalculoCaloria(models.Model):
    GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]
    ACTIVIDAD_CHOICES = [
        ('sedentario', 'Sedentario (x1.2)'),
        ('poca', 'Poca actividad (x1.375)'),
        ('activo', 'Activo (x1.55)'),
        ('diario', 'Entrena a diario (x1.725)'),
        ('atleta', 'Atleta (x1.9)'),
    ]
    OBJETIVO_CHOICES = [
        ('perder_rapido', 'Perder peso rápido (-1kg/sem)'),
        ('perder', 'Perder peso (-0.5kg/sem)'),
        ('mantener', 'Mantener peso'),
        ('ganar', 'Ganar peso (+0.5kg/sem)'),
        ('ganar_rapido', 'Ganar peso rápido (+1kg/sem)'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    edad = models.PositiveIntegerField()
    peso = models.FloatField()
    altura = models.FloatField()
    nivel_actividad = models.CharField(max_length=20, choices=ACTIVIDAD_CHOICES)
    objetivo = models.CharField(max_length=20, choices=OBJETIVO_CHOICES)
    # Resultados calculados
    tmb = models.FloatField(null=True, blank=True)
    getd = models.FloatField(null=True, blank=True)
    proteinas_g = models.FloatField(null=True, blank=True)
    carbos_g = models.FloatField(null=True, blank=True)
    grasas_g = models.FloatField(null=True, blank=True)
    calculado_en = models.DateTimeField(auto_now_add=True)

    FACTORES_ACTIVIDAD = {
        'sedentario': 1.2,
        'poca': 1.375,
        'activo': 1.55,
        'diario': 1.725,
        'atleta': 1.9,
    }
    AJUSTE_OBJETIVO = {
        'perder_rapido': -1000,
        'perder': -500,
        'mantener': 0,
        'ganar': 500,
        'ganar_rapido': 1000,
    }

    def calcular(self):
        if self.genero == 'M':
            self.tmb = (10 * self.peso) + (6.25 * self.altura) - (5 * self.edad) + 5
        else:
            self.tmb = (10 * self.peso) + (6.25 * self.altura) - (5 * self.edad) - 161

        factor = self.FACTORES_ACTIVIDAD.get(self.nivel_actividad, 1.55)
        ajuste = self.AJUSTE_OBJETIVO.get(self.objetivo, 0)
        self.getd = round(self.tmb * factor + ajuste, 0)
        self.tmb = round(self.tmb, 0)

        # Macros: 30% proteína, 40% carbs, 30% grasa
        self.proteinas_g = round((self.getd * 0.30) / 4, 1)
        self.carbos_g = round((self.getd * 0.40) / 4, 1)
        self.grasas_g = round((self.getd * 0.30) / 9, 1)

    class Meta:
        verbose_name = "Cálculo de Calorías"
        verbose_name_plural = "Cálculos de Calorías"

    def __str__(self):
        return f"Cálculo {self.usuario} - {self.calculado_en.date() if self.calculado_en else ''}"
