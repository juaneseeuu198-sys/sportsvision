from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

from apps.routines.models import Entrenamiento, SerieEntrenamiento
from .models import RegistroPeso


@login_required
def calendario_progreso(request):
    """Calendario con historial de entrenamientos."""
    import calendar
    from datetime import date

    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    # Construir días del mes
    cal = calendar.monthcalendar(year, month)
    meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
             'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    # Entrenamientos del mes
    entrenamientos = Entrenamiento.objects.filter(
        usuario=request.user,
        iniciado_en__year=year,
        iniciado_en__month=month,
        completado=True
    )

    # Mapear día -> entrenamientos
    dias_con_entrenamiento = {}
    for e in entrenamientos:
        dia = e.iniciado_en.day
        if dia not in dias_con_entrenamiento:
            dias_con_entrenamiento[dia] = []
        dias_con_entrenamiento[dia].append(e)

    # Navegación
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # Detalle del día seleccionado
    dia_sel = int(request.GET.get('dia', 0))
    entrenamientos_dia = []
    if dia_sel:
        entrenamientos_dia = Entrenamiento.objects.filter(
            usuario=request.user,
            iniciado_en__year=year,
            iniciado_en__month=month,
            iniciado_en__day=dia_sel,
        ).prefetch_related('series__ejercicio')

    context = {
        'calendario': cal,
        'year': year,
        'month': month,
        'mes_nombre': meses[month - 1],
        'dias_con_entrenamiento': dias_con_entrenamiento,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'dia_sel': dia_sel,
        'entrenamientos_dia': entrenamientos_dia,
    }
    return render(request, 'progress/calendario.html', context)
