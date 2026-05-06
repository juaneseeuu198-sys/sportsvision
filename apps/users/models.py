import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    OBJETIVO_CHOICES = [
        ('bajar_peso',          'Bajar de peso'),
        ('mantener_peso',       'Mantener peso'),
        ('ganar_musculo',       'Ganar músculo'),
        ('mejorar_resistencia', 'Mejorar resistencia'),
        ('mejorar_flexibilidad','Mejorar flexibilidad'),
        ('rendimiento',         'Rendimiento deportivo'),
    ]
    NIVEL_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio',   'Intermedio'),
        ('avanzado',     'Avanzado'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    ROL_CHOICES = [
        ('usuario',       'Usuario'),
        ('profesional',   'Profesional / Entrenador'),
        ('admin_pro',     'Profesional Principal (Admin)'),
    ]

    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    edad          = models.PositiveIntegerField(null=True, blank=True)
    peso          = models.FloatField(null=True, blank=True, help_text="Peso en kg")
    altura        = models.FloatField(null=True, blank=True, help_text="Altura en cm")
    avatar        = models.ImageField(upload_to='avatars/', null=True, blank=True)
    avatar_data   = models.TextField(blank=True, default='',
                                     help_text="Avatar en base64 (persiste en BD)")
    genero        = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, default='')
    objetivo      = models.CharField(max_length=30, choices=OBJETIVO_CHOICES, blank=True, default='')
    nivel         = models.CharField(max_length=15, choices=NIVEL_CHOICES, default='principiante')
    limitaciones  = models.JSONField(default=list, blank=True,
                                     help_text="Lista de condiciones físicas o limitaciones del usuario")
    rol           = models.CharField(max_length=15, choices=ROL_CHOICES, default='usuario')
    # Solo para profesionales: código único de invitación
    codigo_pro    = models.CharField(max_length=10, blank=True, default='',
                                     help_text="Código único para que usuarios se conecten")
    especialidad  = models.CharField(max_length=100, blank=True, default='',
                                     help_text="Ej: Entrenador personal, Nutricionista")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def generar_codigo(self):
        """Genera un código único de 6 caracteres para el profesional."""
        self.codigo_pro = uuid.uuid4().hex[:6].upper()
        self.save(update_fields=['codigo_pro', 'rol', 'especialidad'])

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"


class RelacionProfesional(models.Model):
    """
    Vincula un profesional con un usuario, con consentimiento granular.
    El usuario controla exactamente qué datos comparte.
    """
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente de aprobación'),
        ('activa',     'Activa'),
        ('revocada',   'Revocada por el usuario'),
        ('rechazada',  'Rechazada por el usuario'),
    ]

    profesional  = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='mis_clientes')
    usuario      = models.ForeignKey(User, on_delete=models.CASCADE,
                                     related_name='mis_profesionales')
    estado       = models.CharField(max_length=12, choices=ESTADO_CHOICES,
                                    default='pendiente')

    # Consentimientos granulares (usuario decide qué compartir)
    ver_datos_basicos    = models.BooleanField(default=True,
        help_text="Nombre, objetivo, nivel, edad, peso, altura")
    ver_entrenamientos   = models.BooleanField(default=True,
        help_text="Historial de entrenamientos y series")
    ver_mediciones       = models.BooleanField(default=False,
        help_text="Mediciones corporales: peso, grasa, medidas")
    ver_nutricion        = models.BooleanField(default=False,
        help_text="Plan nutricional y calorías")
    ver_salud            = models.BooleanField(default=False,
        help_text="Condiciones de salud y limitaciones (dato sensible)")

    fecha_solicitud  = models.DateTimeField(auto_now_add=True)
    fecha_respuesta  = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['profesional', 'usuario']
        verbose_name = "Relación Profesional-Usuario"
        verbose_name_plural = "Relaciones Profesional-Usuario"

    def __str__(self):
        return f"{self.profesional.username} → {self.usuario.username} ({self.estado})"


class SolicitudProfesional(models.Model):
    """
    Solicitud de un usuario para convertirse en profesional.
    El Admin Pro revisa y aprueba o rechaza.
    """
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente'),
        ('aprobada',   'Aprobada'),
        ('rechazada',  'Rechazada'),
    ]

    usuario      = models.OneToOneField(User, on_delete=models.CASCADE,
                                         related_name='solicitud_profesional')
    especialidad = models.CharField(max_length=120,
                                    help_text="Área de especialización")
    experiencia  = models.TextField(help_text="Años de experiencia y formación")
    motivo       = models.TextField(help_text="Por qué quiere ser profesional en la plataforma")
    estado       = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='pendiente')
    nota_admin   = models.TextField(blank=True, default='',
                                    help_text="Nota del Admin Pro al aprobar/rechazar")
    fecha_envio  = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    revisado_por = models.ForeignKey(User, null=True, blank=True,
                                     on_delete=models.SET_NULL,
                                     related_name='solicitudes_revisadas')

    class Meta:
        verbose_name = "Solicitud de Profesional"
        verbose_name_plural = "Solicitudes de Profesional"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"Solicitud de {self.usuario.username} ({self.estado})"


class EmailVerificationToken(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE,
                                      related_name='email_verification_token')
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    class Meta:
        verbose_name = "Token de verificación de correo"

    def __str__(self):
        return f"Token de {self.user.username}"
