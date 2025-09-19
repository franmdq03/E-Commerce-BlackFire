"""
Vistas para la app 'contacto'.

Contienen la lógica para mostrar el formulario de contacto, 
enviar el mensaje por correo y mostrar la página de éxito.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormularioContacto
from django.core.mail import send_mail
from django.conf import settings

def vista_contacto(request):
    """
    Muestra y procesa el formulario de contacto.

    Parámetros:
    - request: objeto HttpRequest.

    Flujo:
    - Si el método es POST:
        - Valida el formulario.
        - Si es válido, extrae los datos y envía un correo al soporte.
        - Muestra un mensaje de éxito y redirige a la página de éxito.
    - Si el método es GET:
        - Muestra el formulario vacío.

    Retorna:
    - Renderiza la plantilla 'contacto/contacto.html' con el formulario.
    """
    if request.method == 'POST':
        form = FormularioContacto(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            telefono = form.cleaned_data['telefono']
            mensaje = form.cleaned_data['mensaje']

            asunto = f"Nuevo mensaje de contacto de {nombre}"
            mensaje_email = f"Nombre: {nombre}\nCorreo: {correo}\nTeléfono: {telefono}\nMensaje:\n{mensaje}"

            send_mail(
                asunto,
                mensaje_email,
                settings.DEFAULT_FROM_EMAIL,  # Remitente configurado
                ['soporte@tudominio.com'],   # Destinatario(s)
                fail_silently=False,
            )

            messages.success(request, '¡Tu mensaje ha sido enviado exitosamente! Nos pondremos en contacto pronto.')
            return redirect('contacto_exito')
    else:
        form = FormularioContacto()
    
    return render(request, 'contacto/contacto.html', {'form': form})

def vista_contacto_exito(request):
    """
    Muestra la página de éxito tras enviar el formulario de contacto.

    Parámetros:
    - request: objeto HttpRequest.

    Retorna:
    - Renderiza la plantilla 'contacto/contacto_exito.html'.
    """
    return render(request, 'contacto/contacto_exito.html')

