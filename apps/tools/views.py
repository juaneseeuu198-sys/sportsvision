from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .forms import CaloriasForm, IMCForm, PlanNutricionalForm
from .models import CalculoCaloria, PlanNutricional


# ─── Calorie Calculator ────────────────────────────────────────────────────────

@login_required
def calculadora_calorias(request):
    resultado = None
    form = CaloriasForm()

    if request.method == 'POST':
        form = CaloriasForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            genero = d['genero']
            edad   = d['edad']
            peso   = d['peso']
            altura = d['altura']

            # Mifflin-St Jeor
            if genero == 'M':
                tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
            else:
                tmb = 10 * peso + 6.25 * altura - 5 * edad - 161

            factores = {
                'sedentario': 1.2,
                'poca': 1.375,
                'activo': 1.55,
                'diario': 1.725,
                'extra': 1.9,
            }
            getd = tmb * factores[d['nivel_actividad']]

            ajuste = {
                'perder_rapido': -0.20,
                'perder': -0.10,
                'mantener': 0,
                'ganar': 0.10,
                'ganar_rapido': 0.20,
            }
            calorias = getd * (1 + ajuste[d['objetivo']])

            resultado = {
                'genero': genero,
                'edad': edad, 'peso': peso, 'altura': altura,
                'nivel_actividad': d['nivel_actividad'],
                'objetivo': d['objetivo'],
                'tmb': tmb,
                'getd': getd,
                'proteinas_g': round(calorias * 0.30 / 4, 1),
                'carbos_g':    round(calorias * 0.45 / 4, 1),
                'grasas_g':    round(calorias * 0.25 / 9, 1),
            }

    dietas = CalculoCaloria.objects.filter(usuario=request.user) if request.user.is_authenticated else []
    return render(request, 'tools/calculadora_calorias.html', {
        'form': form,
        'resultado': resultado,
        'dietas_count': len(list(dietas)),
    })


# ─── IMC Calculator ────────────────────────────────────────────────────────────

@login_required
def calculadora_imc(request):
    resultado = None
    form = IMCForm()

    if request.method == 'POST':
        form = IMCForm(request.POST)
        if form.is_valid():
            try:
                peso   = form.cleaned_data['peso']
                altura = form.cleaned_data['altura'] / 100  # cm → m

                if peso > 0 and altura > 0:
                    imc = peso / (altura ** 2)

                    if imc < 16:
                        categoria, color, riesgo = 'Delgadez Severa',   'danger', 'Muy Alto'
                    elif imc < 17:
                        categoria, color, riesgo = 'Delgadez Moderada', 'danger', 'Alto'
                    elif imc < 18.5:
                        categoria, color, riesgo = 'Delgadez Leve',     'warning', 'Moderado'
                    elif imc < 25:
                        categoria, color, riesgo = 'Peso Normal',       'success', 'Bajo'
                    elif imc < 30:
                        categoria, color, riesgo = 'Sobrepeso',         'warning', 'Moderado'
                    elif imc < 35:
                        categoria, color, riesgo = 'Obesidad Clase 1',  'danger', 'Alto'
                    elif imc < 40:
                        categoria, color, riesgo = 'Obesidad Clase 2',  'danger', 'Muy Alto'
                    else:
                        categoria, color, riesgo = 'Obesidad Clase 3',  'danger', 'Extremo'

                    altura_m = form.cleaned_data['altura'] / 100
                    peso_min = round(18.5 * (altura_m ** 2), 1)
                    peso_max = round(24.9 * (altura_m ** 2), 1)

                    if imc < 18.5:
                        cambiar = f'+ {round(peso_min - peso, 1)} kg'
                    elif imc > 25:
                        cambiar = f'- {round(peso - peso_max, 1)} kg'
                    else:
                        cambiar = 'Mantener peso actual'

                    resultado = {
                        'imc':      round(imc, 1),
                        'categoria': categoria,
                        'color':    color,
                        'riesgo':   riesgo,
                        'peso_min': peso_min,
                        'peso_max': peso_max,
                        'cambiar':  cambiar,
                        'peso':     peso,
                        'altura':   int(form.cleaned_data['altura']),
                    }
            except (ValueError, ZeroDivisionError):
                pass

    return render(request, 'tools/calculadora_imc.html', {
        'form': form,
        'resultado': resultado,
    })


# ─── Nutritional Plan ──────────────────────────────────────────────────────────

ALIMENTOS = {
    'proteinas': {
        'ninguna':     [('Pechuga de pollo', 31, 0, 3.6, 165),
                        ('Huevo entero', 13, 1.1, 11, 155),
                        ('Atún en agua', 29, 0, 1, 128),
                        ('Carne de res magra', 26, 0, 7, 175),
                        ('Salmón', 20, 0, 13, 208),
                        ('Claras de huevo', 11, 0.7, 0.2, 52)],
        'vegetariano': [('Huevo entero', 13, 1.1, 11, 155),
                        ('Queso cottage', 11, 3.4, 4.3, 98),
                        ('Yogur griego', 10, 3.6, 0.4, 59),
                        ('Tofu firme', 8, 2, 4.8, 76),
                        ('Claras de huevo', 11, 0.7, 0.2, 52)],
        'vegano':      [('Tofu firme', 8, 2, 4.8, 76),
                        ('Tempeh', 19, 9, 11, 195),
                        ('Edamame', 11, 8.9, 5.2, 121),
                        ('Lentejas cocidas', 9, 20, 0.4, 116),
                        ('Garbanzos cocidos', 9, 27, 2.6, 164)],
        'sin_gluten':  [('Pechuga de pollo', 31, 0, 3.6, 165),
                        ('Huevo entero', 13, 1.1, 11, 155),
                        ('Salmón', 20, 0, 13, 208),
                        ('Atún en agua', 29, 0, 1, 128),
                        ('Camarones', 24, 0.2, 0.3, 99)],
        'sin_lactosa': [('Pechuga de pollo', 31, 0, 3.6, 165),
                        ('Huevo entero', 13, 1.1, 11, 155),
                        ('Atún en agua', 29, 0, 1, 128),
                        ('Tofu firme', 8, 2, 4.8, 76),
                        ('Salmón', 20, 0, 13, 208)],
    },
    'carbohidratos': {
        'ninguna':     [('Arroz blanco cocido', 2.7, 28, 0.3, 130),
                        ('Avena en hojuelas', 11, 66, 7, 389),
                        ('Papa cocida', 2, 17, 0.1, 77),
                        ('Pan integral', 9, 41, 3.4, 247),
                        ('Pasta integral', 5, 37, 1.4, 174)],
        'vegetariano': [('Arroz blanco cocido', 2.7, 28, 0.3, 130),
                        ('Avena en hojuelas', 11, 66, 7, 389),
                        ('Papa cocida', 2, 17, 0.1, 77),
                        ('Quinoa cocida', 4.4, 21, 1.9, 120),
                        ('Pan integral', 9, 41, 3.4, 247)],
        'vegano':      [('Arroz integral cocido', 2.6, 23, 0.9, 111),
                        ('Avena en hojuelas', 11, 66, 7, 389),
                        ('Papa cocida', 2, 17, 0.1, 77),
                        ('Quinoa cocida', 4.4, 21, 1.9, 120),
                        ('Batata cocida', 2, 20, 0.1, 86)],
        'sin_gluten':  [('Arroz blanco cocido', 2.7, 28, 0.3, 130),
                        ('Papa cocida', 2, 17, 0.1, 77),
                        ('Quinoa cocida', 4.4, 21, 1.9, 120),
                        ('Batata cocida', 2, 20, 0.1, 86),
                        ('Maíz cocido', 3.3, 19, 1.4, 96)],
        'sin_lactosa': [('Arroz blanco cocido', 2.7, 28, 0.3, 130),
                        ('Avena en hojuelas', 11, 66, 7, 389),
                        ('Papa cocida', 2, 17, 0.1, 77),
                        ('Pan integral', 9, 41, 3.4, 247),
                        ('Pasta integral', 5, 37, 1.4, 174)],
    },
    'grasas': {
        'ninguna':     [('Aguacate', 2, 9, 15, 160),
                        ('Aceite de oliva', 0, 0, 100, 884),
                        ('Almendras', 21, 22, 49, 579),
                        ('Nueces', 15, 14, 65, 654)],
        'vegetariano': [('Aguacate', 2, 9, 15, 160),
                        ('Aceite de oliva', 0, 0, 100, 884),
                        ('Almendras', 21, 22, 49, 579),
                        ('Mantequilla de maní', 25, 20, 50, 588)],
        'vegano':      [('Aguacate', 2, 9, 15, 160),
                        ('Aceite de oliva', 0, 0, 100, 884),
                        ('Almendras', 21, 22, 49, 579),
                        ('Semillas de chía', 17, 42, 31, 486)],
        'sin_gluten':  [('Aguacate', 2, 9, 15, 160),
                        ('Aceite de oliva', 0, 0, 100, 884),
                        ('Almendras', 21, 22, 49, 579),
                        ('Nueces', 15, 14, 65, 654)],
        'sin_lactosa': [('Aguacate', 2, 9, 15, 160),
                        ('Aceite de oliva', 0, 0, 100, 884),
                        ('Almendras', 21, 22, 49, 579),
                        ('Nueces', 15, 14, 65, 654)],
    },
    'verduras': [
        ('Brócoli', 2.8, 7, 0.4, 34),
        ('Espinaca', 2.9, 3.6, 0.4, 23),
        ('Zanahoria', 0.9, 10, 0.2, 41),
        ('Pepino', 0.65, 3.6, 0.11, 16),
        ('Tomate', 0.9, 3.9, 0.2, 18),
        ('Lechuga romana', 1.2, 3.3, 0.3, 17),
    ],
}

NOMBRES_COMIDAS = {
    3: ['Desayuno', 'Almuerzo', 'Cena'],
    4: ['Desayuno', 'Media Mañana', 'Almuerzo', 'Cena'],
    5: ['Desayuno', 'Media Mañana', 'Almuerzo', 'Merienda', 'Cena'],
    6: ['Desayuno', 'Media Mañana', 'Almuerzo', 'Merienda', 'Pre-Entreno', 'Cena'],
}

PORCIONES_COMIDA = {
    3: [0.30, 0.40, 0.30],
    4: [0.25, 0.15, 0.40, 0.20],
    5: [0.22, 0.13, 0.35, 0.15, 0.15],
    6: [0.20, 0.10, 0.30, 0.15, 0.10, 0.15],
}

EMOJIS_COMIDA = {
    'Desayuno':      '🌅',
    'Media Mañana':  '🍎',
    'Almuerzo':      '🍽️',
    'Merienda':      '🥤',
    'Pre-Entreno':   '⚡',
    'Cena':          '🌙',
}


def _build_plan(calorias_dia, proteinas_g, carbos_g, grasas_g, comidas_dia, restriccion):
    nombres   = NOMBRES_COMIDAS[comidas_dia]
    porciones = PORCIONES_COMIDA[comidas_dia]

    alim_prot = ALIMENTOS['proteinas'].get(restriccion, ALIMENTOS['proteinas']['ninguna'])
    alim_carb = ALIMENTOS['carbohidratos'].get(restriccion, ALIMENTOS['carbohidratos']['ninguna'])
    alim_gras = ALIMENTOS['grasas'].get(restriccion, ALIMENTOS['grasas']['ninguna'])
    alim_verd = ALIMENTOS['verduras']

    plan = []
    for i, (nombre, porc) in enumerate(zip(nombres, porciones)):
        kcal_comida = calorias_dia * porc
        prot_c = proteinas_g * porc
        carb_c = carbos_g * porc
        gras_c = grasas_g * porc

        prot_item = alim_prot[i % len(alim_prot)]
        carb_item = alim_carb[i % len(alim_carb)]
        gras_item = alim_gras[i % len(alim_gras)]
        verd_item = alim_verd[i % len(alim_verd)]

        prot_g_porcion = round((prot_c / (prot_item[1] / 100)), 0) if prot_item[1] > 0 else 0
        carb_g_porcion = round((carb_c / (carb_item[2] / 100)), 0) if carb_item[2] > 0 else 0
        gras_g_porcion = round((gras_c / (gras_item[3] / 100)), 0) if gras_item[3] > 0 else 0

        alimentos_comida = [
            {'nombre': prot_item[0], 'cantidad': f'{min(int(prot_g_porcion), 250)}g', 'tipo': 'proteina'},
            {'nombre': carb_item[0], 'cantidad': f'{min(int(carb_g_porcion), 300)}g', 'tipo': 'carbo'},
            {'nombre': verd_item[0], 'cantidad': '100g', 'tipo': 'verdura'},
        ]
        if nombre in ('Desayuno', 'Almuerzo', 'Cena'):
            alimentos_comida.append(
                {'nombre': gras_item[0], 'cantidad': f'{min(int(gras_g_porcion), 30)}g', 'tipo': 'grasa'}
            )

        plan.append({
            'nombre':    nombre,
            'emoji':     EMOJIS_COMIDA.get(nombre, '🍴'),
            'kcal':      round(kcal_comida),
            'proteinas': round(prot_c, 1),
            'carbos':    round(carb_c, 1),
            'grasas':    round(gras_c, 1),
            'alimentos': alimentos_comida,
        })

    return plan


# Advertencias y recomendaciones por condición
ALERTAS_LIMITACIONES = {
    'asma': {
        'icono': 'bi-wind',
        'color': '#60a5fa',
        'titulo': 'Asma / Problemas respiratorios',
        'nutricion': 'Prioriza antioxidantes (vitamina C, E) y omega-3 para reducir inflamación. Evita alimentos procesados y sulfitos (vino, frutos secos con conservantes).',
        'ejercicio': 'Calienta siempre 10+ min antes. Evita ejercicio en frío extremo o alta humedad. Ten siempre tu broncodilatador a mano.',
    },
    'cardiaco': {
        'icono': 'bi-heart',
        'color': '#f87171',
        'titulo': 'Problemas cardíacos',
        'nutricion': 'Dieta baja en sodio (<1500 mg/día) y grasas saturadas. Aumenta omega-3 (salmón, nueces), fibra y potasio (plátano, legumbres). Limita cafeína y alcohol.',
        'ejercicio': 'Consulta siempre con tu cardiólogo antes de aumentar intensidad. Mantén frecuencia cardíaca en zonas bajas-moderadas.',
    },
    'hipertension': {
        'icono': 'bi-activity',
        'color': '#f97316',
        'titulo': 'Hipertensión',
        'nutricion': 'Sigue el enfoque DASH: más frutas, verduras, lácteos bajos en grasa y menos sodio. Limita embutidos, enlatados y comida rápida.',
        'ejercicio': 'Evita ejercicios isométricos con apnea (Valsalva). Cardio moderado (caminar, bicicleta) 30 min/día es ideal.',
    },
    'diabetes': {
        'icono': 'bi-droplet',
        'color': '#34d399',
        'titulo': 'Diabetes',
        'nutricion': 'Prioriza carbohidratos de bajo índice glucémico (avena, legumbres, verduras). Evita azúcares simples y harinas refinadas. Distribución uniforme de carbos en cada comida.',
        'ejercicio': 'El ejercicio mejora la sensibilidad a la insulina. Monitorea tu glucosa antes y después del entrenamiento.',
    },
    'lesion_muscular': {
        'icono': 'bi-lightning',
        'color': '#a78bfa',
        'titulo': 'Lesión muscular',
        'nutricion': 'Aumenta la proteína (1.6–2g/kg) para acelerar la recuperación. Incluye alimentos antiinflamatorios: cúrcuma, jengibre, omega-3 y vitamina D.',
        'ejercicio': 'Evita ejercitar el grupo muscular afectado. Trabaja los grupos compensatorios y realiza rehabilitación activa con supervisión.',
    },
    'lesion_rodilla': {
        'icono': 'bi-person-walking',
        'color': '#fbbf24',
        'titulo': 'Lesión de rodilla',
        'nutricion': 'Colágeno hidrolizado (10g/día) y vitamina C ayudan a regenerar cartílago. Omega-3 para reducir inflamación articular.',
        'ejercicio': 'Evita sentadillas profundas, correr y saltos. Prioriza natación, bicicleta estática y ejercicios de cadena cinética abierta.',
    },
    'lesion_espalda': {
        'icono': 'bi-person',
        'color': '#fb923c',
        'titulo': 'Lesión de espalda / columna',
        'nutricion': 'Mantén peso saludable para reducir carga vertebral. Vitamina D y calcio para la densidad ósea. Antiinflamatorios naturales (omega-3, cúrcuma).',
        'ejercicio': 'Evita peso muerto, sentadilla con barra y movimientos de rotación brusca. Fortalece el core con ejercicios de bajo impacto (plancha, bird-dog).',
    },
    'lesion_hombro': {
        'icono': 'bi-arrows',
        'color': '#c084fc',
        'titulo': 'Lesión de hombro',
        'nutricion': 'Colágeno hidrolizado y vitamina C para recuperación de tejidos blandos. Magnesio para relajar la musculatura.',
        'ejercicio': 'Evita press por encima de la cabeza, jalones y movimientos circulares amplios. Trabaja rotadores del manguito con bandas elásticas.',
    },
    'articulacion': {
        'icono': 'bi-bounding-box',
        'color': '#38bdf8',
        'titulo': 'Articulación con riesgo',
        'nutricion': 'Dieta antiinflamatoria: frutas del bosque, aceite de oliva extra virgen, pescado azul y vegetales de hoja verde. Limita azúcar y grasas trans.',
        'ejercicio': 'Prioriza ejercicio de bajo impacto (natación, elíptica). Evita impactos repetitivos. Calienta bien las articulaciones antes de cargar peso.',
    },
    'movilidad_reducida': {
        'icono': 'bi-wheelchair',
        'color': '#00d4aa',
        'titulo': 'Movilidad reducida',
        'nutricion': 'Ajusta las calorías a tu nivel de actividad real. Prioriza proteína alta para preservar músculo. Incluye vitamina D y calcio.',
        'ejercicio': 'Ejercicios en silla, en cama o en agua según tu capacidad. La resistencia con bandas elásticas es segura y adaptable.',
    },
    'embarazo': {
        'icono': 'bi-gender-female',
        'color': '#f9a8d4',
        'titulo': 'Embarazo / postparto',
        'nutricion': 'Aumenta calorías (+300 kcal/día en 2º-3º trimestre). Prioriza ácido fólico, hierro, calcio, omega-3 (DHA). Evita alcohol, cafeína excesiva y pescados con mercurio.',
        'ejercicio': 'Solo ejercicio aprobado por tu ginecólogo. Evita posición boca abajo después del 1er trimestre, saltos y contacto. Caminar y yoga prenatal son ideales.',
    },
}


@login_required
def plan_nutricional(request):
    resultado = None

    # Obtener perfil y limitaciones del usuario
    try:
        perfil = request.user.profile
    except Exception:
        perfil = None

    limitaciones = []
    alertas = []
    if perfil:
        limitaciones = perfil.limitaciones or []
        alertas = [ALERTAS_LIMITACIONES[k] for k in limitaciones if k in ALERTAS_LIMITACIONES]

    # Valores por defecto desde el perfil para pre-rellenar el formulario
    initial = {}
    if perfil:
        if perfil.genero in ('M', 'F'):
            initial['genero'] = perfil.genero
        if perfil.edad:
            initial['edad'] = perfil.edad
        if perfil.peso:
            initial['peso'] = perfil.peso
        if perfil.altura:
            initial['altura'] = perfil.altura
        obj_map = {
            'bajar_peso': 'perder', 'mantener_peso': 'mantener',
            'ganar_musculo': 'ganar', 'mejorar_resistencia': 'mantener',
            'mejorar_flexibilidad': 'mantener', 'rendimiento': 'ganar',
        }
        if perfil.objetivo:
            initial['objetivo'] = obj_map.get(perfil.objetivo, 'mantener')

    form = PlanNutricionalForm(initial=initial)

    if request.method == 'POST':
        form = PlanNutricionalForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            genero      = d['genero']
            edad        = d['edad']
            peso        = d['peso']
            altura      = d['altura']
            objetivo    = d['objetivo']
            restriccion = d['restriccion']
            comidas_dia = d['comidas_dia']

            if genero == 'M':
                tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
            else:
                tmb = 10 * peso + 6.25 * altura - 5 * edad - 161

            getd = tmb * 1.55
            ajuste = {'perder': -0.15, 'mantener': 0, 'ganar': 0.10}
            calorias_dia = getd * (1 + ajuste[objetivo])

            # Ajuste de macros según limitaciones
            if 'diabetes' in limitaciones:
                prot_pct, carb_pct, gras_pct = 0.35, 0.35, 0.30  # menos carbos simples
            elif objetivo == 'ganar':
                prot_pct, carb_pct, gras_pct = 0.30, 0.50, 0.20
            elif objetivo == 'perder':
                prot_pct, carb_pct, gras_pct = 0.35, 0.40, 0.25
            else:
                prot_pct, carb_pct, gras_pct = 0.30, 0.45, 0.25

            # Si tiene lesión muscular → más proteína
            if any(k in limitaciones for k in ('lesion_muscular', 'lesion_rodilla', 'lesion_espalda', 'lesion_hombro')):
                prot_pct = min(prot_pct + 0.05, 0.40)
                carb_pct = max(carb_pct - 0.05, 0.30)

            proteinas_g = round(calorias_dia * prot_pct / 4, 1)
            carbos_g    = round(calorias_dia * carb_pct / 4, 1)
            grasas_g    = round(calorias_dia * gras_pct / 9, 1)

            plan = _build_plan(calorias_dia, proteinas_g, carbos_g, grasas_g,
                               comidas_dia, restriccion)

            resultado = {
                'genero': genero, 'edad': edad, 'peso': peso, 'altura': altura,
                'objetivo': objetivo, 'restriccion': restriccion,
                'calorias_dia': round(calorias_dia),
                'proteinas_g': proteinas_g,
                'carbos_g': carbos_g,
                'grasas_g': grasas_g,
                'plan': plan,
            }

    return render(request, 'tools/plan_nutricional.html', {
        'form':         form,
        'resultado':    resultado,
        'limitaciones': limitaciones,
        'alertas':      alertas,
        'perfil':       perfil,
    })


# ─── Guardar Plan Nutricional ───────────────────────────────────────────────────

@login_required
def guardar_plan_nutricional(request):
    if request.method != 'POST':
        return redirect('plan_nutricional')

    import json as _json

    def _int(val, default):
        try: return int(val) if val not in (None, '') else default
        except (ValueError, TypeError): return default

    def _float(val, default):
        try: return float(val) if val not in (None, '') else default
        except (ValueError, TypeError): return default

    nombre       = request.POST.get('nombre', '').strip() or 'Mi Plan'
    genero       = request.POST.get('genero', 'M') or 'M'
    edad         = _int(request.POST.get('edad'), 25)
    peso         = _float(request.POST.get('peso'), 70)
    altura       = _float(request.POST.get('altura'), 175)
    objetivo     = request.POST.get('objetivo', 'mantener') or 'mantener'
    restriccion  = request.POST.get('restriccion', 'ninguna') or 'ninguna'
    comidas_dia  = _int(request.POST.get('comidas_dia'), 3)
    calorias_dia = _float(request.POST.get('calorias_dia'), 0)
    proteinas_g  = _float(request.POST.get('proteinas_g'), 0)
    carbos_g     = _float(request.POST.get('carbos_g'), 0)
    grasas_g     = _float(request.POST.get('grasas_g'), 0)
    try:
        plan_json = _json.loads(request.POST.get('plan_json', '[]') or '[]')
    except Exception:
        plan_json = []

    plan = PlanNutricional(
        usuario=request.user, nombre=nombre,
        genero=genero, edad=edad, peso=peso, altura=altura,
        objetivo=objetivo, restriccion=restriccion,
        comidas_dia=comidas_dia, calorias_dia=calorias_dia,
        proteinas_g=proteinas_g, carbos_g=carbos_g, grasas_g=grasas_g,
        plan_json=plan_json,
    )
    plan.save()
    messages.success(request, f'Plan "{nombre}" guardado en Mis Dietas.')
    return redirect('mis_dietas')


# ─── Guardar dieta (calculadora) ────────────────────────────────────────────────

@login_required
def guardar_dieta(request):
    if request.method != 'POST':
        return redirect('calculadora_calorias')

    nombre          = request.POST.get('nombre', '').strip() or 'Mi Dieta'
    genero          = request.POST.get('genero')
    try:
        edad   = int(request.POST.get('edad', 25))
        peso   = float(request.POST.get('peso', 70))
        altura = float(request.POST.get('altura', 175))
    except (ValueError, TypeError):
        return redirect('calculadora_calorias')
    nivel_actividad = request.POST.get('nivel_actividad', 'activo')
    objetivo        = request.POST.get('objetivo', 'mantener')

    dieta = CalculoCaloria(
        usuario=request.user, nombre=nombre,
        genero=genero, edad=edad, peso=peso, altura=altura,
        nivel_actividad=nivel_actividad, objetivo=objetivo,
    )
    dieta.calcular()
    dieta.save()
    messages.success(request, f'Dieta "{nombre}" guardada correctamente.')
    return redirect('mis_dietas')


# ─── Mis Dietas ──────────────────────────────────────────────────────────────────

@login_required
def mis_dietas(request):
    calculos = CalculoCaloria.objects.filter(usuario=request.user)
    planes   = PlanNutricional.objects.filter(usuario=request.user)
    return render(request, 'tools/mis_dietas.html', {
        'calculos': calculos,
        'planes':   planes,
        'total':    calculos.count() + planes.count(),
    })


@login_required
def eliminar_dieta(request, dieta_id):
    dieta = get_object_or_404(CalculoCaloria, id=dieta_id, usuario=request.user)
    nombre = dieta.nombre or 'Dieta'
    dieta.delete()
    messages.success(request, f'"{nombre}" eliminada.')
    return redirect('mis_dietas')


@login_required
def activar_dieta(request, dieta_id):
    dieta = get_object_or_404(CalculoCaloria, id=dieta_id, usuario=request.user)
    CalculoCaloria.objects.filter(usuario=request.user).update(activa=False)
    dieta.activa = True
    dieta.save()
    messages.success(request, f'"{dieta.nombre}" establecida como dieta activa.')
    return redirect('mis_dietas')


@login_required
def eliminar_plan(request, plan_id):
    plan = get_object_or_404(PlanNutricional, id=plan_id, usuario=request.user)
    nombre = plan.nombre or 'Plan'
    plan.delete()
    messages.success(request, f'"{nombre}" eliminado.')
    return redirect('mis_dietas')


@login_required
def activar_plan(request, plan_id):
    plan = get_object_or_404(PlanNutricional, id=plan_id, usuario=request.user)
    PlanNutricional.objects.filter(usuario=request.user).update(activa=False)
    plan.activa = True
    plan.save()
    messages.success(request, f'"{plan.nombre}" establecido como plan activo.')
    return redirect('mis_dietas')


# ─── Hub ────────────────────────────────────────────────────────────────────────

@login_required
def herramientas(request):
    return render(request, 'tools/herramientas.html')


# ─── FitBot — Asistente IA ──────────────────────────────────────────────────────

@login_required
def chatbot(request):
    if request.method == 'POST':
        import json as _json
        import requests as http_requests
        from django.conf import settings
        from apps.progress.models import RegistroPeso, MedicionCorporal
        from apps.routines.models import Entrenamiento
        from django.utils import timezone
        from datetime import timedelta

        try:
            body = _json.loads(request.body)
            user_message = body.get('message', '').strip()
            action = body.get('action', '')
        except Exception:
            return JsonResponse({'error': 'invalid'}, status=400)

        # Limpiar conversación
        if action == 'clear':
            request.session['fitbot_history'] = []
            return JsonResponse({'ok': True})

        if not user_message:
            return JsonResponse({'error': 'empty'}, status=400)

        # ── Contexto del usuario ──────────────────────────────────────────────
        user = request.user
        try:
            profile = user.profile
        except Exception:
            profile = None

        ctx = []

        if profile:
            nombre = user.first_name or user.username
            ctx.append(f"Nombre: {nombre}")
            if profile.peso:
                ctx.append(f"Peso en perfil: {profile.peso} kg")
            if profile.altura:
                ctx.append(f"Altura: {profile.altura} cm")
            if profile.peso and profile.altura and profile.altura > 0:
                imc = round(profile.peso / (profile.altura / 100) ** 2, 1)
                ctx.append(f"IMC actual: {imc}")

        # Historial de pesos
        pesos = list(RegistroPeso.objects.filter(usuario=user).order_by('-fecha')[:8])
        if pesos:
            peso_str = ', '.join([f"{p.fecha.strftime('%d/%m')}: {p.peso}kg" for p in pesos])
            ctx.append(f"Historial de peso (reciente primero): {peso_str}")
            if len(pesos) >= 2:
                diff = pesos[0].peso - pesos[-1].peso
                tendencia = f"{'bajó' if diff < 0 else 'subió'} {abs(round(diff, 1))}kg en {len(pesos)} registros"
                ctx.append(f"Tendencia: {tendencia}")

        # Cálculo calórico activo
        calculo = None
        try:
            calculo = CalculoCaloria.objects.filter(usuario=user).latest('calculado_en')
            ctx.append(f"Meta calórica diaria: {calculo.getd} kcal")
            ctx.append(f"Objetivo: {calculo.objetivo}")
            ctx.append(f"Macros diarios — Proteínas: {calculo.proteinas_g}g, Carbos: {calculo.carbos_g}g, Grasas: {calculo.grasas_g}g")
        except CalculoCaloria.DoesNotExist:
            pass

        # Entrenamientos recientes
        desde = timezone.now() - timedelta(days=30)
        n_entrenos = Entrenamiento.objects.filter(
            usuario=user, completado=True, iniciado_en__gte=desde
        ).count()
        if n_entrenos:
            ctx.append(f"Entrenamientos completados (últimos 30 días): {n_entrenos}")

        context_text = '\n'.join(ctx) if ctx else 'El usuario no tiene datos de progreso registrados aún.'

        system_prompt = f"""Eres FitBot, el asistente personal de fitness y nutrición de SportsVision.

Puedes hacer dos cosas:
1. Analizar el progreso de peso y calorías del usuario usando sus datos reales
2. Responder preguntas generales sobre ejercicio, nutrición, suplementos, descanso y bienestar

DATOS REALES DEL USUARIO:
{context_text}

INSTRUCCIONES:
- Responde siempre en español, de forma amigable y motivadora
- Cuando el usuario pregunte por su progreso, usa sus datos reales y sé específico
- Para preguntas generales de fitness/nutrición, responde con conocimiento experto y práctico
- Mantén respuestas concisas (máximo 3-4 párrafos)
- Usa emojis ocasionalmente para hacer la respuesta más amigable
- Si no tienes datos suficientes para algo, dilo honestamente y sugiere qué registrar"""

        # ── Historial de conversación ─────────────────────────────────────────
        history = request.session.get('fitbot_history', [])
        history.append({'role': 'user', 'content': user_message})

        # ── Motor local de respuestas ─────────────────────────────────────────
        def _respuesta_local(msg, profile, pesos, calculo, n_entrenos):
            m = msg.lower()
            nombre = (profile.user.first_name if profile and profile.user.first_name else user.username)

            # Progreso de peso
            if any(w in m for w in ['peso', 'progreso', 'adelgaz', 'engord', 'kilos', 'bajado', 'subido']):
                if not pesos:
                    return f"Hola {nombre}! 👋 Aún no tienes registros de peso. Ve a **Tu Progreso → Registrar peso** para empezar a hacer seguimiento. ¡Cada dato cuenta! 📊"
                ultimo = pesos[0].peso
                resp = f"📊 Tu último peso registrado es **{ultimo} kg**.\n\n"
                if len(pesos) >= 2:
                    diff = round(pesos[0].peso - pesos[-1].peso, 1)
                    if diff < 0:
                        resp += f"✅ ¡Excelente! Has bajado **{abs(diff)} kg** desde tu primer registro. ¡Vas por buen camino!\n\nConsejo: mantén un déficit calórico moderado (300-500 kcal/día) y sigue entrenando con consistencia para seguir bajando sin perder músculo. 💪"
                    elif diff > 0:
                        resp += f"📈 Has subido **{diff} kg** desde tu primer registro.\n\nSi tu objetivo es ganar músculo, ¡es una buena señal! Si quieres perder peso, revisa tus calorías diarias y asegúrate de estar en déficit. Recuerda que el progreso no siempre es lineal. 🎯"
                    else:
                        resp += "⚖️ Tu peso se ha mantenido estable. Si quieres cambiar tu composición corporal, ajusta tus calorías: déficit para perder grasa, superávit para ganar músculo."
                if profile and profile.altura:
                    imc = round(ultimo / (profile.altura / 100) ** 2, 1)
                    cat = 'Bajo peso' if imc < 18.5 else 'Normal' if imc < 25 else 'Sobrepeso' if imc < 30 else 'Obesidad'
                    resp += f"\n\n🔢 Tu IMC actual es **{imc}** ({cat})."
                return resp

            # Calorías
            if any(w in m for w in ['caloria', 'caloría', 'kcal', 'dieta', 'comer', 'alimenta', 'nutri', 'macro']):
                if calculo:
                    obj_labels = {'perder_rapido':'perder peso rápido','perder':'perder peso','mantener':'mantener tu peso','ganar':'ganar masa muscular','ganar_rapido':'ganar masa rápido'}
                    obj = obj_labels.get(calculo.objetivo, calculo.objetivo)
                    return (f"🔥 Según tu cálculo, necesitas **{int(calculo.getd)} kcal/día** para {obj}.\n\n"
                            f"📊 Distribución de macros diarios:\n"
                            f"• Proteínas: **{calculo.proteinas_g}g** (músculo y saciedad)\n"
                            f"• Carbohidratos: **{calculo.carbos_g}g** (energía principal)\n"
                            f"• Grasas: **{calculo.grasas_g}g** (hormonas y absorción)\n\n"
                            f"💡 Tip: distribuye las calorías en 3-5 comidas. Prioriza proteína en cada comida para preservar músculo.")
                return ("Para calcular tus calorías personalizadas, ve a **Herramientas → Calculadora de Calorías**. 🔢\n\n"
                        "En general, una mujer activa necesita ~1800-2200 kcal/día y un hombre activo ~2200-2800 kcal/día. "
                        "Ajusta según tu objetivo: déficit de 300-500 kcal para perder grasa, superávit de 200-400 kcal para ganar músculo.")

            # Proteína
            if any(w in m for w in ['proteina', 'proteína', 'protein', 'pollo', 'carne', 'huevo']):
                if profile and profile.peso:
                    p_min = round(profile.peso * 1.6, 0)
                    p_max = round(profile.peso * 2.2, 0)
                    return (f"💪 Para tu peso de **{profile.peso} kg**, necesitas entre **{int(p_min)}g y {int(p_max)}g de proteína al día**.\n\n"
                            f"Mejores fuentes de proteína:\n"
                            f"• 🐔 Pechuga de pollo (31g/100g)\n"
                            f"• 🥚 Huevos (6g por huevo)\n"
                            f"• 🐟 Atún/salmón (25-28g/100g)\n"
                            f"• 🫘 Legumbres (8-15g/100g)\n"
                            f"• 🥛 Yogur griego (10g/100g)\n\n"
                            f"Distribuye la proteína en todas tus comidas para maximizar la síntesis muscular. 🎯")
                return ("La recomendación general es **1.6-2.2g de proteína por kg de peso corporal** al día.\n\n"
                        "Para ganar músculo: apunta a 2g/kg. Para mantener: 1.6g/kg. Para perder grasa preservando músculo: 2-2.4g/kg.\n\n"
                        "Fuentes top: pollo, huevos, atún, salmón, legumbres, yogur griego y claras de huevo. 🥚")

            # Ganar músculo
            if any(w in m for w in ['musculo', 'músculo', 'masa', 'volumen', 'ganar', 'crecer', 'hipertrofia']):
                return ("💪 Para ganar músculo necesitas 3 pilares:\n\n"
                        "**1. Entrenamiento:** Haz pesas 3-5 días/semana con progresión de carga. Enfócate en ejercicios compuestos: sentadilla, peso muerto, press banca y remo.\n\n"
                        "**2. Nutrición:** Superávit calórico de 200-400 kcal/día. Consume 1.8-2.2g de proteína por kg de peso. No te saltes carbohidratos — son el combustible de tus músculos.\n\n"
                        "**3. Descanso:** Duerme 7-9 horas. Los músculos crecen mientras descansas, no mientras entrenas. 😴\n\n"
                        "La paciencia es clave: espera resultados visibles en 8-12 semanas de consistencia. 🎯")

            # Perder grasa
            if any(w in m for w in ['perder', 'bajar', 'adelgazar', 'quemar', 'grasa', 'definir', 'delgado']):
                return ("🔥 Para perder grasa de forma efectiva y sostenible:\n\n"
                        "**Calorías:** Déficit de 300-500 kcal/día (no más, para no perder músculo).\n\n"
                        "**Proteína alta:** 2-2.4g/kg de peso para preservar músculo mientras pierdes grasa.\n\n"
                        "**Ejercicio:** Combina pesas (preserva músculo) con cardio moderado (3-4 días/semana, 30-45 min). El HIIT es muy efectivo.\n\n"
                        "**Hidratación:** Bebe 2-3 litros de agua al día. A veces la sensación de hambre es en realidad sed.\n\n"
                        "⚠️ Evita déficits extremos: perder más de 1kg/semana suele ser agua y músculo, no grasa. 📉")

            # Ejercicios del día / rutina
            if any(w in m for w in ['ejercicio', 'rutina', 'entrena', 'workout', 'hacer hoy', 'hoy', 'empezar']):
                if n_entrenos >= 5:
                    return (f"🏆 ¡Llevas {n_entrenos} entrenamientos este mes, genial! \n\n"
                            "Asegúrate de incluir días de descanso (al menos 1-2 por semana). Si llevas varios días seguidos, considera un día de recuperación activa: caminar, estirar o yoga. 🧘\n\n"
                            "Para hoy puedes hacer:\n• Estiramientos profundos 15 min\n• Foam roller en grupos musculares trabajados\n• Caminata de 30 min a ritmo moderado")
                return ("💪 Un buen plan de entrenamiento para principiantes/intermedios:\n\n"
                        "**Lunes:** Pecho + Tríceps (press, aperturas, fondos)\n"
                        "**Martes:** Espalda + Bíceps (jalones, remo, curl)\n"
                        "**Miércoles:** Descanso o cardio suave\n"
                        "**Jueves:** Hombros + Core (press militar, elevaciones, plancha)\n"
                        "**Viernes:** Piernas (sentadilla, peso muerto, prensa)\n"
                        "**Sábado:** Cardio HIIT 20-30 min\n"
                        "**Domingo:** Descanso activo\n\n"
                        "Ve a **Nueva Rutina** para crear tu plan personalizado en SportsVision. 🎯")

            # Suplementos
            if any(w in m for w in ['suplemento', 'proteina en polvo', 'whey', 'creatina', 'bcaa', 'pre-entreno', 'vitamina']):
                return ("🧪 Suplementos más respaldados por la ciencia:\n\n"
                        "**Creatina monohidrato** ⭐⭐⭐: El más estudiado. Aumenta fuerza y masa muscular. 3-5g/día, cualquier momento.\n\n"
                        "**Proteína whey** ⭐⭐⭐: Conveniente si no llegas a tus metas de proteína con comida. No es mágica, es comida en polvo.\n\n"
                        "**Cafeína** ⭐⭐: Mejora rendimiento y concentración. 3-6mg/kg, 30-60 min antes de entrenar.\n\n"
                        "**Vitamina D** ⭐⭐: Muchas personas tienen déficit. Importante para huesos, hormonas e inmunidad.\n\n"
                        "⚠️ BCAA, glutamina y la mayoría de pre-entrenos tienen evidencia limitada. Prioriza nutrición real primero. 🥗")

            # Descanso / sueño
            if any(w in m for w in ['descanso', 'dormir', 'sueño', 'recupera', 'cansado', 'fatiga']):
                return ("😴 El descanso es tan importante como el entrenamiento:\n\n"
                        "**Sueño:** 7-9 horas por noche. Durante el sueño profundo se libera hormona de crecimiento que repara y construye músculo.\n\n"
                        "**Entre sesiones:** Los músculos necesitan 48-72h para recuperarse completamente. No entrenes el mismo grupo muscular dos días seguidos.\n\n"
                        "**Señales de sobreentrenamiento:** cansancio persistente, fuerza que no avanza, mal humor, dificultad para dormir. Si tienes varios de estos, toma 3-5 días de descanso total.\n\n"
                        "**Recuperación activa:** caminar, nadar suave o yoga en días de descanso mantiene la circulación sin estresar los músculos. 🧘")

            # Hidratación
            if any(w in m for w in ['agua', 'hidrat', 'beber', 'líquido']):
                if profile and profile.peso:
                    litros = round(profile.peso * 0.033, 1)
                    return (f"💧 Para tu peso de **{profile.peso} kg**, necesitas aproximadamente **{litros} litros de agua al día**.\n\n"
                            "Durante el ejercicio añade 500-1000ml por hora de entrenamiento.\n\n"
                            "Señales de deshidratación: orina oscura, dolor de cabeza, fatiga, calambres.\n\n"
                            "Tip: Bebe un vaso de agua al despertar, uno antes de cada comida y uno antes/durante/después del entrenamiento. 🌊")
                return ("💧 La recomendación general es **2-3 litros de agua al día** (más si haces ejercicio o hace calor).\n\n"
                        "Fórmula simple: 33ml por kg de peso corporal. Un indicador fácil: si tu orina es amarillo claro, estás bien hidratado.")

            # Saludos y consultas generales
            if any(w in m for w in ['hola', 'buenas', 'hey', 'qué tal', 'como estas', 'cómo estás']):
                return f"¡Hola {nombre}! 😊 Estoy aquí para ayudarte con tu fitness. Puedo analizar tu progreso, darte consejos de nutrición, rutinas de ejercicio, suplementación y más. ¿Qué quieres saber hoy? 💪"

            if any(w in m for w in ['gracias', 'perfecto', 'genial', 'excelente', 'ok', 'bien']):
                return f"¡De nada {nombre}! 🙌 Recuerda: la consistencia es la clave del éxito. ¿Hay algo más en lo que pueda ayudarte? 💪"

            # Respuesta genérica
            return (f"Buena pregunta, {nombre}! 🤔 Puedo ayudarte con:\n\n"
                    "• 📊 Análisis de tu progreso de peso\n"
                    "• 🔥 Calorías y macros personalizados\n"
                    "• 💪 Consejos para ganar músculo\n"
                    "• 📉 Estrategias para perder grasa\n"
                    "• 🏋️ Rutinas y ejercicios\n"
                    "• 🧪 Suplementación basada en ciencia\n"
                    "• 😴 Descanso y recuperación\n\n"
                    "¿Sobre cuál de estos temas quieres saber más?")

        # ── Llamada a Claude API (si hay key) o motor local ──────────────────
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            bot_response = _respuesta_local(user_message, profile, pesos,
                                            calculo if 'calculo' in dir() else None,
                                            n_entrenos if 'n_entrenos' in dir() else 0)
        else:
            try:
                resp = http_requests.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': 'claude-haiku-4-5-20251001',
                        'max_tokens': 1024,
                        'system': system_prompt,
                        'messages': history[-20:],
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                bot_response = resp.json()['content'][0]['text']
            except Exception:
                bot_response = _respuesta_local(user_message, profile, pesos,
                                                calculo if 'calculo' in dir() else None,
                                                n_entrenos if 'n_entrenos' in dir() else 0)

        # Guardar en sesión (máx 20 mensajes = 10 intercambios)
        history.append({'role': 'assistant', 'content': bot_response})
        request.session['fitbot_history'] = history[-20:]

        return JsonResponse({'response': bot_response})

    return redirect('herramientas')


@login_required
def descargar_dieta_pdf(request, plan_id):
    from io import BytesIO
    from django.utils import timezone
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    plan = get_object_or_404(PlanNutricional, id=plan_id, usuario=request.user)
    dias = plan.plan_json if isinstance(plan.plan_json, list) else []

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    def mk(name, **kw):
        return ParagraphStyle(name, parent=styles['Normal'], **kw)

    C = colors.HexColor
    story = []
    story.append(Paragraph('SPORTSVISION',
        mk('brand', fontSize=11, textColor=C('#6b7280'), spaceAfter=2)))
    story.append(Paragraph(plan.nombre or 'Plan Nutricional',
        mk('title', fontSize=22, textColor=C('#00d4aa'), spaceAfter=6)))

    objetivo = plan.objetivo or '-'
    resumen = (
        f'Objetivo: {objetivo}  ·  {plan.calorias_dia} kcal/dia  ·  '
        f'Proteinas: {plan.proteinas_g}g  ·  Carbos: {plan.carbos_g}g  ·  '
        f'Grasas: {plan.grasas_g}g'
    )
    story.append(Paragraph(resumen,
        mk('sub', fontSize=9, textColor=C('#9ca3af'), spaceAfter=8)))
    story.append(HRFlowable(width='100%', thickness=1, color=C('#1e293b')))
    story.append(Spacer(1, 0.4*cm))

    for i, dia_data in enumerate(dias):
        dia_nombre = dia_data.get('dia', '')
        meals = dia_data.get('meals', [])

        story.append(Paragraph(dia_nombre,
            mk(f'dia{i}', fontSize=12, textColor=C('#00d4aa'),
               fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)))

        header = ['Comida', 'Hora', 'Descripcion', 'Kcal', 'P', 'C', 'G']
        data = [header]
        for m in meals:
            p_val = str(m.get('p', '')) + 'g'
            c_val = str(m.get('c', '')) + 'g'
            f_val = str(m.get('f', '')) + 'g'
            data.append([
                Paragraph(m.get('n', ''), mk(f'mn{i}', fontSize=8, textColor=C('#e2e8f0'))),
                m.get('time', ''),
                Paragraph(m.get('d', ''), mk(f'md{i}', fontSize=7, textColor=C('#9ca3af'))),
                str(m.get('k', '')),
                p_val, c_val, f_val,
            ])

        tbl = Table(data,
                    colWidths=[3.5*cm, 1.5*cm, 6*cm, 1.2*cm, 1*cm, 1*cm, 1*cm],
                    repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  C('#0d1b2a')),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  C('#00d4aa')),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0),  8),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [C('#111827'), C('#1a2035')]),
            ('TEXTCOLOR',     (0, 1), (-1, -1), C('#e2e8f0')),
            ('FONTSIZE',      (0, 1), (-1, -1), 8),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN',         (0, 0), (0, -1),  'LEFT'),
            ('ALIGN',         (2, 0), (2, -1),  'LEFT'),
            ('GRID',          (0, 0), (-1, -1), 0.25, C('#374151')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 5),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(tbl)

    story.append(Spacer(1, 0.6*cm))
    fecha = timezone.now().strftime('%d/%m/%Y %H:%M')
    story.append(Paragraph(
        f'Generado por SportsVision · {fecha}',
        mk('footer', fontSize=7, textColor=C('#4b5563'), alignment=TA_CENTER)))

    doc.build(story)
    buf.seek(0)
    filename = (plan.nombre or 'dieta').replace(' ', '_').lower()
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dieta_{filename}.pdf"'
    return response

