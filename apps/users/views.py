from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
import random
import requests as http_requests
from .forms import RegistroForm, EditarUsuarioForm, EditarPerfilForm, CompletarPerfilGoogleForm
from .models import UserProfile, RelacionProfesional, SolicitudProfesional, EmailPreVerification


def landing(request):
    """Página de inicio / landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/landing.html')


def auth_choice(request):
    """Pantalla de elección: Login o Registro."""
    return render(request, 'users/auth_choice.html')


def _enviar_otp_registro(email, codigo):
    """Envía el código OTP vía Brevo HTTP API (no SMTP)."""
    html = render_to_string('users/emails/otp_registro_email.html', {
        'codigo': codigo,
        'email': email,
    })
    resp = http_requests.post(
        'https://api.brevo.com/v3/smtp/email',
        headers={
            'api-key': settings.BREVO_API_KEY,
            'Content-Type': 'application/json',
        },
        json={
            'sender': {'name': 'SportsVision', 'email': 'sportsvisionmanager@gmail.com'},
            'to': [{'email': email}],
            'subject': f'SportsVision — Tu código de verificación: {codigo}',
            'htmlContent': html,
        },
        timeout=15,
    )
    resp.raise_for_status()


@csrf_exempt
def iniciar_registro(request):
    """Paso 1 — El usuario ingresa su email y recibe un código OTP."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            error = 'Ingresa tu correo electrónico.'
        elif User.objects.filter(email=email).exists():
            error = 'Este correo ya se encuentra registrado. ¿Quieres iniciar sesión?'
        else:
            # Invalidar códigos anteriores para este email
            EmailPreVerification.objects.filter(email=email, is_used=False).update(is_used=True)
            codigo = str(random.randint(100000, 999999))
            EmailPreVerification.objects.create(email=email, codigo=codigo)
            try:
                _enviar_otp_registro(email, codigo)
                request.session['email_registro'] = email
                return redirect('confirmar_email_registro')
            except Exception as e:
                error = f'Error al enviar el código: {e}'

    return render(request, 'users/inicio_registro.html', {'error': error})


@csrf_exempt
def confirmar_email_registro(request):
    """Paso 2 — El usuario ingresa el código OTP recibido por correo."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    email = request.session.get('email_registro')
    if not email:
        return redirect('iniciar_registro')

    error = None
    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'reenviar':
            EmailPreVerification.objects.filter(email=email, is_used=False).update(is_used=True)
            codigo = str(random.randint(100000, 999999))
            EmailPreVerification.objects.create(email=email, codigo=codigo)
            try:
                _enviar_otp_registro(email, codigo)
                messages.success(request, 'Código reenviado.')
            except Exception as e:
                error = f'Error al reenviar: {e}'

        elif accion == 'verificar':
            codigo_ingresado = request.POST.get('codigo', '').strip()
            preverif = EmailPreVerification.objects.filter(
                email=email, is_used=False
            ).order_by('-created_at').first()

            if not preverif:
                error = 'No hay código pendiente. Solicita uno nuevo.'
            elif preverif.is_expired():
                error = 'El código expiró. Haz clic en "Reenviar código".'
            elif preverif.codigo != codigo_ingresado:
                error = 'Código incorrecto. Inténtalo de nuevo.'
            else:
                preverif.is_used = True
                preverif.save()
                request.session['email_verificado'] = email
                request.session.pop('email_registro', None)
                return redirect('registro')

    return render(request, 'users/confirmar_email_registro.html', {
        'email': email,
        'error': error,
    })


@csrf_exempt
def registro(request):
    """Paso 3 — Completar los datos de la cuenta (email ya verificado)."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    email_verificado = request.session.get('email_verificado')
    if not email_verificado:
        return redirect('iniciar_registro')

    if request.method == 'POST':
        form = RegistroForm(request.POST, initial={'email': email_verificado})
        # Forzar el email verificado aunque el usuario lo cambie en el POST
        data = request.POST.copy()
        data['email'] = email_verificado
        form = RegistroForm(data)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = email_verificado
            user.is_active = True
            user.save()
            form.save_profile(user)

            request.session.pop('email_verificado', None)

            login(request, user, backend='apps.users.backends.EmailOrUsernameBackend')

            objetivo = form.cleaned_data.get('objetivo', '')
            if objetivo:
                from apps.routines.views import generar_plan_inicial
                generar_plan_inicial(user, objetivo)

            return redirect('bienvenido')
    else:
        form = RegistroForm(initial={'email': email_verificado})

    return render(request, 'users/registro.html', {
        'form': form,
        'email_verificado': email_verificado,
    })


@login_required
def bienvenido(request):
    """Página de bienvenida con los siguientes pasos tras verificar el correo."""
    return render(request, 'users/bienvenido.html')


@csrf_exempt
def login_view(request):
    """Inicio de sesión — acepta usuario o correo."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    identifier = ''

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password   = request.POST.get('password', '')

        user = authenticate(request, username=identifier, password=password)
        if user:
            # Verificar suspensión temporal
            try:
                if user.profile.suspendido_hasta and user.profile.suspendido_hasta > timezone.now():
                    hasta = user.profile.suspendido_hasta.strftime('%d/%m/%Y %H:%M')
                    error = f'Cuenta suspendida hasta el {hasta}.'
                else:
                    login(request, user)
                    return redirect('dashboard')
            except Exception:
                login(request, user)
                return redirect('dashboard')
        else:
            error = 'Usuario/correo o contraseña incorrectos.'

    return render(request, 'users/login.html', {
        'error': error,
        'identifier': identifier,
    })


def logout_view(request):
    """Cerrar sesión."""
    logout(request)
    return redirect('landing')


@login_required
def dashboard(request):
    from apps.routines.models import Rutina, Entrenamiento, SerieEntrenamiento
    from apps.users.models import UserProfile

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    rutinas = Rutina.objects.filter(usuario=request.user).order_by('-creada_en')[:6]

    total_entrenamientos = Entrenamiento.objects.filter(
        usuario=request.user, completado=True
    ).count()
    total_rutinas = Rutina.objects.filter(usuario=request.user).count()
    total_series = SerieEntrenamiento.objects.filter(
        entrenamiento__usuario=request.user, completada=True
    ).count()

    display_name = request.user.first_name or request.user.username

    return render(request, 'users/dashboard.html', {
        'rutinas': rutinas,
        'display_name': display_name,
        'profile': profile,
        'total_entrenamientos': total_entrenamientos,
        'total_rutinas': total_rutinas,
        'total_series': total_series,
    })


@login_required
def perfil(request):
    from apps.routines.models import Rutina, Entrenamiento, SerieEntrenamiento
    from apps.progress.models import RegistroPeso
    from apps.tools.models import CalculoCaloria

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    total_entrenamientos = Entrenamiento.objects.filter(
        usuario=request.user, completado=True
    ).count()
    total_rutinas = Rutina.objects.filter(usuario=request.user).count()
    total_series = SerieEntrenamiento.objects.filter(
        entrenamiento__usuario=request.user, completada=True
    ).count()

    # Kilos totales levantados
    series_con_peso = SerieEntrenamiento.objects.filter(
        entrenamiento__usuario=request.user,
        completada=True,
        peso__isnull=False,
    )
    kg_totales = sum(
        (s.peso or 0) * (s.repeticiones or 1) for s in series_con_peso
    )

    entrenamientos_recientes = Entrenamiento.objects.filter(
        usuario=request.user, completado=True
    ).order_by('-terminado_en')[:5]

    pesos = list(RegistroPeso.objects.filter(
        usuario=request.user
    ).order_by('fecha')[:12])

    try:
        ultimo_calculo = CalculoCaloria.objects.filter(
            usuario=request.user
        ).latest('calculado_en')
    except CalculoCaloria.DoesNotExist:
        ultimo_calculo = None

    # IMC
    imc = imc_categoria = imc_color = None
    if profile.peso and profile.altura:
        h_m = profile.altura / 100
        imc = round(profile.peso / (h_m ** 2), 1)
        if imc < 18.5:
            imc_categoria, imc_color = 'Bajo peso',    '#4361ee'
        elif imc < 25:
            imc_categoria, imc_color = 'Peso normal',  '#00d4aa'
        elif imc < 30:
            imc_categoria, imc_color = 'Sobrepeso',    '#f4a261'
        else:
            imc_categoria, imc_color = 'Obesidad',     '#e63946'

    return render(request, 'users/perfil.html', {
        'profile': profile,
        'total_entrenamientos': total_entrenamientos,
        'total_rutinas': total_rutinas,
        'total_series': total_series,
        'kg_totales': int(kg_totales),
        'entrenamientos_recientes': entrenamientos_recientes,
        'pesos': pesos,
        'ultimo_calculo': ultimo_calculo,
        'imc': imc,
        'imc_categoria': imc_categoria,
        'imc_color': imc_color,
    })


@login_required
def editar_perfil(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        avatar_b64 = request.POST.get('avatar_cropped', '').strip()

        # Guardado rápido de avatar desde la página de perfil (solo foto)
        if (avatar_b64 or 'avatar' in request.FILES) and not request.POST.get('first_name'):
            if avatar_b64 and avatar_b64.startswith('data:image'):
                profile.avatar_data = avatar_b64
                profile.save(update_fields=['avatar_data'])
            elif 'avatar' in request.FILES:
                if profile.avatar:
                    profile.avatar.delete(save=False)
                profile.avatar = request.FILES['avatar']
                profile.save(update_fields=['avatar'])
            messages.success(request, 'Foto de perfil actualizada.')
            return redirect('perfil')

        user_form    = EditarUsuarioForm(request.POST, instance=request.user)
        profile_form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            if avatar_b64 and avatar_b64.startswith('data:image'):
                profile.avatar_data = avatar_b64
                profile.save(update_fields=['avatar_data'])
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')
    else:
        user_form    = EditarUsuarioForm(instance=request.user)
        profile_form = EditarPerfilForm(instance=profile)

    return render(request, 'users/editar_perfil.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
def eliminar_avatar(request):
    if request.method == 'POST':
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
        profile.avatar_data = ''
        profile.save(update_fields=['avatar', 'avatar_data'])
        messages.success(request, 'Foto de perfil eliminada.')
    return redirect('perfil')


# ─────────────────────────────────────────────────────────────────────────────
# VISTAS DE PROFESIONAL
# ─────────────────────────────────────────────────────────────────────────────

def _es_profesional(user):
    if user.is_superuser:
        return True
    try:
        return user.profile.rol in ('profesional', 'admin_pro')
    except Exception:
        return False


def _es_admin_pro(user):
    if user.is_superuser:
        return True
    try:
        return user.profile.rol == 'admin_pro'
    except Exception:
        return False


@login_required
def solicitar_profesional(request):
    """El usuario envía una solicitud para convertirse en profesional."""
    profile = request.user.profile

    # Si ya es profesional o admin_pro, redirigir al dashboard
    if profile.rol in ('profesional', 'admin_pro'):
        return redirect('profesional_dashboard')

    # Si ya tiene solicitud pendiente o aprobada
    solicitud_existente = SolicitudProfesional.objects.filter(
        usuario=request.user
    ).first()

    if request.method == 'POST':
        especialidad = request.POST.get('especialidad', '').strip()
        experiencia  = request.POST.get('experiencia', '').strip()
        motivo       = request.POST.get('motivo', '').strip()

        if not especialidad or not experiencia or not motivo:
            messages.error(request, 'Completa todos los campos de la solicitud.')
            return redirect('solicitar_profesional')

        if solicitud_existente and solicitud_existente.estado == 'pendiente':
            messages.warning(request, 'Ya tienes una solicitud pendiente de revisión.')
            return redirect('solicitar_profesional')

        # Si fue rechazada, permite reenviar
        if solicitud_existente:
            solicitud_existente.especialidad = especialidad
            solicitud_existente.experiencia  = experiencia
            solicitud_existente.motivo       = motivo
            solicitud_existente.estado       = 'pendiente'
            solicitud_existente.nota_admin   = ''
            solicitud_existente.fecha_respuesta = None
            solicitud_existente.revisado_por = None
            solicitud_existente.save()
        else:
            SolicitudProfesional.objects.create(
                usuario=request.user,
                especialidad=especialidad,
                experiencia=experiencia,
                motivo=motivo,
            )

        messages.success(request, 'Solicitud enviada. El Profesional Principal revisará tu perfil en breve.')
        return redirect('solicitar_profesional')

    return render(request, 'users/solicitar_profesional.html', {
        'profile':   profile,
        'solicitud': solicitud_existente,
    })


# ── Admin Pro ──────────────────────────────────────────────────────────────────

@login_required
def admin_pro_dashboard(request):
    """Panel del Profesional Principal — gestiona solicitudes de profesional."""
    if not _es_admin_pro(request.user):
        messages.error(request, 'Acceso restringido al Profesional Principal.')
        return redirect('dashboard')

    pendientes = SolicitudProfesional.objects.filter(
        estado='pendiente'
    ).select_related('usuario', 'usuario__profile').order_by('fecha_envio')

    historial = SolicitudProfesional.objects.exclude(
        estado='pendiente'
    ).select_related('usuario', 'usuario__profile', 'revisado_por').order_by('-fecha_respuesta')[:20]

    todos_profesionales = UserProfile.objects.filter(
        rol='profesional'
    ).select_related('user').order_by('user__date_joined')

    # Todos los usuarios (excluye al propio admin)
    busqueda = request.GET.get('q', '').strip()
    todos_usuarios = UserProfile.objects.exclude(
        user=request.user
    ).select_related('user').order_by('-fecha_registro')

    if busqueda:
        todos_usuarios = todos_usuarios.filter(
            user__username__icontains=busqueda
        ) | todos_usuarios.filter(
            user__first_name__icontains=busqueda
        ) | todos_usuarios.filter(
            user__email__icontains=busqueda
        )
        todos_usuarios = todos_usuarios.distinct()

    return render(request, 'users/admin_pro_dashboard.html', {
        'pendientes':          pendientes,
        'historial':           historial,
        'todos_profesionales': todos_profesionales,
        'total_usuarios':      UserProfile.objects.exclude(user=request.user).count(),
        'todos_usuarios':      todos_usuarios,
        'busqueda':            busqueda,
    })


@login_required
def revisar_solicitud(request, solicitud_id):
    """Admin Pro aprueba o rechaza una solicitud."""
    if not _es_admin_pro(request.user):
        return redirect('dashboard')

    solicitud = get_object_or_404(SolicitudProfesional, id=solicitud_id)

    if request.method == 'POST':
        accion     = request.POST.get('accion')  # 'aprobar' o 'rechazar'
        nota_admin = request.POST.get('nota_admin', '').strip()

        if accion == 'aprobar':
            solicitud.estado       = 'aprobada'
            solicitud.nota_admin   = nota_admin
            solicitud.revisado_por = request.user
            solicitud.fecha_respuesta = timezone.now()
            solicitud.save()

            # Actualizar el perfil del usuario a profesional
            profile = solicitud.usuario.profile
            profile.rol         = 'profesional'
            profile.especialidad = solicitud.especialidad
            if not profile.codigo_pro:
                profile.generar_codigo()
            else:
                profile.save()

            messages.success(request,
                f'✅ {solicitud.usuario.username} ahora es profesional. '
                f'Código generado: {solicitud.usuario.profile.codigo_pro}')

        elif accion == 'rechazar':
            solicitud.estado       = 'rechazada'
            solicitud.nota_admin   = nota_admin or 'Solicitud no aprobada en esta ocasión.'
            solicitud.revisado_por = request.user
            solicitud.fecha_respuesta = timezone.now()
            solicitud.save()
            messages.warning(request, f'Solicitud de {solicitud.usuario.username} rechazada.')

    return redirect('admin_pro_dashboard')


@login_required
def admin_ver_usuario(request, user_id):
    """Admin Pro ve el perfil completo de cualquier usuario."""
    if not _es_admin_pro(request.user):
        return redirect('dashboard')

    cliente = get_object_or_404(User, id=user_id)
    profile = cliente.profile

    from django.db.models import Prefetch
    from apps.routines.models import Entrenamiento, SerieEntrenamiento, Rutina, EjercicioRutina, PlanDia
    from apps.progress.models import MedicionCorporal, RegistroPeso
    from apps.tools.models import PlanNutricional, CalculoCaloria

    # Entrenamientos con sus series prefetcheadas
    entrenamientos = Entrenamiento.objects.filter(
        usuario=cliente, completado=True
    ).prefetch_related(
        Prefetch(
            'series',
            queryset=SerieEntrenamiento.objects.filter(
                completada=True
            ).select_related('ejercicio').order_by('ejercicio__nombre', 'numero_serie'),
        )
    ).order_by('-iniciado_en')[:20]

    # Rutinas del usuario con sus ejercicios
    rutinas = Rutina.objects.filter(usuario=cliente).prefetch_related(
        Prefetch(
            'ejercicios_rutina',
            queryset=EjercicioRutina.objects.select_related(
                'ejercicio', 'ejercicio__grupo_muscular'
            ).order_by('orden'),
        )
    ).order_by('-creada_en')

    # Plan semanal
    ORDEN_DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    plan_semanal_qs = PlanDia.objects.filter(
        usuario=cliente
    ).select_related('rutina').order_by('dia')
    plan_semanal = {p.dia: p for p in plan_semanal_qs}
    plan_ordenado = [
        (dia, plan_semanal.get(dia))
        for dia in ORDEN_DIAS
    ]

    mediciones = MedicionCorporal.objects.filter(
        usuario=cliente
    ).order_by('-fecha')[:12]

    pesos = RegistroPeso.objects.filter(
        usuario=cliente
    ).order_by('-fecha')[:12]

    planes_nutri = PlanNutricional.objects.filter(
        usuario=cliente
    ).order_by('-creado_en')

    calculos_cal = CalculoCaloria.objects.filter(
        usuario=cliente
    ).order_by('-calculado_en')

    # Totales globales
    all_series = SerieEntrenamiento.objects.filter(
        entrenamiento__usuario=cliente, completada=True
    )
    total_series = all_series.count()
    kg_total = sum((s.peso or 0) * (s.repeticiones or 0) for s in all_series)

    LABELS_LIM = {
        'asma': 'Asma / Respiratorio', 'cardiaco': 'Problemas cardíacos',
        'hipertension': 'Hipertensión', 'diabetes': 'Diabetes',
        'lesion_muscular': 'Lesión muscular', 'lesion_rodilla': 'Lesión de rodilla',
        'lesion_espalda': 'Lesión de espalda', 'lesion_hombro': 'Lesión de hombro',
        'articulacion': 'Articulación en riesgo', 'movilidad_reducida': 'Movilidad reducida',
        'embarazo': 'Embarazo / postparto', 'otra': 'Otra condición',
    }

    return render(request, 'users/admin_ver_usuario.html', {
        'cliente':        cliente,
        'profile':        profile,
        'entrenamientos': entrenamientos,
        'rutinas':        rutinas,
        'plan_ordenado':  plan_ordenado,
        'mediciones':     mediciones,
        'pesos':          pesos,
        'planes_nutri':   planes_nutri,
        'calculos_cal':   calculos_cal,
        'condiciones':    [LABELS_LIM.get(k, k) for k in (profile.limitaciones or [])],
        'total_series':   total_series,
        'kg_total':       kg_total,
        'now':            timezone.now(),
    })


@login_required
def admin_crear_rutina(request, user_id):
    """Admin Pro crea una rutina para cualquier usuario."""
    if not _es_admin_pro(request.user):
        return redirect('dashboard')

    from apps.routines.models import Rutina, EjercicioRutina
    from apps.exercises.models import Ejercicio, GrupoMuscular

    cliente = get_object_or_404(User, id=user_id)

    grupos = GrupoMuscular.objects.prefetch_related('ejercicios').order_by('nombre')
    ejercicios = Ejercicio.objects.select_related('grupo_muscular').order_by('grupo_muscular__nombre', 'nombre')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip() or 'Rutina Admin'
        nivel  = request.POST.get('nivel', 'principiante')
        ej_ids = request.POST.getlist('ejercicios')

        if not ej_ids:
            messages.error(request, 'Selecciona al menos un ejercicio.')
        else:
            rutina = Rutina.objects.create(
                usuario=cliente,
                nombre=nombre,
                nivel=nivel,
            )
            for i, ej_id in enumerate(ej_ids):
                try:
                    series = int(request.POST.get(f'series_{ej_id}', 3) or 3)
                    reps   = int(request.POST.get(f'reps_{ej_id}',   12) or 12)
                except (ValueError, TypeError):
                    series, reps = 3, 12
                EjercicioRutina.objects.create(
                    rutina=rutina,
                    ejercicio_id=ej_id,
                    orden=i,
                    series_sugeridas=max(1, min(series, 10)),
                    repeticiones_sugeridas=max(1, min(reps, 50)),
                )
            messages.success(
                request,
                f'Rutina "{nombre}" creada para {cliente.username} con {len(ej_ids)} ejercicios.'
            )
            return redirect('admin_ver_usuario', user_id=user_id)

    return render(request, 'users/admin_crear_rutina.html', {
        'cliente':    cliente,
        'profile':    cliente.profile,
        'grupos':     grupos,
        'ejercicios': ejercicios,
    })


@login_required
def revocar_profesional_admin(request, user_id):
    """Admin Pro revoca el estado de profesional de un usuario."""
    if not _es_admin_pro(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, user_id=user_id)
        nombre = profile.user.username
        profile.rol = 'usuario'
        profile.codigo_pro = ''
        profile.save()
        # Marcar sus relaciones activas como revocadas
        RelacionProfesional.objects.filter(
            profesional=profile.user, estado='activa'
        ).update(estado='revocada')
        messages.success(request, f'Acceso profesional de {nombre} revocado.')

    return redirect('admin_pro_dashboard')


@login_required
def banear_usuario(request, user_id):
    """Banea o desbanea un usuario (activa/desactiva su cuenta)."""
    if not _es_admin_pro(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        if usuario == request.user:
            messages.error(request, 'No puedes banearte a ti mismo.')
            return redirect('admin_ver_usuario', user_id=user_id)
        razon = request.POST.get('razon', '').strip()
        usuario.is_active = not usuario.is_active
        usuario.save()
        usuario.profile.nota_moderacion = razon if not usuario.is_active else ''
        usuario.profile.save(update_fields=['nota_moderacion'])
        accion = 'baneado' if not usuario.is_active else 'desbaneado'
        messages.success(request, f'Usuario {usuario.username} {accion} correctamente.')
    return redirect('admin_ver_usuario', user_id=user_id)


@login_required
def sancionar_usuario(request, user_id):
    """Suspende temporalmente a un usuario por el tiempo indicado."""
    if not _es_admin_pro(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        if usuario == request.user:
            messages.error(request, 'No puedes sancionarte a ti mismo.')
            return redirect('admin_ver_usuario', user_id=user_id)
        try:
            dias  = max(0, int(request.POST.get('dias', 0)))
            horas = max(0, int(request.POST.get('horas', 0)))
        except (ValueError, TypeError):
            dias = horas = 0
        razon = request.POST.get('razon', '').strip()
        if dias == 0 and horas == 0:
            usuario.profile.suspendido_hasta = None
            usuario.profile.nota_moderacion  = ''
            usuario.profile.save(update_fields=['suspendido_hasta', 'nota_moderacion'])
            messages.success(request, f'Sanción de {usuario.username} levantada.')
        else:
            usuario.profile.suspendido_hasta = timezone.now() + timedelta(days=dias, hours=horas)
            usuario.profile.nota_moderacion  = razon
            usuario.profile.save(update_fields=['suspendido_hasta', 'nota_moderacion'])
            messages.success(request, f'{usuario.username} sancionado por {dias}d {horas}h.')
    return redirect('admin_ver_usuario', user_id=user_id)


@login_required
def verificar_password_admin(request):
    """Verifica la contraseña del admin y devuelve datos sensibles."""
    if not _es_admin_pro(request.user):
        return JsonResponse({'ok': False}, status=403)
    if request.method == 'POST':
        password = request.POST.get('password', '')
        user_id  = request.POST.get('user_id', '')
        if authenticate(username=request.user.username, password=password):
            try:
                target = get_object_or_404(User, id=int(user_id))
            except (ValueError, TypeError):
                return JsonResponse({'ok': False, 'error': 'ID inválido'})
            return JsonResponse({
                'ok': True,
                'telefono': target.profile.telefono or '—',
                'direccion': target.profile.direccion or '—',
            })
        return JsonResponse({'ok': False, 'error': 'Contraseña incorrecta'})
    return JsonResponse({'ok': False}, status=405)


@login_required
def activar_profesional(request):
    """Redirige al flujo de solicitud (ya no es auto-activación)."""
    return redirect('solicitar_profesional')


@login_required
def profesional_dashboard(request):
    """Panel principal del profesional — lista de clientes vinculados."""
    if not _es_profesional(request.user):
        messages.error(request, 'No tienes acceso a esta sección.')
        return redirect('dashboard')

    profile = request.user.profile
    if not profile.codigo_pro:
        profile.generar_codigo()

    relaciones = RelacionProfesional.objects.filter(
        profesional=request.user
    ).select_related('usuario', 'usuario__profile').order_by('-fecha_solicitud')

    activas   = relaciones.filter(estado='activa')
    pendientes = relaciones.filter(estado='pendiente')

    return render(request, 'users/profesional_dashboard.html', {
        'profile':    profile,
        'activas':    activas,
        'pendientes': pendientes,
    })


@login_required
def profesional_cliente(request, user_id):
    """Vista detallada de un cliente — solo datos con consentimiento."""
    if not _es_profesional(request.user):
        return redirect('dashboard')

    relacion = get_object_or_404(
        RelacionProfesional,
        profesional=request.user,
        usuario_id=user_id,
        estado='activa',
    )
    cliente = relacion.usuario
    profile = cliente.profile

    ctx = {
        'relacion': relacion,
        'cliente':  cliente,
        'profile':  profile,
    }

    # Datos básicos — siempre visibles si ver_datos_basicos
    if relacion.ver_datos_basicos:
        ctx['datos_basicos'] = {
            'nombre':    cliente.first_name or cliente.username,
            'objetivo':  profile.get_objetivo_display() if profile.objetivo else '—',
            'nivel':     profile.get_nivel_display(),
            'edad':      profile.edad,
            'peso':      profile.peso,
            'altura':    profile.altura,
            'genero':    profile.get_genero_display() if profile.genero else '—',
        }

    # Entrenamientos
    if relacion.ver_entrenamientos:
        from apps.routines.models import Entrenamiento, SerieEntrenamiento
        entrenamientos = Entrenamiento.objects.filter(
            usuario=cliente, completado=True
        ).order_by('-iniciado_en')[:20]
        ctx['entrenamientos'] = entrenamientos

    # Mediciones corporales
    if relacion.ver_mediciones:
        from apps.progress.models import MedicionCorporal
        mediciones = MedicionCorporal.objects.filter(
            usuario=cliente
        ).order_by('-fecha')[:10]
        ctx['mediciones'] = mediciones

    # Nutrición
    if relacion.ver_nutricion:
        from apps.tools.models import PlanNutricional, CalculoCaloria
        plan_activo = PlanNutricional.objects.filter(
            usuario=cliente, activa=True
        ).first()
        calculo_activo = CalculoCaloria.objects.filter(
            usuario=cliente, activa=True
        ).first()
        ctx['plan_nutri']    = plan_activo
        ctx['calculo_cals']  = calculo_activo

    # Condiciones de salud — dato más sensible, requiere consentimiento explícito
    if relacion.ver_salud:
        LABELS = {
            'asma': 'Asma / Respiratorio', 'cardiaco': 'Problemas cardíacos',
            'hipertension': 'Hipertensión', 'diabetes': 'Diabetes',
            'lesion_muscular': 'Lesión muscular', 'lesion_rodilla': 'Lesión de rodilla',
            'lesion_espalda': 'Lesión de espalda', 'lesion_hombro': 'Lesión de hombro',
            'articulacion': 'Articulación en riesgo', 'movilidad_reducida': 'Movilidad reducida',
            'embarazo': 'Embarazo / postparto', 'otra': 'Otra condición',
        }
        ctx['condiciones_salud'] = [
            LABELS.get(k, k) for k in (profile.limitaciones or [])
        ]

    return render(request, 'users/profesional_cliente.html', ctx)


@csrf_exempt
@login_required
def regenerar_codigo(request):
    """Regenera el código de invitación del profesional."""
    if not _es_profesional(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        request.user.profile.generar_codigo()
        messages.success(request, 'Código de invitación regenerado.')
    return redirect('profesional_dashboard')


# ─────────────────────────────────────────────────────────────────────────────
# VISTAS DE PRIVACIDAD (usuario normal)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def privacidad(request):
    """Panel de privacidad del usuario — gestiona conexiones con profesionales."""
    relaciones = RelacionProfesional.objects.filter(
        usuario=request.user
    ).select_related('profesional', 'profesional__profile').order_by('-fecha_solicitud')

    return render(request, 'users/privacidad.html', {
        'relaciones': relaciones,
    })


@login_required
def conectar_profesional(request):
    """El usuario ingresa el código del profesional para vincularse."""
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        try:
            pro_profile = UserProfile.objects.get(
                codigo_pro=codigo, rol='profesional'
            )
        except UserProfile.DoesNotExist:
            messages.error(request, 'Código no encontrado. Verifica con tu profesional.')
            return redirect('privacidad')

        if pro_profile.user == request.user:
            messages.error(request, 'No puedes conectarte contigo mismo.')
            return redirect('privacidad')

        if RelacionProfesional.objects.filter(
            profesional=pro_profile.user, usuario=request.user
        ).exclude(estado='revocada').exists():
            messages.warning(request, 'Ya tienes una conexión activa o pendiente con este profesional.')
            return redirect('privacidad')

        relacion = RelacionProfesional.objects.create(
            profesional=pro_profile.user,
            usuario=request.user,
            estado='activa',
            ver_datos_basicos=True,
            ver_entrenamientos='ver_entrenamientos' in request.POST,
            ver_mediciones='ver_mediciones' in request.POST,
            ver_nutricion='ver_nutricion' in request.POST,
            ver_salud='ver_salud' in request.POST,
            fecha_respuesta=timezone.now(),
        )
        nombre_pro = pro_profile.user.first_name or pro_profile.user.username
        messages.success(request, f'Conectado con {nombre_pro}. Puedes cambiar los permisos en cualquier momento.')
    return redirect('privacidad')


@login_required
def actualizar_permisos(request, relacion_id):
    """El usuario actualiza qué datos puede ver el profesional."""
    relacion = get_object_or_404(
        RelacionProfesional, id=relacion_id, usuario=request.user
    )
    if request.method == 'POST':
        relacion.ver_datos_basicos  = True  # siempre activo
        relacion.ver_entrenamientos = 'ver_entrenamientos' in request.POST
        relacion.ver_mediciones     = 'ver_mediciones' in request.POST
        relacion.ver_nutricion      = 'ver_nutricion' in request.POST
        relacion.ver_salud          = 'ver_salud' in request.POST
        relacion.save()
        messages.success(request, 'Permisos actualizados correctamente.')
    return redirect('privacidad')


@login_required
def revocar_profesional(request, relacion_id):
    """El usuario revoca el acceso del profesional."""
    relacion = get_object_or_404(
        RelacionProfesional, id=relacion_id, usuario=request.user
    )
    if request.method == 'POST':
        relacion.estado = 'revocada'
        relacion.save()
        messages.success(request, 'Acceso revocado. El profesional ya no puede ver tus datos.')
    return redirect('privacidad')


# ─────────────────────────────────────────────────────────────────────────────
# TÉRMINOS Y CONDICIONES
# ─────────────────────────────────────────────────────────────────────────────

def terminos_condiciones(request):
    return render(request, 'users/terminos_condiciones.html')


# ─── Google OAuth ──────────────────────────────────────────────────────────────

import urllib.parse
import secrets
import base64

_GOOGLE_AUTH_URL     = 'https://accounts.google.com/o/oauth2/v2/auth'
_GOOGLE_TOKEN_URL    = 'https://oauth2.googleapis.com/token'
_GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def google_login(request):
    """Redirige al usuario a la pantalla de autorización de Google."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        messages.error(request, 'El login con Google no está configurado todavía.')
        return redirect('login')

    state = secrets.token_urlsafe(32)
    request.session['google_state'] = state

    redirect_uri = settings.FRONTEND_URL.rstrip('/') + '/usuarios/auth/google/callback/'

    params = urllib.parse.urlencode({
        'client_id':     client_id,
        'redirect_uri':  redirect_uri,
        'response_type': 'code',
        'scope':         'openid email profile',
        'state':         state,
        'access_type':   'online',
        'prompt':        'select_account',
    })
    return redirect(f'{_GOOGLE_AUTH_URL}?{params}')


@csrf_exempt
def google_callback(request):
    """Callback que recibe el código de autorización de Google."""
    # Verificar state anti-CSRF
    state = request.GET.get('state', '')
    if state != request.session.get('google_state', ''):
        messages.error(request, 'Error de seguridad en la autenticación. Intenta de nuevo.')
        return redirect('login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google no devolvió autorización.')
        return redirect('login')

    redirect_uri = settings.FRONTEND_URL.rstrip('/') + '/usuarios/auth/google/callback/'

    # Intercambiar code → access_token
    try:
        token_resp = http_requests.post(_GOOGLE_TOKEN_URL, data={
            'code':          code,
            'client_id':     settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri':  redirect_uri,
            'grant_type':    'authorization_code',
        }, timeout=15)
        token_resp.raise_for_status()
        access_token = token_resp.json().get('access_token')
    except Exception:
        messages.error(request, 'Error al conectar con Google. Intenta de nuevo.')
        return redirect('login')

    # Obtener datos del usuario
    try:
        info_resp = http_requests.get(
            _GOOGLE_USERINFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15,
        )
        info_resp.raise_for_status()
        info = info_resp.json()
    except Exception:
        messages.error(request, 'No se pudo obtener información de Google.')
        return redirect('login')

    email      = info.get('email', '').lower()
    name       = info.get('name', '')
    picture    = info.get('picture', '')
    google_id  = info.get('sub', '')

    if not email:
        messages.error(request, 'Google no compartió tu correo electrónico.')
        return redirect('login')

    # Buscar o crear usuario
    user = None
    created = False
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        parts = name.split(' ', 1)
        username = email.split('@')[0]
        base = username
        n = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=parts[0] if parts else '',
            last_name=parts[1] if len(parts) > 1 else '',
        )
        user.set_unusable_password()
        user.save()
        created = True

    # Verificar estado de la cuenta
    if not user.is_active:
        messages.error(request, 'Tu cuenta ha sido baneada. Contacta al administrador.')
        return redirect('login')
    try:
        prof = user.profile
        if prof.suspendido_hasta and prof.suspendido_hasta > timezone.now():
            hasta = prof.suspendido_hasta.strftime('%d/%m/%Y %H:%M')
            messages.error(request, f'Cuenta suspendida hasta el {hasta}.')
            return redirect('login')
        # Usuario existente: guardar avatar si no tiene uno
        if not created and picture and not prof.avatar and not prof.avatar_data:
            try:
                img_resp = http_requests.get(picture, timeout=10)
                if img_resp.ok:
                    b64 = base64.b64encode(img_resp.content).decode()
                    prof.avatar_data = f'data:image/jpeg;base64,{b64}'
                    prof.save(update_fields=['avatar_data'])
            except Exception:
                pass
    except Exception:
        pass

    login(request, user, backend='apps.users.backends.EmailOrUsernameBackend')
    if created:
        request.session['google_picture_url'] = picture
        request.session.save()
        return redirect('completar_perfil_google')
    return redirect('dashboard')


@login_required
def completar_perfil_google(request):
    """Nuevo usuario de Google completa su perfil (objetivo, datos físicos, salud)."""
    # Si el usuario ya tiene perfil completo (acepto_terminos=True), va al dashboard
    try:
        if request.user.profile.acepto_terminos:
            return redirect('dashboard')
    except Exception:
        pass  # Sin perfil todavía → continúa al formulario

    google_picture_url = request.session.get('google_picture_url', '')

    if request.method == 'POST':
        form = CompletarPerfilGoogleForm(request.POST)
        if form.is_valid():
            objetivo = form.cleaned_data.get('objetivo') or ''
            nivel_por_objetivo = {
                'ganar_musculo': 'intermedio',
                'rendimiento':   'avanzado',
            }
            nivel = nivel_por_objetivo.get(objetivo, 'principiante')

            # Guardar nombre en el User
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.save(update_fields=['first_name'])

            # Crear o actualizar perfil
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.edad            = form.cleaned_data.get('edad')
            profile.peso            = form.cleaned_data.get('peso')
            profile.altura          = form.cleaned_data.get('altura')
            profile.genero          = form.cleaned_data.get('genero') or ''
            profile.objetivo        = objetivo
            profile.nivel           = nivel
            profile.limitaciones    = form.cleaned_data.get('limitaciones') or []
            profile.acepto_terminos = form.cleaned_data.get('acepto_terminos', False)

            profile.save()

            request.session.pop('google_picture_url', None)

            try:
                if objetivo:
                    from apps.routines.views import generar_plan_inicial
                    generar_plan_inicial(request.user, objetivo)
            except Exception:
                pass

            return redirect('bienvenido')
    else:
        form = CompletarPerfilGoogleForm(initial={'first_name': request.user.first_name})

    return render(request, 'users/completar_perfil_google.html', {
        'form': form,
        'google_picture_url': google_picture_url,
        'google_email': request.user.email,
    })


