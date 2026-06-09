from django.db import models
from django.contrib.auth.models import User


class CalculoCaloria(models.Model):
    GENERO_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]
    ACTIVIDAD_CHOICES = [
        ('sedentario', 'Sedentario (x1.2)'),
        ('poca',       'Poca actividad (x1.375)'),
        ('activo',     'Activo (x1.55)'),
        ('diario',     'Entrena a diario (x1.725)'),
        ('atleta',     'Atleta (x1.9)'),
    ]
    OBJETIVO_CHOICES = [
        ('perder_rapido', 'Perder peso rápido (-1kg/sem)'),
        ('perder',        'Perder peso (-0.5kg/sem)'),
        ('mantener',      'Mantener peso'),
        ('ganar',         'Ganar peso (+0.5kg/sem)'),
        ('ganar_rapido',  'Ganar peso rápido (+1kg/sem)'),
    ]

    usuario         = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre          = models.CharField(max_length=80, blank=True, default='', help_text='Nombre de la dieta')
    activa          = models.BooleanField(default=False, help_text='Dieta activa del usuario')
    genero          = models.CharField(max_length=1,  choices=GENERO_CHOICES)
    edad            = models.PositiveIntegerField()
    peso            = models.FloatField()
    altura          = models.FloatField()
    nivel_actividad = models.CharField(max_length=20, choices=ACTIVIDAD_CHOICES)
    objetivo        = models.CharField(max_length=20, choices=OBJETIVO_CHOICES)
    tmb             = models.FloatField(null=True, blank=True)
    getd            = models.FloatField(null=True, blank=True)
    proteinas_g     = models.FloatField(null=True, blank=True)
    carbos_g        = models.FloatField(null=True, blank=True)
    grasas_g        = models.FloatField(null=True, blank=True)
    calculado_en    = models.DateTimeField(auto_now_add=True)

    FACTORES_ACTIVIDAD = {
        'sedentario': 1.2, 'poca': 1.375, 'activo': 1.55,
        'diario': 1.725,   'atleta': 1.9,
    }
    AJUSTE_OBJETIVO = {
        'perder_rapido': -1000, 'perder': -500, 'mantener': 0,
        'ganar': 500,           'ganar_rapido': 1000,
    }

    def calcular(self):
        if self.genero == 'M':
            self.tmb = (10 * self.peso) + (6.25 * self.altura) - (5 * self.edad) + 5
        else:
            self.tmb = (10 * self.peso) + (6.25 * self.altura) - (5 * self.edad) - 161
        factor      = self.FACTORES_ACTIVIDAD.get(self.nivel_actividad, 1.55)
        ajuste      = self.AJUSTE_OBJETIVO.get(self.objetivo, 0)
        self.getd   = round(self.tmb * factor + ajuste, 0)
        self.tmb    = round(self.tmb, 0)
        self.proteinas_g = round((self.getd * 0.30) / 4, 1)
        self.carbos_g    = round((self.getd * 0.40) / 4, 1)
        self.grasas_g    = round((self.getd * 0.30) / 9, 1)

    class Meta:
        verbose_name          = "Cálculo de Calorías"
        verbose_name_plural   = "Cálculos de Calorías"
        ordering              = ['-calculado_en']

    def __str__(self):
        return self.nombre or f"Dieta {self.calculado_en.date() if self.calculado_en else ''}"


class PlanNutricional(models.Model):
    OBJETIVO_CHOICES = [
        ('perder',   'Perder peso'),
        ('mantener', 'Mantener peso'),
        ('ganar',    'Ganar peso'),
    ]
    RESTRICCION_CHOICES = [
        ('ninguna',     'Sin restricción'),
        ('vegetariano', 'Vegetariano'),
        ('vegano',      'Vegano'),
        ('sin_gluten',  'Sin gluten'),
        ('sin_lactosa', 'Sin lactosa'),
    ]

    usuario      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planes_nutricionales')
    nombre       = models.CharField(max_length=80, blank=True, default='')
    activa       = models.BooleanField(default=False)
    genero       = models.CharField(max_length=1)
    edad         = models.PositiveIntegerField()
    peso         = models.FloatField()
    altura       = models.FloatField()
    objetivo     = models.CharField(max_length=20, choices=OBJETIVO_CHOICES)
    restriccion  = models.CharField(max_length=20, choices=RESTRICCION_CHOICES, default='ninguna')
    comidas_dia  = models.PositiveIntegerField(default=3)
    calorias_dia = models.FloatField()
    proteinas_g  = models.FloatField()
    carbos_g     = models.FloatField()
    grasas_g     = models.FloatField()
    plan_json    = models.JSONField(default=list)   # lista de comidas
    creado_en    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Plan Nutricional"
        verbose_name_plural = "Planes Nutricionales"
        ordering            = ['-creado_en']

    def __str__(self):
        return self.nombre or f"Plan {self.creado_en.date() if self.creado_en else ''}"
