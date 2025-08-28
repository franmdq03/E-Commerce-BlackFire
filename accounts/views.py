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
    if request.method == "POST":
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            nombre = formulario.cleaned_data["first_name"]
            apellido = formulario.cleaned_data["last_name"]
            telefono = formulario.cleaned_data["phone"]
            correo = formulario.cleaned_data["email"]
            contrasena = formulario.cleaned_data["password"]

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

            # Crear perfil de usuario automáticamente
            UserProfile.objects.create(user=usuario)

            messages.success(request, f'Cuenta creada para {usuario.email}')

            # Preparar email de activación
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
            enviar_correo = EmailMessage(asunto_correo, mensaje, to=[correo])
            enviar_correo.send()

            return redirect("/accounts/iniciar_sesion/?command=verification&email=" + correo)
    else:
        formulario = FormularioRegistro()
    
    contexto = {
        "formulario": formulario,
    }
    return render(request, "accounts/register.html", contexto)


@csrf_exempt
def iniciar_sesion(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")

        # Autenticar usando email (username = correo)
        usuario = auth.authenticate(username=correo, password=contrasena)

        if usuario is not None:
            if usuario.is_active:
                # Asociar items del carrito anónimo al usuario
                try:
                    carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
                    existen_items = ItemCarrito.objects.filter(carrito=carrito).exists()
                    if existen_items:
                        items_carrito = ItemCarrito.objects.filter(carrito=carrito)
                        for item in items_carrito:
                            item.usuario = usuario
                            item.save()
                except Carrito.DoesNotExist:
                    pass

                auth.login(request, usuario)
                messages.success(request, "Has iniciado sesión correctamente.")

                url_referer = request.META.get("HTTP_REFERER")
                try:
                    query = requests.utils.urlparse(url_referer).query
                    params = dict(x.split("=") for x in query.split("&"))
                    if "next" in params:
                        siguiente_pagina = params["next"]
                        return redirect(siguiente_pagina)
                except Exception:
                    pass

                return redirect("home")
            else:
                messages.error(request, "Tu cuenta no está activa. Por favor, activa tu cuenta vía email.")
                return redirect("iniciar_sesion")
        else:
            messages.error(request, "Usuario o contrasena incorrectos. Por favor, intenta nuevamente.")
            return redirect("iniciar_sesion")

    return render(request, "accounts/login.html")


@login_required(login_url="iniciar_sesion")
def cerrar_sesion(request):
    auth.logout(request)
    messages.success(request, "Has cerrado sesión.")
    return redirect("iniciar_sesion")


def activar(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        messages.success(request, "¡Felicidades! Tu cuenta ha sido activada.")
        return redirect("iniciar_sesion")
    else:
        messages.error(request, "Enlace de activación inválido")
        return redirect("registrar")



@login_required(login_url='iniciar_sesion')
def panel(request):
    ordenes = Orden.objects.order_by('-creado_en').filter(usuario_id=request.user.id, ordenado=True)
    cantidad_ordenes = ordenes.count()

    try:
        perfil_usuario = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        perfil_usuario = None  # o crear uno aquí mismo, o manejar sin perfil

    contexto = {
        'cantidad_ordenes': cantidad_ordenes,
        'perfil_usuario': perfil_usuario,
    }
    return render(request, 'accounts/dashboard.html', contexto)


def olvido_contrasena(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            usuario = Account.objects.get(email__exact=email)
            sitio_actual = get_current_site(request)
            asunto_correo = "Restablece tu contrasena"
            mensaje = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "usuario": usuario,
                    "dominio": sitio_actual,
                    "uid": urlsafe_base64_encode(force_bytes(usuario.pk)),
                    "token": default_token_generator.make_token(usuario),
                },
            )
            enviar_correo = EmailMessage(asunto_correo, mensaje, to=[email])
            enviar_correo.send()
            messages.success(
                request, "Se ha enviado un correo para restablecer la contrasena."
            )
            return redirect("iniciar_sesion")
        else:
            messages.error(request, "¡La cuenta no existe!")
            return redirect("olvido_contrasena")
    return render(request, "accounts/forgotPassword.html")


def validar_restablecer_contrasena(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        request.session["uid"] = uid
        messages.success(request, "Por favor restablece tu contrasena")
        return redirect("restablecer_contrasena")
    else:
        messages.error(request, "¡Este enlace ha expirado!")
        return redirect("iniciar_sesion")


def restablecer_contrasena(request):
    if request.method == "POST":
        contrasena = request.POST["contrasena"]
        confirmar_contrasena = request.POST["confirmar_contrasena"]

        if contrasena == confirmar_contrasena:
            uid = request.session.get("uid")
            usuario = Account.objects.get(pk=uid)
            usuario.set_password(contrasena)
            usuario.save()
            messages.success(request, "contrasena restablecida correctamente")
            return redirect("iniciar_sesion")
        else:
            messages.error(request, "¡Las contrasenas no coinciden!")
            return redirect("restablecer_contrasena")
    else:
        return render(request, "accounts/resetPassword.html")


@login_required(login_url="iniciar_sesion")
def mis_ordenes(request):
    ordenes = Orden.objects.filter(usuario=request.user, ordenado=True).order_by(
        "-creado_en"
    )
    contexto = {
        "ordenes": ordenes,
    }
    return render(request, "accounts/my_orders.html", contexto)


@login_required(login_url="iniciar_sesion")
def editar_perfil(request):
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
    contexto = {
        "formulario_usuario": formulario_usuario,
        "formulario_perfil": formulario_perfil,
        "perfil_usuario": perfil_usuario,
    }
    return render(request, "accounts/edit_profile.html", contexto)


@login_required(login_url="iniciar_sesion")
def cambiar_contrasena(request):
    if request.method == "POST":
        contrasena_actual = request.POST["contrasena_actual"]
        nueva_contrasena = request.POST["nueva_contrasena"]
        confirmar_contrasena = request.POST["confirmar_contrasena"]

        usuario = Account.objects.get(username__exact=request.user.username)

        if nueva_contrasena == confirmar_contrasena:
            exito = usuario.check_password(contrasena_actual)
            if exito:
                usuario.set_password(nueva_contrasena)
                usuario.save()
                messages.success(request, "contrasena actualizada correctamente.")
                return redirect("cambiar_contrasena")
            else:
                messages.error(request, "Por favor ingresa la contrasena actual válida")
                return redirect("cambiar_contrasena")
        else:
            messages.error(request, "¡Las contrasenas no coinciden!")
            return redirect("cambiar_contrasena")
    return render(request, "accounts/change_password.html")


@login_required(login_url="iniciar_sesion")
def detalle_orden(request, id_orden):
    detalle_orden = ProductoOrdenado.objects.filter(orden__numero_orden=id_orden)
    orden = Orden.objects.get(numero_orden=id_orden)
    subtotal = 0
    for i in detalle_orden:
        subtotal += i.precio_producto * i.cantidad

    contexto = {
        "detalle_orden": detalle_orden,
        "orden": orden,
        "subtotal": subtotal,
    }
    return render(request, "accounts/order_detail.html", contexto)
