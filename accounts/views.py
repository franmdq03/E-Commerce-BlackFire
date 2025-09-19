"""
Views de la app 'accounts' del ecommerce.
Incluye:
- Registro, activación y login de usuarios
- Recuperación y cambio de contraseña
- Gestión de perfil y edición de usuario
- Visualización de órdenes y detalle de órdenes
- Asociación de carrito anónimo al iniciar sesión
"""

from django.shortcuts import render, redirect, get_object_or_404
from .forms import FormularioRegistro, FormularioUsuario, FormularioPerfilUsuario
from .models import Account, UserProfile
from orders.models import Orden, ProductoOrdenado
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _id_carrito
from carts.models import Carrito, ItemCarrito
import requests

from django.views.decorators.csrf import csrf_exempt


def registrar(request):
    """Registra un usuario, crea perfil y envía email de activación."""
    if request.method == "POST":
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["first_name"]
            apellido = formulario.cleaned_data["last_name"]
            telefono = formulario.cleaned_data["phone"]
            correo = formulario.cleaned_data["email"]
            contrasena = formulario.cleaned_data["password"]

            # Generar username único
            nombre_usuario = correo.split("@")[0]
            base_username = nombre_usuario
            contador = 1
            while Account.objects.filter(username=base_username).exists():
                base_username = f"{nombre_usuario}{contador}"
                contador += 1

            usuario = Account.objects.create_user(
                first_name=nombre,
                last_name=apellido,
                username=base_username,
                email=correo,
                password=contrasena,
            )
            usuario.phone = telefono
            usuario.save()

            # Crear perfil automáticamente
            UserProfile.objects.create(user=usuario)

            messages.success(request, f"Cuenta creada para {usuario.email}")

            # Enviar email de activación
            dominio = f"{request.scheme}://{request.get_host()}"
            asunto_correo = "Por favor activa tu cuenta"
            mensaje = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "usuario": usuario,
                    "dominio": dominio,
                    "uid": urlsafe_base64_encode(force_bytes(usuario.pk)),
                    "token": default_token_generator.make_token(usuario),
                },
            )
            EmailMessage(asunto_correo, mensaje, to=[correo]).send()
            return redirect(
                "/accounts/iniciar_sesion/?command=verification&email=" + correo
            )
    else:
        formulario = FormularioRegistro()

    return render(request, "accounts/register.html", {"formulario": formulario})


@csrf_exempt
def iniciar_sesion(request):
    """Autentica usuario y asocia carrito anónimo si existe."""
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        usuario = auth.authenticate(username=correo, password=contrasena)

        if usuario:
            if usuario.is_active:
                try:
                    carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
                    items_carrito = ItemCarrito.objects.filter(carrito=carrito)
                    for item in items_carrito:
                        item.usuario = usuario
                        item.save()
                except Carrito.DoesNotExist:
                    pass

                auth.login(request, usuario)
                messages.success(request, "Has iniciado sesión correctamente.")

                # Redirigir a la página siguiente si existe
                url_referer = request.META.get("HTTP_REFERER")
                try:
                    query = requests.utils.urlparse(url_referer).query
                    params = dict(x.split("=") for x in query.split("&"))
                    if "next" in params:
                        return redirect(params["next"])
                except Exception:
                    pass
                return redirect("home")
            else:
                messages.error(request, "Tu cuenta no está activa. Actívala vía email.")
        else:
            messages.error(request, "Usuario o contrasena incorrectos.")

        return redirect("iniciar_sesion")

    return render(request, "accounts/login.html")


@login_required(login_url="iniciar_sesion")
def cerrar_sesion(request):
    """Cierra sesión del usuario."""
    auth.logout(request)
    messages.success(request, "Has cerrado sesión.")
    return redirect("iniciar_sesion")


def activar(request, uidb64, token):
    """Activa cuenta desde enlace enviado por email."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        usuario = None

    if usuario and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        messages.success(request, "¡Cuenta activada!")
        return redirect("iniciar_sesion")
    messages.error(request, "Enlace de activación inválido")
    return redirect("registrar")


@login_required(login_url="iniciar_sesion")
def panel(request):
    """Dashboard del usuario con órdenes y perfil."""
    ordenes = Orden.objects.filter(usuario_id=request.user.id, ordenado=True).order_by(
        "-creado_en"
    )
    perfil_usuario = UserProfile.objects.filter(user_id=request.user.id).first()
    return render(
        request,
        "accounts/dashboard.html",
        {
            "cantidad_ordenes": ordenes.count(),
            "perfil_usuario": perfil_usuario,
        },
    )


def olvido_contrasena(request):
    """Envía email para restablecer contraseña si la cuenta existe."""
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            usuario = Account.objects.get(email=email)
            sitio_actual = get_current_site(request)
            asunto = "Restablece tu contrasena"
            mensaje = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "usuario": usuario,
                    "dominio": sitio_actual,
                    "uid": urlsafe_base64_encode(force_bytes(usuario.pk)),
                    "token": default_token_generator.make_token(usuario),
                },
            )
            EmailMessage(asunto, mensaje, to=[email]).send()
            messages.success(
                request, "Se ha enviado un correo para restablecer la contrasena."
            )
            return redirect("iniciar_sesion")
        messages.error(request, "¡La cuenta no existe!")
        return redirect("olvido_contrasena")
    return render(request, "accounts/forgotPassword.html")


def validar_restablecer_contrasena(request, uidb64, token):
    """Valida enlace de restablecimiento y redirige a formulario."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        usuario = None

    if usuario and default_token_generator.check_token(usuario, token):
        request.session["uid"] = uid
        messages.success(request, "Por favor restablece tu contrasena")
        return redirect("restablecer_contrasena")
    messages.error(request, "¡Este enlace ha expirado!")
    return redirect("iniciar_sesion")


def restablecer_contrasena(request):
    """Permite restablecer contraseña desde sesión."""
    if request.method == "POST":
        contrasena = request.POST["contrasena"]
        confirmar = request.POST["confirmar_contrasena"]
        if contrasena == confirmar:
            uid = request.session.get("uid")
            usuario = Account.objects.get(pk=uid)
            usuario.set_password(contrasena)
            usuario.save()
            messages.success(request, "Contraseña restablecida correctamente")
            return redirect("iniciar_sesion")
        messages.error(request, "¡Las contrasenas no coinciden!")
        return redirect("restablecer_contrasena")
    return render(request, "accounts/resetPassword.html")


@login_required(login_url="iniciar_sesion")
def mis_ordenes(request):
    """Lista todas las órdenes del usuario."""
    ordenes = Orden.objects.filter(usuario=request.user, ordenado=True).order_by(
        "-creado_en"
    )
    return render(request, "accounts/my_orders.html", {"ordenes": ordenes})


@login_required(login_url="iniciar_sesion")
def editar_perfil(request):
    """Permite al usuario editar su perfil y datos personales."""
    perfil_usuario = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        formulario_usuario = FormularioUsuario(request.POST, instance=request.user)
        formulario_perfil = FormularioPerfilUsuario(
            request.POST, request.FILES, instance=perfil_usuario
        )
        if formulario_usuario.is_valid() and formulario_perfil.is_valid():
            formulario_usuario.save()
            formulario_perfil.save()
            messages.success(request, "Tu perfil ha sido actualizado.")
            return redirect("editar_perfil")
    else:
        formulario_usuario = FormularioUsuario(instance=request.user)
        formulario_perfil = FormularioPerfilUsuario(instance=perfil_usuario)

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "formulario_usuario": formulario_usuario,
            "formulario_perfil": formulario_perfil,
            "perfil_usuario": perfil_usuario,
        },
    )


@login_required(login_url="iniciar_sesion")
def cambiar_contrasena(request):
    """Permite al usuario cambiar su contraseña actual."""
    if request.method == "POST":
        actual = request.POST["contrasena_actual"]
        nueva = request.POST["nueva_contrasena"]
        confirmar = request.POST["confirmar_contrasena"]
        usuario = Account.objects.get(username=request.user.username)
        if nueva == confirmar:
            if usuario.check_password(actual):
                usuario.set_password(nueva)
                usuario.save()
                messages.success(request, "Contraseña actualizada correctamente.")
            else:
                messages.error(request, "Ingresa la contraseña actual válida")
        else:
            messages.error(request, "¡Las contrasenas no coinciden!")
        return redirect("cambiar_contrasena")
    return render(request, "accounts/change_password.html")


@login_required(login_url="iniciar_sesion")
def detalle_orden(request, id_orden):
    """Muestra detalle de una orden específica con subtotal."""
    detalle_orden = ProductoOrdenado.objects.filter(orden__numero_orden=id_orden)
    orden = Orden.objects.get(numero_orden=id_orden)
    subtotal = sum(i.precio_producto * i.cantidad for i in detalle_orden)
    return render(
        request,
        "accounts/order_detail.html",
        {
            "detalle_orden": detalle_orden,
            "orden": orden,
            "subtotal": subtotal,
        },
    )
