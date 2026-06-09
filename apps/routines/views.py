from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
import json

from .models import Rutina, EjercicioRutina, Entrenamiento, SerieEntrenamiento, PlanDia
from .forms import RutinaForm, SerieForm
from apps.exercises.models import Ejercicio, Equipo, GrupoMuscular


OBJETIVO_CONFIG = {
    'bajar_peso':           {'dias': 4, 'nivel': 'principiante'},
    'mantener_peso':        {'dias': 3, 'nivel': 'principiante'},
    'ganar_musculo':        {'dias': 5, 'nivel': 'intermedio'},
    'mejorar_resistencia':  {'dias': 4, 'nivel': 'principiante'},
    'mejorar_flexibilidad': {'dias': 3, 'nivel': 'principiante'},
    'rendimiento':          {'dias': 5, 'nivel': 'avanzado'},
}

SPLITS = {
    3: [('Empuje',  ['pecho','hombros','triceps']),
        ('Jalón',   ['espalda','biceps','antebrazos']),
        ('Piernas', ['piernas','gluteos','pantorrillas'])],
    4: [('Superior A', ['pecho','hombros','triceps']),
        ('Inferior A', ['piernas','gluteos','pantorrillas']),
        ('Superior B', ['espalda','biceps','antebrazos']),
        ('Inferior B', ['piernas','abdomen','core'])],
    5: [('Pecho & Tríceps', ['pecho','triceps']),
        ('Espalda & Bíceps', ['espalda','biceps']),
        ('Piernas',          ['piernas','gluteos','pantorrillas']),
        ('Hombros & Core',   ['hombros','abdomen','core']),
        ('Full Body',        ['pecho','espalda','piernas','hombros','biceps'])],
}

# ── Adaptaciones por limitación de salud ──────────────────────────────────────

# Grupos musculares a excluir completamente para cada limitación
_LIM_GRUPOS_EXCLUIDOS = {
    'lesion_rodilla':     {'piernas', 'gluteos'},
    'lesion_hombro':      {'hombros'},
    'movilidad_reducida': {'piernas', 'gluteos', 'cardio'},
    'embarazo':           {'cardio', 'abdomen'},
    'asma':               {'cardio'},
    'cardiaco':           {'cardio'},
}

# Grupos a agregar como compensación/reemplazo
_LIM_GRUPOS_EXTRA = {
    'lesion_rodilla':     ['movilidad', 'core', 'antebrazos'],
    'lesion_espalda':     ['movilidad', 'core'],
    'lesion_hombro':      ['movilidad', 'core', 'piernas'],
    'movilidad_reducida': ['movilidad', 'core', 'antebrazos', 'pantorrillas'],
    'embarazo':           ['movilidad', 'pantorrillas'],
    'asma':               ['movilidad'],
    'cardiaco':           ['movilidad'],
    'hipertension':       ['movilidad'],
    'articulacion':       ['movilidad'],
    'diabetes':           ['cardio', 'movilidad'],
    'lesion_muscular':    ['movilidad'],
}

# Palabras clave de nombres de ejercicios a excluir
_LIM_NOMBRES_EXCLUIDOS = {
    'lesion_rodilla': [
        'sentadilla', 'zancada', 'lunge', 'peso muerto', 'prensa', 'step-up',
        'nordic', 'sissy', 'cossack', 'hack squat', 'zercher', 'goblet',
        'bulgarian', 'búlgara', 'sumo', 'femoral',
    ],
    'lesion_espalda': [
        'peso muerto', 'good morning', 'buenos días', 'hiperextensiones',
        'remo con barra', 'rack pull', 'remo pendlay', 'superman',
        'deadlift', 'remo pendlay', 't-bar',
    ],
    'lesion_hombro': [
        'press militar', 'press arnold', 'push press', 'handstand',
        'pike push', 'cuban press', 'fondos', 'dip', 'elevacion',
        'elevaciones', 'encogimiento', 'scaption', 'w raise',
    ],
    'asma': [
        'burpee', 'sprint', 'jump rope', 'box jump', 'tabata',
        'thrusters', 'doble under', 'bear crawl', 'kick boxing',
    ],
    'cardiaco': [
        'burpee', 'sprint', 'box jump', 'jump', 'thruster', 'salto',
        'tabata', 'hiit', 'saltar', 'doble under', 'speed skaters',
        'lateral shuffle',
    ],
    'articulacion': [
        'jump', 'salto', 'burpee', 'box jump', 'sprint', 'pliométric',
        'explosiv', 'saltar',
    ],
    'embarazo': [
        'crunch', 'sit-up', 'russian twist', 'leg raise', 'plancha abdominal',
        'salto', 'jump', 'burpee', 'hollow', 'dragon flag', 'windshield',
        'v-up', 'hanging', 'decline crunch', 'ab wheel',
    ],
    'hipertension': [
        'peso muerto', 'sentadilla con barra', 'press militar', 'rack pull',
    ],
}

# Nivel máximo permitido por limitación
_LIM_NIVEL_MAX = {
    'cardiaco':           'principiante',
    'movilidad_reducida': 'principiante',
    'embarazo':           'principiante',
    'lesion_muscular':    'principiante',
    'lesion_rodilla':     'intermedio',
    'lesion_espalda':     'intermedio',
    'lesion_hombro':      'intermedio',
    'asma':               'intermedio',
    'hipertension':       'intermedio',
    'articulacion':       'intermedio',
}

_NIVEL_ORDEN = {'principiante': 0, 'intermedio': 1, 'avanzado': 2}

# Splits alternativos para limitaciones severas
_SPLITS_ADAPTADOS = {
    'lesion_rodilla': {
        3: [('Tren Superior A',    ['pecho', 'hombros', 'triceps', 'core']),
            ('Tren Superior B',    ['espalda', 'biceps', 'antebrazos', 'pantorrillas']),
            ('Core & Movilidad',   ['movilidad', 'core', 'abdomen'])],
        4: [('Empuje Superior',    ['pecho', 'hombros', 'triceps']),
            ('Jalón Superior',     ['espalda', 'biceps', 'antebrazos']),
            ('Core & Movilidad A', ['movilidad', 'core', 'pantorrillas']),
            ('Core & Movilidad B', ['movilidad', 'abdomen', 'antebrazos'])],
        5: [('Pecho & Tríceps',    ['pecho', 'triceps']),
            ('Espalda & Bíceps',   ['espalda', 'biceps', 'antebrazos']),
            ('Hombros & Core',     ['hombros', 'core', 'abdomen']),
            ('Movilidad & Panto',  ['movilidad', 'pantorrillas']),
            ('Full Superior',      ['pecho', 'espalda', 'hombros', 'biceps'])],
    },
    'movilidad_reducida': {
        3: [('Tren Superior A',  ['pecho', 'biceps', 'antebrazos']),
            ('Tren Superior B',  ['espalda', 'hombros', 'triceps']),
            ('Core & Movilidad', ['movilidad', 'core', 'pantorrillas'])],
        4: [('Empuje Suave',     ['pecho', 'triceps', 'core']),
            ('Jalón Suave',      ['espalda', 'biceps', 'antebrazos']),
            ('Hombros & Movil.', ['hombros', 'movilidad']),
            ('Core & Panto.',    ['core', 'pantorrillas', 'abdomen'])],
        5: [('Pecho & Tríceps',  ['pecho', 'triceps']),
            ('Espalda & Bíceps', ['espalda', 'biceps']),
            ('Hombros & Core',   ['hombros', 'core']),
            ('Antebrazos & Pant',['antebrazos', 'pantorrillas']),
            ('Movilidad Total',  ['movilidad', 'core'])],
    },
    'embarazo': {
        3: [('Movilidad & Bienestar', ['movilidad', 'pantorrillas']),
            ('Tren Superior Suave',   ['espalda', 'biceps', 'antebrazos']),
            ('Cuerpo Suave',          ['movilidad', 'core', 'pantorrillas'])],
        4: [('Movilidad A',      ['movilidad', 'pantorrillas']),
            ('Tren Superior A',  ['pecho', 'biceps', 'antebrazos']),
            ('Movilidad B',      ['movilidad', 'core']),
            ('Tren Superior B',  ['espalda', 'hombros', 'triceps'])],
        5: [('Movilidad A',      ['movilidad']),
            ('Tren Superior A',  ['pecho', 'biceps']),
            ('Movilidad B',      ['movilidad', 'pantorrillas']),
            ('Tren Superior B',  ['espalda', 'antebrazos']),
            ('Core Suave',       ['core', 'hombros'])],
    },
}


def _adaptar_grupos(grupos_slugs: list, limitaciones: list) -> tuple:
    """
    Devuelve (grupos_adaptados, nombres_a_excluir, nivel_max_limitacion).
    Elimina grupos peligrosos, agrega grupos de compensación
    y recopila palabras clave de ejercicios a excluir.
    """
    excluidos = set()
    nombres_excluidos = []
    nivel_max = 'avanzado'

    for lim in limitaciones:
        excluidos |= _LIM_GRUPOS_EXCLUIDOS.get(lim, set())
        nombres_excluidos += _LIM_NOMBRES_EXCLUIDOS.get(lim, [])
        lim_max = _LIM_NIVEL_MAX.get(lim)
        if lim_max and _NIVEL_ORDEN[lim_max] < _NIVEL_ORDEN[nivel_max]:
            nivel_max = lim_max

    grupos = [g for g in grupos_slugs if g not in excluidos]

    extras = set()
    for lim in limitaciones:
        for g in _LIM_GRUPOS_EXTRA.get(lim, []):
            if g not in excluidos:
                extras.add(g)
    for g in extras:
        if g not in grupos:
            grupos.append(g)

    if not grupos:
        grupos = ['movilidad', 'core']

    return grupos, list(set(nombres_excluidos)), nivel_max


def _get_split_adaptado(limitaciones: list, dias: int, split_default: list) -> list:
    """Retorna el split correcto según las limitaciones del usuario."""
    for key in ('embarazo', 'movilidad_reducida', 'lesion_rodilla'):
        if key in limitaciones:
            opciones = _SPLITS_ADAPTADOS.get(key, {})
            if dias in opciones:
                return opciones[dias]
            if opciones:
                closest = min(opciones.keys(), key=lambda x: abs(x - dias))
                return opciones[closest]
    return split_default


def _qs_ejercicios(grupos, nivel, excluir_nombres, equipos_ids=None):
    """Queryset de ejercicios filtrado por grupos, nivel y exclusiones."""
    qs = Ejercicio.objects.filter(
        grupo_muscular__slug__in=grupos,
        nivel=nivel,
    ).distinct()
    if equipos_ids:
        qs = qs.filter(equipos__id__in=equipos_ids).distinct()
    for kw in excluir_nombres:
        qs = qs.exclude(nombre__icontains=kw)
    return qs


def _nivel_ajustado(nivel_base: str, nivel_max_lim: str) -> str:
    """Devuelve el nivel más restrictivo entre el base y el de la limitación."""
    if _NIVEL_ORDEN.get(nivel_max_lim, 99) < _NIVEL_ORDEN.get(nivel_base, 99):
        return nivel_max_lim
    return nivel_base


def _get_limitaciones(user) -> list:
    """Obtiene la lista de limitaciones del perfil del usuario."""
    try:
        return user.profile.limitaciones or []
    except Exception:
        return []


def generar_plan_inicial(user, objetivo):
    """Genera rutinas y plan semanal automáticamente tras el registro."""
    config = OBJETIVO_CONFIG.get(objetivo, {'dias': 3, 'nivel': 'principiante'})
    nivel_base     = config['nivel']
    dias_entreno   = config['dias']
    num_ejercicios = 5
    dias_semana    = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    limitaciones   = _get_limitaciones(user)

    split_default = SPLITS.get(dias_entreno, SPLITS[3])
    sesiones      = _get_split_adaptado(limitaciones, dias_entreno, split_default)

    PlanDia.objects.filter(usuario=user).delete()

    for i, dia in enumerate(dias_semana):
        if i < len(sesiones):
            nombre_sesion, grupos_base = sesiones[i]
            grupos, excluir_nombres, nivel_max = _adaptar_grupos(grupos_base, limitaciones)
            nivel = _nivel_ajustado(nivel_base, nivel_max)

            ejercicios = list(
                _qs_ejercicios(grupos, nivel, excluir_nombres).order_by('?')[:num_ejercicios]
            )
            # fallback: si no hay suficientes con ese nivel, ampliar
            if len(ejercicios) < 3:
                ejercicios = list(
                    _qs_ejercicios(grupos, 'principiante', excluir_nombres).order_by('?')[:num_ejercicios]
                )

            rutina = Rutina.objects.create(
                usuario=user, nombre=nombre_sesion,
                nivel=nivel, es_auto_generada=True
            )
            for j, ej in enumerate(ejercicios):
                EjercicioRutina.objects.create(rutina=rutina, ejercicio=ej, orden=j)
            PlanDia.objects.create(usuario=user, dia=dia, rutina=rutina, descanso=False)
        else:
            PlanDia.objects.create(usuario=user, dia=dia, rutina=None, descanso=True)


# ---- Set filtros desde bottom sheets ----
@login_required
def set_filtros(request):
    grupos = request.GET.get('grupos', None)
    equipos = request.GET.get('equipos', None)
    if grupos is not None:
        request.session['grupos_seleccionados'] = [grupos] if grupos else []
    if equipos is not None:
        request.session['equipos_seleccionados'] = [equipos] if equipos else []
    from django.http import HttpResponse
    return HttpResponse('ok')


# ---- PASO 1: Selección de equipo ----
@login_required
def paso1_equipo(request):
    equipos = Equipo.objects.all()
    if request.method == 'POST':
        seleccionados = request.POST.getlist('equipos')
        request.session['equipos_seleccionados'] = seleccionados
        return redirect('paso2_musculos')
    return render(request, 'routines/paso1_equipo.html', {'equipos': equipos})


# ---- PASO 2: Selección de músculos ----
@login_required
def paso2_musculos(request):
    grupos = GrupoMuscular.objects.all()
    if request.method == 'POST':
        seleccionados = request.POST.getlist('grupos')
        request.session['grupos_seleccionados'] = seleccionados
        return redirect('paso3_ejercicios')
    return render(request, 'routines/paso2_musculos.html', {'grupos': grupos})


# ---- PASO 3: Selección/personalización de ejercicios ----
@login_required
def paso3_ejercicios(request):
    # Cargar todos los ejercicios con equipos y grupo muscular prefetchados
    # El filtrado se hace en el cliente (JavaScript) para respuesta instantánea
    ejercicios = Ejercicio.objects.all().order_by('nombre').prefetch_related('equipos').select_related('grupo_muscular')
    equipos_ids = request.session.get('equipos_seleccionados', [])
    grupos_ids  = request.session.get('grupos_seleccionados', [])

    if request.method == 'POST':
        ejercicios_ids = request.POST.getlist('ejercicios')
        nombre = request.POST.get('nombre', 'Mi Rutina')

        rutina = Rutina.objects.create(
            usuario=request.user,
            nombre=nombre,
        )
        if equipos_ids:
            rutina.equipos.set(equipos_ids)
        if grupos_ids:
            rutina.grupos_musculares.set(grupos_ids)

        for i, ej_id in enumerate(ejercicios_ids):
            EjercicioRutina.objects.create(
                rutina=rutina,
                ejercicio_id=ej_id,
                orden=i
            )

        dia_plan = request.POST.get('dia_plan', '')
        if dia_plan in ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']:
            PlanDia.objects.update_or_create(
                usuario=request.user, dia=dia_plan,
                defaults={'rutina': rutina, 'descanso': False}
            )
            messages.success(request, f'¡Rutina "{nombre}" creada y programada para el {dia_plan.capitalize()}!')
        else:
            messages.success(request, f'¡Rutina "{nombre}" creada!')
        return redirect('iniciar_entrenamiento', rutina_id=rutina.id)

    dias_semana = [
        ('lunes','Lunes'), ('martes','Martes'), ('miercoles','Miércoles'),
        ('jueves','Jueves'), ('viernes','Viernes'), ('sabado','Sábado'), ('domingo','Domingo'),
    ]

    # Ejercicios recientes del usuario (últimas 3 rutinas)
    ids_recientes = (
        EjercicioRutina.objects
        .filter(rutina__usuario=request.user)
        .order_by('-rutina__id')
        .values_list('ejercicio_id', flat=True)[:20]
    )
    recientes = list(dict.fromkeys(ids_recientes))[:6]
    ejercicios_recientes = Ejercicio.objects.filter(id__in=recientes)

    return render(request, 'routines/paso3_ejercicios.html', {
        'ejercicios': ejercicios,
        'ejercicios_recientes': ejercicios_recientes,
        'todos_grupos': GrupoMuscular.objects.all(),
        'todos_equipos': Equipo.objects.all(),
        'grupos_activos': grupos_ids,
        'equipos_activos': equipos_ids,
        'dias_semana': dias_semana,
    })


# ---- Mis rutinas ----
@login_required
def mis_rutinas(request):
    rutinas = Rutina.objects.filter(usuario=request.user)
    return render(request, 'routines/mis_rutinas.html', {'rutinas': rutinas})


# ---- Auto generador ----
@login_required
def auto_generador(request):
    equipos = Equipo.objects.all()

    if request.method == 'POST':
        equipos_ids = request.POST.getlist('equipos')
        nivel = request.POST.get('nivel', 'principiante')
        try:
            num_ejercicios = max(1, int(request.POST.get('num_ejercicios', 5)))
        except (ValueError, TypeError):
            num_ejercicios = 5

        ejercicios_qs = Ejercicio.objects.filter(nivel=nivel)
        if equipos_ids:
            ejercicios_qs = ejercicios_qs.filter(equipos__id__in=equipos_ids).distinct()

        ejercicios_auto = list(ejercicios_qs.order_by('?')[:num_ejercicios])

        rutina = Rutina.objects.create(
            usuario=request.user,
            nombre=f'Rutina Auto - {nivel.capitalize()}',
            nivel=nivel,
            es_auto_generada=True
        )
        if equipos_ids:
            rutina.equipos.set(equipos_ids)

        for i, ej in enumerate(ejercicios_auto):
            EjercicioRutina.objects.create(rutina=rutina, ejercicio=ej, orden=i)

        messages.success(request, '¡Rutina auto-generada!')
        return redirect('iniciar_entrenamiento', rutina_id=rutina.id)

    return render(request, 'routines/auto_generador.html', {'equipos': equipos})


# ---- Entrenamiento activo ----
@login_required
def iniciar_entrenamiento(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id, usuario=request.user)
    ejercicios_rutina = rutina.ejercicios_rutina.select_related('ejercicio').all()

    # Obtener o crear entrenamiento activo
    try:
        entrenamiento, created = Entrenamiento.objects.get_or_create(
            usuario=request.user,
            rutina=rutina,
            completado=False,
            defaults={'nombre': rutina.nombre}
        )
    except Entrenamiento.MultipleObjectsReturned:
        entrenamiento = (
            Entrenamiento.objects.filter(
                usuario=request.user, rutina=rutina, completado=False
            ).latest('iniciado_en')
        )
        created = False

    try:
        ejercicio_idx = int(request.GET.get('ejercicio', 0))
    except (ValueError, TypeError):
        ejercicio_idx = 0
    ejercicios_list = list(ejercicios_rutina)

    if ejercicio_idx >= len(ejercicios_list):
        return redirect('finalizar_entrenamiento', entrenamiento_id=entrenamiento.id)

    ejercicio_actual = ejercicios_list[ejercicio_idx]

    # Series confirmadas de este ejercicio en este entrenamiento
    series = SerieEntrenamiento.objects.filter(
        entrenamiento=entrenamiento,
        ejercicio=ejercicio_actual.ejercicio,
        completada=True,
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'guardar_serie':
            peso_raw = request.POST.get('peso', '').strip()
            reps_raw = request.POST.get('repeticiones', '').strip()
            numero_siguiente = series.count() + 1

            # Reusar la serie autoguardada si existe, si no crear una nueva
            serie, _ = SerieEntrenamiento.objects.get_or_create(
                entrenamiento=entrenamiento,
                ejercicio=ejercicio_actual.ejercicio,
                numero_serie=numero_siguiente,
                defaults={'completada': False}
            )
            try:
                serie.peso = float(peso_raw) if peso_raw else None
            except ValueError:
                serie.peso = None
            try:
                serie.repeticiones = int(reps_raw) if reps_raw else None
            except ValueError:
                serie.repeticiones = None
            serie.completada = True
            serie.save()

            # Si es el último ejercicio, redirigir con flag para mostrar overlay
            if ejercicio_idx == len(ejercicios_list) - 1:
                return redirect(f"{request.path}?ejercicio={ejercicio_idx}&listo=1")
            return redirect(f"{request.path}?ejercicio={ejercicio_idx}")

        elif action == 'eliminar_serie':
            serie_id = request.POST.get('serie_id')
            try:
                serie = SerieEntrenamiento.objects.get(id=serie_id, entrenamiento=entrenamiento)
                serie.delete()
                # Renumerar las series restantes
                series_restantes = SerieEntrenamiento.objects.filter(
                    entrenamiento=entrenamiento,
                    ejercicio=ejercicio_actual.ejercicio,
                    completada=True,
                ).order_by('numero_serie')
                for i, s in enumerate(series_restantes, start=1):
                    if s.numero_serie != i:
                        s.numero_serie = i
                        s.save(update_fields=['numero_serie'])
            except SerieEntrenamiento.DoesNotExist:
                pass
            return redirect(f"{request.path}?ejercicio={ejercicio_idx}")

        elif action == 'actualizar_serie':
            serie_id = request.POST.get('serie_id')
            try:
                serie = SerieEntrenamiento.objects.get(id=serie_id, entrenamiento=entrenamiento)
                peso = request.POST.get('peso', '').strip()
                reps = request.POST.get('repeticiones', '').strip()
                serie.peso = float(peso) if peso else None
                serie.repeticiones = int(reps) if reps else None
                serie.save(update_fields=['peso', 'repeticiones'])
            except (SerieEntrenamiento.DoesNotExist, ValueError):
                pass
            return redirect(f"{request.path}?ejercicio={ejercicio_idx}")

        elif action == 'siguiente_ejercicio':
            next_idx = min(ejercicio_idx + 1, len(ejercicios_list) - 1)
            return redirect(f"{request.path}?ejercicio={next_idx}")

        elif action == 'ir_a_ejercicio':
            try:
                idx = int(request.POST.get('idx', ejercicio_idx))
            except (ValueError, TypeError):
                idx = ejercicio_idx
            idx = max(0, min(idx, len(ejercicios_list) - 1))
            return redirect(f"{request.path}?ejercicio={idx}")

        elif action == 'terminar_entrenamiento':
            return redirect('finalizar_entrenamiento', entrenamiento_id=entrenamiento.id)

        return redirect(f"{request.path}?ejercicio={ejercicio_idx}")

    form = SerieForm()

    # Serie en progreso (autoguardada pero no confirmada aún)
    numero_siguiente = series.count() + 1
    serie_en_progreso = SerieEntrenamiento.objects.filter(
        entrenamiento=entrenamiento,
        ejercicio=ejercicio_actual.ejercicio,
        numero_serie=numero_siguiente,
        completada=False,
    ).first()

    # Última serie completada para pre-rellenar el peso de la nueva fila
    ultima_serie_completada = SerieEntrenamiento.objects.filter(
        entrenamiento=entrenamiento,
        ejercicio=ejercicio_actual.ejercicio,
        completada=True,
    ).order_by('numero_serie').last()

    # Calcular progreso
    total = len(ejercicios_list)
    completados = ejercicio_idx
    progreso_pct = int((completados / total) * 100) if total > 0 else 0

    # Peso total acumulado
    peso_total = sum(
        (s.peso or 0) * (s.repeticiones or 0)
        for s in SerieEntrenamiento.objects.filter(entrenamiento=entrenamiento)
    )

    context = {
        'entrenamiento': entrenamiento,
        'rutina': rutina,
        'ejercicio_actual': ejercicio_actual,
        'ejercicios_list': ejercicios_list,
        'ejercicio_idx': ejercicio_idx,
        'series': series,
        'form': form,
        'progreso_pct': progreso_pct,
        'peso_total': round(peso_total, 1),
        'es_ultimo': ejercicio_idx == len(ejercicios_list) - 1,
        'mostrar_overlay': request.GET.get('listo') == '1' and ejercicio_idx == len(ejercicios_list) - 1,
        'mostrar_descanso': request.GET.get('descanso') == '1',
        'serie_en_progreso': serie_en_progreso,
        'ultima_serie_completada': ultima_serie_completada,
    }
    return render(request, 'routines/entrenamiento_activo.html', context)


@login_required
def finalizar_entrenamiento(request, entrenamiento_id):
    entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id, usuario=request.user)
    entrenamiento.completado = True
    entrenamiento.terminado_en = timezone.now()
    entrenamiento.save()

    series = list(
        SerieEntrenamiento.objects.filter(
            entrenamiento=entrenamiento
        ).select_related('ejercicio__grupo_muscular')
    )
    total_reps = sum(s.repeticiones or 0 for s in series)
    ejercicios_count = len({s.ejercicio_id for s in series})

    muscle_slugs = ','.join(dict.fromkeys(
        s.ejercicio.grupo_muscular.slug
        for s in series
        if s.ejercicio.grupo_muscular_id
    ))

    return render(request, 'routines/entrenamiento_finalizado.html', {
        'entrenamiento': entrenamiento,
        'series': series,
        'total_reps': total_reps,
        'ejercicios_count': ejercicios_count,
        'muscle_slugs': muscle_slugs,
    })


@login_required
def aplicar_plan_recomendado(request):
    """Genera el plan semanal recomendado según el nivel del perfil del usuario."""
    if request.method != 'POST':
        return redirect('plan_semanal')

    from .models import PlanDia
    from apps.users.models import UserProfile

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    nivel = request.POST.get('nivel', 'principiante')

    # Planes recomendados según nivel
    RECOMENDADOS = {
        'principiante': {
            'dias': 3,
            'sesiones': [
                ('Cuerpo Completo A', ['pecho','espalda','piernas','abdomen']),
                ('Cuerpo Completo B', ['hombros','biceps','piernas','pantorrillas']),
                ('Cuerpo Completo C', ['pecho','triceps','piernas','abdomen']),
            ],
            'dias_semana': ['lunes', 'miercoles', 'viernes'],
        },
        'intermedio': {
            'dias': 4,
            'sesiones': [
                ('Superior A — Empuje', ['pecho','hombros','triceps']),
                ('Inferior A',          ['piernas','gluteos','pantorrillas']),
                ('Superior B — Jalón',  ['espalda','biceps','antebrazos']),
                ('Inferior B + Core',   ['piernas','abdomen','gluteos']),
            ],
            'dias_semana': ['lunes', 'martes', 'jueves', 'viernes'],
        },
        'avanzado': {
            'dias': 5,
            'sesiones': [
                ('Pecho & Tríceps',    ['pecho','triceps']),
                ('Espalda & Bíceps',   ['espalda','biceps','antebrazos']),
                ('Piernas & Glúteos',  ['piernas','gluteos','pantorrillas']),
                ('Hombros & Core',     ['hombros','abdomen','core']),
                ('Full Body Potencia', ['pecho','espalda','piernas','hombros']),
            ],
            'dias_semana': ['lunes', 'martes', 'miercoles', 'jueves', 'viernes'],
        },
    }

    plan_config    = RECOMENDADOS.get(nivel, RECOMENDADOS['principiante'])
    num_ejercicios = 5
    limitaciones   = _get_limitaciones(request.user)

    dias_entreno   = plan_config['dias']
    sesiones_base  = plan_config['sesiones']
    sesiones       = _get_split_adaptado(limitaciones, dias_entreno, sesiones_base)
    dias_plan      = plan_config['dias_semana'][:len(sesiones)]

    # Borrar plan anterior
    PlanDia.objects.filter(usuario=request.user).delete()

    dias_todos = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    for dia in dias_todos:
        if dia in dias_plan:
            idx = dias_plan.index(dia)
            nombre_sesion, grupos_base = sesiones[idx]
            grupos, excluir_nombres, nivel_max = _adaptar_grupos(grupos_base, limitaciones)
            nivel_sesion = _nivel_ajustado(nivel, nivel_max)

            ejercicios_qs = _qs_ejercicios(grupos, nivel_sesion, excluir_nombres).order_by('?')[:num_ejercicios]
            if ejercicios_qs.count() < 3:
                ejercicios_qs = _qs_ejercicios(grupos, 'principiante', excluir_nombres).order_by('?')[:num_ejercicios]

            rutina = Rutina.objects.create(
                usuario=request.user,
                nombre=nombre_sesion,
                nivel=nivel_sesion,
                es_auto_generada=True
            )
            for j, ej in enumerate(ejercicios_qs):
                EjercicioRutina.objects.create(rutina=rutina, ejercicio=ej, orden=j)

            PlanDia.objects.create(usuario=request.user, dia=dia, rutina=rutina, descanso=False)
        else:
            PlanDia.objects.create(usuario=request.user, dia=dia, rutina=None, descanso=True)

    label = f'¡Plan recomendado {nivel} aplicado!'
    if limitaciones:
        label += ' (adaptado a tu perfil de salud)'
    messages.success(request, label)
    return redirect('plan_semanal')


@login_required
def generar_plan_auto(request):
    """Genera rutinas automáticas y las asigna al plan semanal."""
    if request.method != 'POST':
        return redirect('plan_semanal')

    from .models import PlanDia

    nivel         = request.POST.get('nivel', 'principiante')
    try:
        dias_entreno   = max(1, min(7, int(request.POST.get('dias_entreno', 3))))
        num_ejercicios = max(1, int(request.POST.get('num_ejercicios', 5)))
    except (ValueError, TypeError):
        dias_entreno, num_ejercicios = 3, 5
    equipos_ids = request.POST.getlist('equipos')

    # Splits según días de entrenamiento
    SPLITS = {
        2: [('Cuerpo Completo A', ['pecho','espalda','piernas','hombros']),
            ('Cuerpo Completo B', ['biceps','triceps','abdomen','piernas','pantorrillas'])],
        3: [('Empuje',  ['pecho','hombros','triceps']),
            ('Jalón',   ['espalda','biceps','antebrazos']),
            ('Piernas', ['piernas','gluteos','pantorrillas'])],
        4: [('Superior A', ['pecho','hombros','triceps']),
            ('Inferior A', ['piernas','gluteos','pantorrillas']),
            ('Superior B', ['espalda','biceps','antebrazos']),
            ('Inferior B', ['piernas','abdomen','core'])],
        5: [('Pecho & Tríceps', ['pecho','triceps']),
            ('Espalda & Bíceps', ['espalda','biceps']),
            ('Piernas',          ['piernas','gluteos','pantorrillas']),
            ('Hombros & Core',   ['hombros','abdomen','core']),
            ('Full Body',        ['pecho','espalda','piernas','hombros','biceps'])],
        6: [('Empuje A',  ['pecho','hombros','triceps']),
            ('Jalón A',   ['espalda','biceps','antebrazos']),
            ('Piernas A', ['piernas','gluteos']),
            ('Empuje B',  ['pecho','hombros','triceps']),
            ('Jalón B',   ['espalda','biceps']),
            ('Piernas B', ['piernas','pantorrillas','abdomen'])],
    }

    dias_semana  = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    limitaciones = _get_limitaciones(request.user)

    split_default = SPLITS.get(dias_entreno, SPLITS[3])
    sesiones      = _get_split_adaptado(limitaciones, dias_entreno, split_default)

    # Borrar plan anterior
    PlanDia.objects.filter(usuario=request.user).delete()

    for i, dia in enumerate(dias_semana):
        if i < len(sesiones):
            nombre_sesion, grupos_base = sesiones[i]
            grupos, excluir_nombres, nivel_max = _adaptar_grupos(grupos_base, limitaciones)
            nivel_sesion = _nivel_ajustado(nivel, nivel_max)

            ejercicios_qs = _qs_ejercicios(grupos, nivel_sesion, excluir_nombres, equipos_ids)
            if ejercicios_qs.count() < 3:
                ejercicios_qs = _qs_ejercicios(grupos, 'principiante', excluir_nombres, equipos_ids)
            ejercicios = list(ejercicios_qs.order_by('?')[:num_ejercicios])

            rutina = Rutina.objects.create(
                usuario=request.user,
                nombre=nombre_sesion,
                nivel=nivel_sesion, es_auto_generada=True
            )
            if equipos_ids:
                rutina.equipos.set(equipos_ids)
            for j, ej in enumerate(ejercicios):
                EjercicioRutina.objects.create(rutina=rutina, ejercicio=ej, orden=j)

            PlanDia.objects.create(usuario=request.user, dia=dia, rutina=rutina, descanso=False)
        else:
            PlanDia.objects.create(usuario=request.user, dia=dia, rutina=None, descanso=True)

    msg = f'¡Plan semanal de {dias_entreno} días generado correctamente!'
    if limitaciones:
        msg += ' Adaptado a tu perfil de salud.'
    messages.success(request, msg)
    return redirect('plan_semanal')


@login_required
def plan_semanal(request):
    from .models import PlanDia
    dias_orden = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    rutinas = Rutina.objects.filter(usuario=request.user)

    if request.method == 'POST':
        for dia in dias_orden:
            rutina_id = request.POST.get(f'rutina_{dia}') or None
            descanso  = request.POST.get(f'descanso_{dia}') == 'on'
            rutina_obj = Rutina.objects.filter(id=rutina_id, usuario=request.user).first() if rutina_id else None
            PlanDia.objects.update_or_create(
                usuario=request.user, dia=dia,
                defaults={'rutina': rutina_obj, 'descanso': descanso}
            )
        return redirect('plan_semanal')

    planes = {p.dia: p for p in PlanDia.objects.filter(usuario=request.user)}
    dias = []
    nombres = {'lunes':'Lunes','martes':'Martes','miercoles':'Miércoles',
               'jueves':'Jueves','viernes':'Viernes','sabado':'Sábado','domingo':'Domingo'}
    for dia in dias_orden:
        plan = planes.get(dia)
        dias.append({
            'key':      dia,
            'nombre':   nombres[dia],
            'rutina':   plan.rutina if plan else None,
            'descanso': plan.descanso if plan else False,
        })

    from apps.users.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Nivel: desde query param (selector), luego perfil, luego default
    nivel_perfil = request.GET.get('nivel') or getattr(profile, 'nivel', None) or 'principiante'
    if nivel_perfil not in ('principiante', 'intermedio', 'avanzado'):
        nivel_perfil = 'principiante'

    PREVIEW = {
        'principiante': {
            'dias': 3, 'descanso': 4,
            'descripcion': 'Full Body 3 días / semana. Ideal para comenzar.',
            'sesiones': [
                ('Lunes',    '💪', 'Cuerpo Completo A'),
                ('Martes',   '😴', 'Descanso'),
                ('Miércoles','💪', 'Cuerpo Completo B'),
                ('Jueves',   '😴', 'Descanso'),
                ('Viernes',  '💪', 'Cuerpo Completo C'),
                ('Sábado',   '😴', 'Descanso'),
                ('Domingo',  '😴', 'Descanso'),
            ],
        },
        'intermedio': {
            'dias': 4, 'descanso': 3,
            'descripcion': 'Upper/Lower split 4 días. Más volumen por grupo.',
            'sesiones': [
                ('Lunes',    '💪', 'Superior A — Empuje'),
                ('Martes',   '💪', 'Inferior A'),
                ('Miércoles','😴', 'Descanso'),
                ('Jueves',   '💪', 'Superior B — Jalón'),
                ('Viernes',  '💪', 'Inferior B + Core'),
                ('Sábado',   '😴', 'Descanso'),
                ('Domingo',  '😴', 'Descanso'),
            ],
        },
        'avanzado': {
            'dias': 5, 'descanso': 2,
            'descripcion': 'PPL + extras 5 días. Alta frecuencia e intensidad.',
            'sesiones': [
                ('Lunes',    '💪', 'Pecho & Tríceps'),
                ('Martes',   '💪', 'Espalda & Bíceps'),
                ('Miércoles','💪', 'Piernas & Glúteos'),
                ('Jueves',   '💪', 'Hombros & Core'),
                ('Viernes',  '💪', 'Full Body Potencia'),
                ('Sábado',   '😴', 'Descanso'),
                ('Domingo',  '😴', 'Descanso'),
            ],
        },
    }

    equipos = Equipo.objects.all()
    nivel_choices = [('principiante','Principiante'),('intermedio','Intermedio'),('avanzado','Avanzado')]

    bienvenida = request.session.pop('plan_bienvenida', False)
    objetivo_label = dict(profile.OBJETIVO_CHOICES).get(profile.objetivo, '') if bienvenida else ''

    # Etiquetas legibles de las limitaciones del usuario
    LABELS_LIMITACIONES = {
        'asma':               'Asma / Respiratorio',
        'cardiaco':           'Problemas cardíacos',
        'hipertension':       'Hipertensión',
        'diabetes':           'Diabetes',
        'lesion_muscular':    'Lesión muscular',
        'lesion_rodilla':     'Lesión de rodilla',
        'lesion_espalda':     'Lesión de espalda',
        'lesion_hombro':      'Lesión de hombro',
        'articulacion':       'Articulación en riesgo',
        'movilidad_reducida': 'Movilidad reducida',
        'embarazo':           'Embarazo / postparto',
        'otra':               'Otra condición',
    }
    limitaciones_usuario = getattr(profile, 'limitaciones', []) or []
    limitaciones_labels  = [LABELS_LIMITACIONES.get(k, k) for k in limitaciones_usuario]

    return render(request, 'routines/plan_semanal.html', {
        'dias': dias, 'rutinas': rutinas,
        'equipos': equipos, 'nivel_choices': nivel_choices,
        'nivel_perfil': nivel_perfil,
        'nivel_preview': PREVIEW[nivel_perfil],
        'preview': PREVIEW,
        'bienvenida': bienvenida,
        'objetivo_label': objetivo_label,
        'display_name': request.user.first_name or request.user.username,
        'limitaciones': limitaciones_usuario,
        'limitaciones_labels': limitaciones_labels,
    })


@login_required
def eliminar_rutina(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id, usuario=request.user)
    if request.method == 'POST':
        rutina.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        messages.success(request, 'Rutina eliminada correctamente.')
    return redirect('mis_rutinas')


@login_required
def descargar_rutina_pdf(request, rutina_id):
    from io import BytesIO
    from pathlib import Path
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image as RLImage,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from django.conf import settings

    rutina = get_object_or_404(Rutina, id=rutina_id, usuario=request.user)
    ejercicios = list(rutina.ejercicios_rutina.select_related(
        'ejercicio', 'ejercicio__grupo_muscular'
    ).order_by('orden'))

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    C = colors.HexColor

    def mk(name, **kw):
        return ParagraphStyle(name, parent=styles['Normal'], **kw)

    story = []

    # ── Encabezado ──────────────────────────────────────
    story.append(Paragraph('SPORTSVISION', mk('brand', fontSize=11, textColor=C('#6b7280'), spaceAfter=2)))
    story.append(Paragraph(rutina.nombre,  mk('tit',   fontSize=22, textColor=C('#00d4aa'), spaceAfter=6)))
    story.append(Paragraph(
        f'Nivel: {rutina.get_nivel_display()}  ·  {len(ejercicios)} ejercicios  ·  '
        f'Creada: {rutina.creada_en.strftime("%d/%m/%Y")}',
        mk('sub', fontSize=10, textColor=C('#6b7280'), spaceAfter=4)))
    if rutina.descripcion:
        story.append(Paragraph(rutina.descripcion, mk('desc', fontSize=9, textColor=C('#9ca3af'))))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=C('#1e293b')))
    story.append(Spacer(1, 0.4*cm))

    # ── Ejercicios con imagen ────────────────────────────
    IMG_SIZE = 2.8 * cm
    static_base = settings.BASE_DIR / 'static'

    name_style  = mk('ename',  fontSize=11, fontName='Helvetica-Bold', textColor=C('#f1f5f9'), spaceAfter=3)
    meta_style  = mk('emeta',  fontSize=8,  textColor=C('#6b7280'))
    instr_style = mk('einstr', fontSize=8,  textColor=C('#94a3b8'), leading=12)

    for er in ejercicios:
        ej = er.ejercicio
        grupo = ej.grupo_muscular.nombre if ej.grupo_muscular else '—'
        reps  = (f'{er.ejercicio.duracion_minutos} min'
                 if ej.duracion_minutos else
                 f'{er.series_sugeridas} series × {er.repeticiones_sugeridas} reps')

        # Intentar cargar la imagen del ejercicio
        img_cell = ''
        if ej.imagen_static:
            img_path = static_base / ej.imagen_static
            if img_path.exists():
                try:
                    img_cell = RLImage(str(img_path), width=IMG_SIZE, height=IMG_SIZE)
                    img_cell.hAlign = 'CENTER'
                except Exception:
                    img_cell = ''

        # Instrucciones (máx. 3 líneas)
        instrucciones = ''
        if ej.instrucciones:
            lineas = [l.strip() for l in ej.instrucciones.split('\n') if l.strip()][:3]
            instrucciones = '\n'.join(f'• {l}' for l in lineas)

        info_cell = [
            Paragraph(f'{er.orden}. {ej.nombre}', name_style),
            Paragraph(f'{grupo}  ·  {reps}', meta_style),
        ]
        if instrucciones:
            info_cell.append(Spacer(1, 2))
            info_cell.append(Paragraph(instrucciones, instr_style))

        row = [[img_cell, info_cell]]
        tbl = Table(row, colWidths=[IMG_SIZE + 0.4*cm, None])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, -1), C('#111827')),
            ('BOX',          (0, 0), (-1, -1), 0.5, C('#1e293b')),
            ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING',   (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
            ('LEFTPADDING',  (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN',        (0, 0), (0, -1),  'CENTER'),
            ('VALIGN',       (0, 0), (0, -1),  'MIDDLE'),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.25*cm))

    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(
        f'Generado por SportsVision · {timezone.now().strftime("%d/%m/%Y %H:%M")}',
        ParagraphStyle('Footer', parent=styles['Normal'],
                       fontSize=7, textColor=colors.HexColor('#4b5563'), alignment=TA_CENTER)))

    doc.build(story)
    buf.seek(0)
    filename = rutina.nombre.replace(' ', '_').lower()
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rutina_{filename}.pdf"'
    return response


@login_required
def autoguardar_serie(request, entrenamiento_id):
    """
    Endpoint AJAX para guardar o actualizar la serie en progreso
    sin que el usuario tenga que presionar ningún botón.
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id, usuario=request.user)
    ejercicio_id  = data.get('ejercicio_id')
    numero_serie  = data.get('numero_serie', 1)
    peso          = data.get('peso')
    repeticiones  = data.get('repeticiones')

    if not ejercicio_id:
        return JsonResponse({'ok': False, 'error': 'Falta ejercicio_id'}, status=400)

    ejercicio = get_object_or_404(Ejercicio, id=ejercicio_id)

    # Buscar si ya existe esta serie (mismo entrenamiento + ejercicio + número)
    serie, created = SerieEntrenamiento.objects.get_or_create(
        entrenamiento=entrenamiento,
        ejercicio=ejercicio,
        numero_serie=numero_serie,
        defaults={'completada': False}
    )

    # Actualizar valores solo si vienen en el payload
    if peso is not None:
        try:
            serie.peso = float(peso) if str(peso).strip() != '' else None
        except (ValueError, TypeError):
            serie.peso = None

    if repeticiones is not None:
        try:
            serie.repeticiones = int(repeticiones) if str(repeticiones).strip() != '' else None
        except (ValueError, TypeError):
            serie.repeticiones = None

    serie.save(update_fields=['peso', 'repeticiones'])

    return JsonResponse({
        'ok': True,
        'created': created,
        'serie_id': serie.id,
        'peso': serie.peso,
        'repeticiones': serie.repeticiones,
    })
