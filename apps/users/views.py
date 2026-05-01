from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, LoginForm, EditarUsuarioForm, EditarPerfilForm
from .models import UserProfile


def landing(request):
    """Página de inicio / landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/landing.html')


def auth_choice(request):
    """Pantalla de elección: Login o Registro."""
    return render(request, 'users/auth_choice.html')


def registro(request):
    """Registro de nuevo usuario."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user,
                  backend='apps.users.backends.EmailOrUsernameBackend')
            return redirect('dashboard')
    else:
        form = RegistroForm()

    return render(request, 'users/registro.html', {'form': form})


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
    except Exception:
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
        user_form    = EditarUsuarioForm(request.POST, instance=request.user)
        profile_form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
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
