from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FormularioContacto  # Importamos el formulario renombrado
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

def vista_contacto(request):
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
                settings.DEFAULT_FROM_EMAIL,  # Remitente (el que configuraste)
                ['soporte@tudominio.com'],   # Destinatario(s)
                fail_silently=False,
            )

            messages.success(request, '¡Tu mensaje ha sido enviado exitosamente! Nos pondremos en contacto pronto.')
            return redirect('contacto_exito')
    else:
        form = FormularioContacto()
    return render(request, 'contacto/contacto.html', {'form': form})

def vista_contacto_exito(request):
    # Vista simple para mostrar un mensaje de éxito
    return render(request, 'contacto/contacto_exito.html')
