from django import forms

class FormularioContacto(forms.Form):
    nombre = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'ej.: María Pérez', 'class': 'form-control'})
    )
    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'ej.: tuemail@ejemplo.com', 'class': 'form-control'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'ej.: 1123445567', 'class': 'form-control'})
    )
    mensaje = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'placeholder': 'Escribí tu mensaje aquí...', 'class': 'form-control'})
    )
