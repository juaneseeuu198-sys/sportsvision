from django import forms
from .models import Rutina, SerieEntrenamiento
from apps.exercises.models import Equipo, GrupoMuscular


class RutinaForm(forms.ModelForm):
    equipos = forms.ModelMultipleChoiceField(
        queryset=Equipo.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'equip-checkbox'}),
        required=False
    )

    class Meta:
        model = Rutina
        fields = ['nombre', 'descripcion', 'equipos', 'nivel']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control sv-input', 'placeholder': 'Nombre de la rutina'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control sv-input', 'rows': 2}),
            'nivel': forms.Select(attrs={'class': 'form-select sv-input'}),
        }


class SerieForm(forms.ModelForm):
    class Meta:
        model = SerieEntrenamiento
        fields = ['repeticiones', 'peso', 'peso_corporal', 'tiempo_minutos', 'tiempo_segundos']
        widgets = {
            'repeticiones': forms.NumberInput(attrs={'class': 'form-control sv-input', 'placeholder': '0'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control sv-input', 'placeholder': '0', 'step': '0.5'}),
            'peso_corporal': forms.NumberInput(attrs={'class': 'form-control sv-input', 'placeholder': '0'}),
            'tiempo_minutos': forms.NumberInput(attrs={'class': 'form-control sv-input', 'placeholder': 'Minutos'}),
            'tiempo_segundos': forms.NumberInput(attrs={'class': 'form-control sv-input', 'placeholder': 'Segundos'}),
        }
