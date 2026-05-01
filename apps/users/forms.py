from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Nombre'}),
            'last_name':  forms.TextInput(attrs={'class': 'sv-input', 'placeholder': 'Apellido'}),
            'email':      forms.EmailInput(attrs={'class': 'sv-input', 'placeholder': 'Email'}),
        }


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['edad', 'peso', 'altura', 'avatar']
        widgets = {
            'edad':   forms.NumberInput(attrs={'class': 'sv-input', 'placeholder': 'Edad'}),
            'peso':   forms.NumberInput(attrs={'class': 'sv-input', 'placeholder': 'Peso (kg)', 'step': '0.1'}),
            'altura': forms.NumberInput(attrs={'class': 'sv-input', 'placeholder': 'Altura (cm)'}),
        }


GENERO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
]


class RegistroForm(UserCreationForm):
    # Cuenta
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control sv-input', 'placeholder': 'tu@correo.com',
    }))

    # Datos personales (paso 2)
    first_name = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control sv-input', 'placeholder': 'Ej: Carlos',
    }))
    edad = forms.IntegerField(required=False, min_value=10, max_value=100, widget=forms.NumberInput(attrs={
        'class': 'form-control sv-input', 'placeholder': '25',
    }))
    peso = forms.FloatField(required=False, min_value=20, max_value=300, widget=forms.NumberInput(attrs={
        'class': 'form-control sv-input', 'placeholder': '70.0', 'step': '0.1',
    }))
    altura = forms.FloatField(required=False, min_value=100, max_value=250, widget=forms.NumberInput(attrs={
        'class': 'form-control sv-input', 'placeholder': '175',
    }))
    genero = forms.ChoiceField(required=False, choices=[('', 'Prefiero no decir')] + GENERO_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'first_name', 'edad', 'peso', 'altura', 'genero']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, placeholder in [
            ('username',  'Tu nombre de usuario'),
            ('password1', 'Mínimo 8 caracteres'),
            ('password2', 'Repite tu contraseña'),
        ]:
            self.fields[name].widget.attrs.update({
                'class': 'form-control sv-input',
                'placeholder': placeholder,
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.email      = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                edad=self.cleaned_data.get('edad'),
                peso=self.cleaned_data.get('peso'),
                altura=self.cleaned_data.get('altura'),
            )
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control sv-input',
            'placeholder': 'EMAIL'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control sv-input',
            'placeholder': 'PASSWORD'
        })
