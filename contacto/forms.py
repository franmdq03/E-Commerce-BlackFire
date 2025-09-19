"""
Formulario de contacto para la app 'contacto'.

Define los campos que el usuario debe completar para enviar un mensaje.
Incluye validación básica y placeholders para mejorar la experiencia.
"""

from django import forms

class FormularioContacto(forms.Form):
    # Nombre completo del usuario
    nombre = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'ej.: María Pérez', 
            'class': 'form-control'
        })
    )

    # Correo electrónico
    correo = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'ej.: tuemail@ejemplo.com', 
            'class': 'form-control'
        })
    )

    # Teléfono (opcional)
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'ej.: 1123445567', 
            'class': 'form-control'
        })
    )

    # Mensaje que desea enviar el usuario
    mensaje = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={
            'placeholder': 'Escribí tu mensaje aquí...', 
            'class': 'form-control'
        })
    )

