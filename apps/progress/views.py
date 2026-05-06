from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import date

from apps.routines.models import Entrenamiento, PlanDia
from apps.tools.models import CalculoCaloria
from .models import RegistroPeso, AnotacionCalendario, MedicionCorporal


@login_required
def calendario_progreso(request):
    """Calendario con historial de entrenamientos."""
    import calendar as cal_module

    year  = int(request.GET.get('year',  timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))

    meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
             'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

    # Entrenamientos del mes
    entrenamientos = Entrenamiento.objects.filter(
        usuario=request.user,
        iniciado_en__year=year,
        iniciado_en__month=month,
        completado=True
    )

    dias_con_entrenamiento = {}
    resumen_dias = {}
    for e in entrenamientos:
        dia = e.iniciado_en.day
        if dia not in dias_con_entrenamiento:
            dias_con_entrenamiento[dia] = []
        dias_con_entrenamiento[dia].append(e)

    for dia, ents in dias_con_entrenamiento.items():
        first = ents[0]
        nombre = (first.rutina.nombre if first.rutina else None) or first.nombre or 'Entrenamiento'
        total_series = sum(e.series.count() for e in ents)
        total_kg = round(sum(
            (s.peso or 0) * (s.repeticiones or 0)
            for e in ents for s in e.series.all()
        ), 1)
        resumen_dias[dia] = {'nombre': nombre, 'series': total_series, 'kg': total_kg}

    # Anotaciones del mes (descanso / planeado) desde la BD
    anotaciones_qs = AnotacionCalendario.objects.filter(
        usuario=request.user,
        fecha__year=year,
        fecha__month=month,
    )
    anotaciones = {a.fecha.day: a.tipo for a in anotaciones_qs}

    # Plan semanal → mapeo weekday (0=lun..6=dom) → info rutina
    DIAS_KEY = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    planes_dia = PlanDia.objects.filter(usuario=request.user).select_related('rutina')
    plan_por_weekday = {}  # {0: {nombre, descanso, rutina_obj}, ...}
    for p in planes_dia:
        idx = DIAS_KEY.index(p.dia)
        plan_por_weekday[idx] = {
            'nombre':     p.rutina.nombre if p.rutina and not p.descanso else None,
            'descanso':   p.descanso,
            'rutina_obj': p.rutina if not p.descanso else None,
        }

    # Plan nutricional (último cálculo del usuario)
    plan_nutri = CalculoCaloria.objects.filter(usuario=request.user).order_by('-calculado_en').first()

    # Navegación
    prev_month, prev_year = (12, year-1) if month == 1  else (month-1, year)
    next_month, next_year = (1,  year+1) if month == 12 else (month+1, year)

    # Detalle del día seleccionado
    dia_sel = int(request.GET.get('dia', 0))
    entrenamientos_dia = []
    plan_dia_sel = None
    if dia_sel:
        entrenamientos_dia = Entrenamiento.objects.filter(
            usuario=request.user,
            iniciado_en__year=year,
            iniciado_en__month=month,
            iniciado_en__day=dia_sel,
        ).prefetch_related('series__ejercicio')

        # Obtener el plan para ese día de la semana
        weekday = date(year, month, dia_sel).weekday()  # 0=lun..6=dom
        plan_dia_sel = plan_por_weekday.get(weekday)

    # Para cada día del calendario, calcular el weekday
    cal_data = cal_module.monthcalendar(year, month)
    import datetime
    # Enriquecer cada celda con el día de la semana y el plan
    celdas_plan = {}  # {day_num: {plan_rutina, plan_descanso}}
    for week in cal_data:
        for weekday_idx, day in enumerate(week):
            if day > 0:
                celdas_plan[day] = plan_por_weekday.get(weekday_idx, {})

    return render(request, 'progress/calendario.html', {
        'calendario':             cal_data,
        'year': year, 'month': month,
        'mes_nombre':             meses[month - 1],
        'dias_con_entrenamiento': dias_con_entrenamiento,
        'resumen_dias':           resumen_dias,
        'anotaciones':            anotaciones,
        'celdas_plan':            celdas_plan,
        'plan_nutri':             plan_nutri,
        'prev_month': prev_month, 'prev_year': prev_year,
        'next_month': next_month, 'next_year': next_year,
        'dia_sel':                dia_sel,
        'entrenamientos_dia':     entrenamientos_dia,
        'plan_dia_sel':           plan_dia_sel,
    })


@login_required
def anotar_dia(request):
    """Guarda o elimina una anotación (descanso/planeado) para un día."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    import json
    data  = json.loads(request.body)
    year  = int(data.get('year'))
    month = int(data.get('month'))
    day   = int(data.get('day'))
    tipo  = data.get('tipo', '')  # 'descanso' | 'planeado' | '' (borrar)

    fecha = date(year, month, day)

    if tipo in ('descanso', 'planeado'):
        AnotacionCalendario.objects.update_or_create(
            usuario=request.user, fecha=fecha,
            defaults={'tipo': tipo}
        )
    else:
        AnotacionCalendario.objects.filter(usuario=request.user, fecha=fecha).delete()

    return JsonResponse({'ok': True, 'tipo': tipo})
