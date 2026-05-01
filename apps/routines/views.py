from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import json

from .models import Rutina, EjercicioRutina, Entrenamiento, SerieEntrenamiento
from .forms import RutinaForm, SerieForm
from apps.exercises.models import Ejercicio, Equipo, GrupoMuscular


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
    equipos_ids = request.session.get('equipos_seleccionados', [])
    grupos_ids = request.session.get('grupos_seleccionados', [])

    ejercicios = Ejercicio.objects.all()
    if equipos_ids:
        ejercicios = ejercicios.filter(equipos__id__in=equipos_ids).distinct()
    if grupos_ids:
        ejercicios = ejercicios.filter(grupo_muscular__id__in=grupos_ids).distinct()

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

        messages.success(request, f'¡Rutina "{nombre}" creada!')
        return redirect('iniciar_entrenamiento', rutina_id=rutina.id)

    return render(request, 'routines/paso3_ejercicios.html', {'ejercicios': ejercicios})


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
        num_ejercicios = int(request.POST.get('num_ejercicios', 5))

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
    entrenamiento, created = Entrenamiento.objects.get_or_create(
        usuario=request.user,
        rutina=rutina,
        completado=False,
        defaults={'nombre': rutina.nombre}
    )

    ejercicio_idx = int(request.GET.get('ejercicio', 0))
    ejercicios_list = list(ejercicios_rutina)

    if ejercicio_idx >= len(ejercicios_list):
        return redirect('finalizar_entrenamiento', entrenamiento_id=entrenamiento.id)

    ejercicio_actual = ejercicios_list[ejercicio_idx]

    # Series existentes de este ejercicio en este entrenamiento
    series = SerieEntrenamiento.objects.filter(
        entrenamiento=entrenamiento,
        ejercicio=ejercicio_actual.ejercicio
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'guardar_serie':
            form = SerieForm(request.POST)
            if form.is_valid():
                serie = form.save(commit=False)
                serie.entrenamiento = entrenamiento
                serie.ejercicio = ejercicio_actual.ejercicio
                serie.numero_serie = series.count() + 1
                serie.completada = True
                serie.save()

        elif action == 'siguiente_ejercicio':
            return redirect(f"{request.path}?ejercicio={ejercicio_idx + 1}")

        elif action == 'terminar_entrenamiento':
            return redirect('finalizar_entrenamiento', entrenamiento_id=entrenamiento.id)

        return redirect(f"{request.path}?ejercicio={ejercicio_idx}")

    form = SerieForm()

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
    }
    return render(request, 'routines/entrenamiento_activo.html', context)


@login_required
def finalizar_entrenamiento(request, entrenamiento_id):
    entrenamiento = get_object_or_404(Entrenamiento, id=entrenamiento_id, usuario=request.user)
    entrenamiento.completado = True
    entrenamiento.terminado_en = timezone.now()
    entrenamiento.save()

    series = SerieEntrenamiento.objects.filter(entrenamiento=entrenamiento).select_related('ejercicio')
    return render(request, 'routines/entrenamiento_finalizado.html', {
        'entrenamiento': entrenamiento,
        'series': series,
    })


@login_required
def eliminar_rutina(request, rutina_id):
    from django.contrib import messages
    rutina = get_object_or_404(Rutina, id=rutina_id, usuario=request.user)
    rutina.delete()
    messages.success(request, 'Rutina eliminada correctamente.')
    return redirect('dashboard')
