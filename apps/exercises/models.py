from django.db import models


class Equipo(models.Model):
    EQUIPO_CHOICES = [
        ('banco', 'Banco'),
        ('peso_corporal', 'Peso Corporal'),
        ('disco', 'Disco'),
        ('mancuernas', 'Mancuernas'),
        ('barra', 'Barra'),
        ('barra_dominadas', 'Barra de Dominadas'),
        ('kettlebell', 'Kettlebell'),
        ('banda', 'Banda'),
    ]
    nombre = models.CharField(max_length=50, choices=EQUIPO_CHOICES, unique=True)
    icono = models.CharField(max_length=10, blank=True, default='🏋️')
    imagen = models.ImageField(upload_to='equipos/', null=True, blank=True)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return self.get_nombre_display()


class GrupoMuscular(models.Model):
    nombre = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Grupo Muscular"
        verbose_name_plural = "Grupos Musculares"

    def __str__(self):
        return self.nombre


class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    instrucciones = models.TextField(blank=True)
    grupo_muscular = models.ForeignKey(
        GrupoMuscular,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ejercicios'
    )
    equipos = models.ManyToManyField(Equipo, blank=True, related_name='ejercicios')
    imagen = models.ImageField(upload_to='ejercicios/', null=True, blank=True)
    gif = models.FileField(upload_to='ejercicios/gifs/', null=True, blank=True)
    nivel = models.CharField(
        max_length=20,
        choices=[('principiante', 'Principiante'), ('intermedio', 'Intermedio'), ('avanzado', 'Avanzado')],
        default='principiante'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
