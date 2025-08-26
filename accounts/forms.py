from django import forms
from .models import Account, UserProfile

class FormularioRegistro(forms.ModelForm):
    password = forms.CharField(
        label="contrasena",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese contrasena',
            'class': 'form-control',
        })
    )
    confirmar_password = forms.CharField(
        label="Confirmar contrasena",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirme contrasena',
            'class': 'form-control',
        })
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone', 'email', 'password']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone': 'Teléfono',
            'email': 'Correo electrónico',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Ingrese Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Ingrese Apellido'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Ingrese Teléfono'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ingrese Correo'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar = cleaned_data.get('confirmar_password')
        if password != confirmar:
            raise forms.ValidationError("¡Las contrasenas no coinciden!")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class FormularioUsuario(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class FormularioPerfilUsuario(forms.ModelForm):
    # Cambiar foto_perfil por profile_picture
    profile_picture = forms.ImageField(
        required=False,
        error_messages={'invalid': "Solo archivos de imagen"},
        widget=forms.FileInput
    )

    class Meta:
        model = UserProfile
        fields = ('address_1', 'address_2', 'city', 'province', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

