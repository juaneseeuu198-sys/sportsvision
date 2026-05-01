from django import forms


NIVEL_ACTIVIDAD_CHOICES = [
    ('sedentario', 'Sedentario — sin ejercicio o muy poco'),
    ('poca',       'Poca actividad — 1-3 días/semana'),
    ('activo',     'Activo — 3-5 días/semana'),
    ('diario',     'Muy activo — 6-7 días/semana'),
    ('extra',      'Extra activo — trabajo físico intenso'),
]

OBJETIVO_CHOICES = [
    ('perder_rapido', 'Perder peso rápido'),
    ('perder',        'Perder peso'),
    ('mantener',      'Mantener peso'),
    ('ganar',         'Ganar músculo'),
    ('ganar_rapido',  'Ganar músculo rápido'),
]

OBJETIVO_NUTRI_CHOICES = [
    ('perder',   'Perder peso'),
    ('mantener', 'Mantener peso'),
    ('ganar',    'Ganar músculo'),
]

RESTRICCION_CHOICES = [
    ('ninguna',     'Sin restricciones'),
    ('vegetariano', 'Vegetariano'),
    ('vegano',      'Vegano'),
    ('sin_gluten',  'Sin gluten'),
    ('sin_lactosa', 'Sin lactosa'),
]


class CaloriasForm(forms.Form):
    genero          = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])
    edad            = forms.IntegerField(min_value=10, max_value=120)
    peso            = forms.FloatField(min_value=30, max_value=300)
    altura          = forms.IntegerField(min_value=100, max_value=250)
    nivel_actividad = forms.ChoiceField(choices=NIVEL_ACTIVIDAD_CHOICES)
    objetivo        = forms.ChoiceField(choices=OBJETIVO_CHOICES)


class IMCForm(forms.Form):
    altura = forms.FloatField(
        min_value=50, max_value=300,
        widget=forms.NumberInput(attrs={
            'class': 'form-control sv-input',
            'placeholder': '170',
            'step': '0.1'
        })
    )
    peso = forms.FloatField(
        min_value=10, max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control sv-input',
            'placeholder': '70',
            'step': '0.1'
        })
    )


class PlanNutricionalForm(forms.Form):
    genero      = forms.ChoiceField(choices=[('M', 'Masculino'), ('F', 'Femenino')])
    edad        = forms.IntegerField(min_value=10, max_value=120)
    peso        = forms.FloatField(min_value=30, max_value=300)
    altura      = forms.IntegerField(min_value=100, max_value=250)
    objetivo    = forms.ChoiceField(choices=OBJETIVO_NUTRI_CHOICES)
    restriccion = forms.ChoiceField(choices=RESTRICCION_CHOICES)
    comidas_dia = forms.IntegerField(min_value=3, max_value=6, initial=4)
