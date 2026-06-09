from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ejercicio, GrupoMuscular, Equipo


@login_required
def lista_ejercicios(request):
    ejercicios = Ejercicio.objects.all().select_related('grupo_muscular')
    grupos = GrupoMuscular.objects.all()
    equipos = Equipo.objects.all()

    # Filtros
    grupo_id = request.GET.get('grupo')
    equipo_id = request.GET.get('equipo')
    nivel = request.GET.get('nivel')

    if grupo_id:
        ejercicios = ejercicios.filter(grupo_muscular_id=grupo_id)
    if equipo_id:
        ejercicios = ejercicios.filter(equipos__id=equipo_id)
    if nivel:
        ejercicios = ejercicios.filter(nivel=nivel)

    return render(request, 'exercises/lista.html', {
        'ejercicios': ejercicios,
        'grupos': grupos,
        'equipos': equipos,
    })


@login_required
def detalle_ejercicio(request, pk):
    ejercicio = get_object_or_404(Ejercicio, pk=pk)
    return render(request, 'exercises/detalle.html', {'ejercicio': ejercicio})
