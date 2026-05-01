from django.db import models
from django.contrib.auth.models import User
from apps.exercises.models import Ejercicio, Equipo, GrupoMuscular


class Rutina(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rutinas')
    nombre = models.CharField(max_length=100, default='Mi Rutina')
    descripcion = models.TextField(blank=True)
    equipos = models.ManyToManyField(Equipo, blank=True)
    grupos_musculares = models.ManyToManyField(GrupoMuscular, blank=True)
    nivel = models.CharField(
        max_length=20,
        choices=[('principiante', 'Principiante'), ('intermedio', 'Intermedio'), ('avanzado', 'Avanzado')],
        default='principiante'
    )
    es_auto_generada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

    def total_ejercicios(self):
        return self.ejercicios_rutina.count()


class EjercicioRutina(models.Model):
    """Ejercicio dentro de una rutina, con orden."""
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='ejercicios_rutina')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField(default=0)
    series_sugeridas = models.PositiveIntegerField(default=3)
    repeticiones_sugeridas = models.PositiveIntegerField(default=12)

    class Meta:
        ordering = ['orden']
        verbose_name = "Ejercicio en Rutina"
        verbose_name_plural = "Ejercicios en Rutina"

    def __str__(self):
        return f"{self.ejercicio.nombre} en {self.rutina.nombre}"


class Entrenamiento(models.Model):
    """Registro de una sesión de entrenamiento completada."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entrenamientos')
    rutina = models.ForeignKey(Rutina, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=100, default='Entrenamiento')
    iniciado_en = models.DateTimeField(auto_now_add=True)
    terminado_en = models.DateTimeField(null=True, blank=True)
    completado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Entrenamiento"
        verbose_name_plural = "Entrenamientos"
        ordering = ['-iniciado_en']

    def __str__(self):
        return f"Entrenamiento de {self.usuario.username} - {self.iniciado_en.date()}"

    def peso_total(self):
        total = 0
        for serie in self.series.all():
            if serie.peso:
                total += serie.peso * (serie.repeticiones or 0)
        return round(total, 1)

    def duracion(self):
        if self.terminado_en:
            delta = self.terminado_en - self.iniciado_en
            minutos = int(delta.total_seconds() // 60)
            return f"{minutos} min"
        return "En progreso"


class SerieEntrenamiento(models.Model):
    """Una serie específica dentro de un entrenamiento."""
    entrenamiento = models.ForeignKey(Entrenamiento, on_delete=models.CASCADE, related_name='series')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    numero_serie = models.PositiveIntegerField(default=1)
    repeticiones = models.PositiveIntegerField(null=True, blank=True)
    peso = models.FloatField(null=True, blank=True, help_text="Peso en kg")
    peso_corporal = models.FloatField(null=True, blank=True)
    tiempo_minutos = models.PositiveIntegerField(null=True, blank=True)
    tiempo_segundos = models.PositiveIntegerField(null=True, blank=True)
    completada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ejercicio', 'numero_serie']
        verbose_name = "Serie"
        verbose_name_plural = "Series"

    def __str__(self):
        return f"Set {self.numero_serie} - {self.ejercicio.nombre}"
