from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import CaloriasForm, IMCForm, PlanNutricionalForm


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

    return render(request, 'tools/calculadora_calorias.html', {
        'form': form,
        'resultado': resultado,
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


@login_required
def plan_nutricional(request):
    resultado = None
    form = PlanNutricionalForm()

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

            if objetivo == 'ganar':
                prot_pct, carb_pct, gras_pct = 0.30, 0.50, 0.20
            elif objetivo == 'perder':
                prot_pct, carb_pct, gras_pct = 0.35, 0.40, 0.25
            else:
                prot_pct, carb_pct, gras_pct = 0.30, 0.45, 0.25

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
        'form': form,
        'resultado': resultado,
    })


# ─── Hub ────────────────────────────────────────────────────────────────────────

@login_required
def herramientas(request):
    return render(request, 'tools/herramientas.html')
