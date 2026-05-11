from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
