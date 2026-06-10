from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta

from django.conf import settings
from django.db.models import F, Sum, FloatField, ExpressionWrapper, Value, Count, Q
from django.db.models.functions import Coalesce
import requests as http_requests

from apps.routines.models import Entrenamiento, PlanDia
from apps.tools.models import CalculoCaloria
from .models import RegistroPeso, AnotacionCalendario, MedicionCorporal


# ─── Google Calendar helpers ───────────────────────────────────────────────────

_GCAL_EVENTS_URL  = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
_GCAL_TOKEN_URL   = 'https://oauth2.googleapis.com/token'

_TIPO_COLORES = {
    'descanso': ('5', '😴 Descanso — SportsVision'),      # banana
    'planeado': ('9', '📋 Entrenamiento — SportsVision'),  # blueberry
}


def _gcal_token(user):
    """Devuelve un access_token válido refrescando si es necesario. None si no conectado."""
    try:
        gcal = user.gcal_token
    except Exception:
        return None

    if timezone.now() >= gcal.token_expiry - timedelta(minutes=5):
        try:
            resp = http_requests.post(_GCAL_TOKEN_URL, data={
                'client_id':     settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'refresh_token': gcal.refresh_token,
                'grant_type':    'refresh_token',
            }, timeout=10)
            data = resp.json()
            gcal.access_token = data['access_token']
            gcal.token_expiry = timezone.now() + timedelta(seconds=data.get('expires_in', 3600))
            gcal.save(update_fields=['access_token', 'token_expiry'])
        except Exception:
            return None

    return gcal.access_token


def _gcal_create(access_token, fecha, tipo, nombre_rutina=None):
    """Crea un evento de día completo en Google Calendar. Devuelve (event_id, error_msg)."""
    color_id, default_title = _TIPO_COLORES.get(tipo, ('1', 'SportsVision'))
    title = default_title
    if tipo == 'planeado' and nombre_rutina:
        title = f'📋 {nombre_rutina} — SportsVision'

    end_date = (fecha + timedelta(days=1)).isoformat()
    try:
        resp = http_requests.post(
            _GCAL_EVENTS_URL,
            headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
            json={
                'summary':     title,
                'start':       {'date': fecha.isoformat()},
                'end':         {'date': end_date},
                'colorId':     color_id,
                'description': 'Marcado desde SportsVision',
            },
            timeout=10,
        )
        data = resp.json()
        if resp.status_code == 200 or resp.status_code == 201:
            return data.get('id', ''), ''
        return '', str(data)
    except Exception as e:
        return '', str(e)


def _gcal_delete(access_token, event_id):
    """Elimina un evento de Google Calendar por ID."""
    if not event_id:
        return
    try:
        http_requests.delete(
            f'{_GCAL_EVENTS_URL}/{event_id}',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
    except Exception:
        pass


# ─── Vistas ────────────────────────────────────────────────────────────────────

@login_required
def calendario_progreso(request):
    """Calendario con historial de entrenamientos."""
    import calendar as cal_module

    now = timezone.now()
    try:
        year  = int(request.GET.get('year',  now.year))
        month = int(request.GET.get('month', now.month))
    except (ValueError, TypeError):
        year, month = now.year, now.month
    month = max(1, min(12, month))

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
    plan_por_weekday = {}
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
    try:
        dia_sel = int(request.GET.get('dia', 0))
    except (ValueError, TypeError):
        dia_sel = 0
    entrenamientos_dia = []
    plan_dia_sel = None
    if dia_sel:
        entrenamientos_dia = Entrenamiento.objects.filter(
            usuario=request.user,
            iniciado_en__year=year,
            iniciado_en__month=month,
            iniciado_en__day=dia_sel,
        ).prefetch_related('series__ejercicio')

        weekday = date(year, month, dia_sel).weekday()
        plan_dia_sel = plan_por_weekday.get(weekday)

    # Para cada día del calendario, calcular el weekday
    cal_data = cal_module.monthcalendar(year, month)
    celdas_plan = {}
    for week in cal_data:
        for weekday_idx, day in enumerate(week):
            if day > 0:
                celdas_plan[day] = plan_por_weekday.get(weekday_idx, {})

    # Estado de conexión con Google Calendar
    gcal_conectado = hasattr(request.user, 'gcal_token')

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
        'gcal_conectado':         gcal_conectado,
    })


@login_required
def anotar_dia(request):
    """Guarda o elimina una anotación (descanso/planeado) para un día y sincroniza con Google Calendar."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'invalid json'}, status=400)
    try:
        year  = int(data.get('year'))
        month = int(data.get('month'))
        day   = int(data.get('day'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'invalid date'}, status=400)
    tipo = data.get('tipo', '')  # 'descanso' | 'planeado' | '' (borrar)

    fecha = date(year, month, day)
    access_token = _gcal_token(request.user)

    if tipo in ('descanso', 'planeado'):
        existing = AnotacionCalendario.objects.filter(usuario=request.user, fecha=fecha).first()

        # Borrar evento anterior en Google Calendar si existía
        if access_token and existing and existing.gcal_event_id:
            _gcal_delete(access_token, existing.gcal_event_id)

        # Nombre de la rutina para días de trabajo
        nombre_rutina = None
        if tipo == 'planeado':
            DIAS_KEY = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
            plan = PlanDia.objects.filter(
                usuario=request.user, dia=DIAS_KEY[fecha.weekday()]
            ).select_related('rutina').first()
            if plan and plan.rutina and not plan.descanso:
                nombre_rutina = plan.rutina.nombre

        gcal_event_id = ''
        if access_token:
            gcal_event_id, _ = _gcal_create(access_token, fecha, tipo, nombre_rutina)

        AnotacionCalendario.objects.update_or_create(
            usuario=request.user, fecha=fecha,
            defaults={'tipo': tipo, 'gcal_event_id': gcal_event_id}
        )
    else:
        existing = AnotacionCalendario.objects.filter(usuario=request.user, fecha=fecha).first()
        if access_token and existing and existing.gcal_event_id:
            _gcal_delete(access_token, existing.gcal_event_id)
        AnotacionCalendario.objects.filter(usuario=request.user, fecha=fecha).delete()

    return JsonResponse({'ok': True, 'tipo': tipo, 'gcal': bool(access_token)})


@login_required
def gcal_sync_all(request):
    """Sube el Plan Semanal a Google Calendar para los próximos 90 días."""
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    access_token = _gcal_token(request.user)
    if not access_token:
        return JsonResponse({'error': 'no_gcal'}, status=403)

    DIAS_KEY = ['lunes','martes','miercoles','jueves','viernes','sabado','domingo']
    planes_dia = PlanDia.objects.filter(usuario=request.user).select_related('rutina')
    plan_por_weekday = {}
    for p in planes_dia:
        idx = DIAS_KEY.index(p.dia)
        plan_por_weekday[idx] = p

    if not plan_por_weekday:
        return JsonResponse({'ok': True, 'creados': 0, 'error': 'No tienes un Plan Semanal configurado. Ve a Rutinas → Plan Semanal primero.'})

    hoy = date.today()
    fin  = hoy + timedelta(days=90)
    creados = 0
    ultimo_error = ''

    current = hoy
    while current <= fin:
        plan = plan_por_weekday.get(current.weekday())
        if plan:
            if plan.descanso:
                tipo, nombre = 'descanso', None
            elif plan.rutina:
                tipo, nombre = 'planeado', plan.rutina.nombre
            else:
                current += timedelta(days=1)
                continue

            event_id, err = _gcal_create(access_token, current, tipo, nombre)
            if event_id:
                creados += 1
            elif err:
                ultimo_error = err
                break
        current += timedelta(days=1)

    return JsonResponse({'ok': True, 'creados': creados, 'error': ultimo_error})
