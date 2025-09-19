"""
Vistas para la app 'orders'.

Incluye la lógica para:
- Realizar un pedido (checkout)
- Procesar pagos con Mercado Pago
- Mostrar la confirmación de la orden
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import mercadopago

from carts.models import ItemCarrito
from .forms import FormularioOrden
from .models import Orden, Pago, ProductoOrdenado
from .mercado_pago import crear_preferencia_mp


sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


def pagos(request):
    """
    Envia un correo de confirmación al cliente con los detalles del pedido.
    Retorna un JsonResponse con el número de orden y el ID de pago.
    """
    asunto_correo = "¡Gracias por tu pedido!"
    mensaje = render_to_string(
        "orders/order_recieved_email.html",
        {
            "usuario": request.user,
            "orden": Orden,
        },
    )
    para_correo = request.user.correo
    enviar_correo = EmailMessage(asunto_correo, mensaje, to=[para_correo])
    enviar_correo.send()

    data = {
        "numero_orden": Orden.numero_orden,
        "transID": Pago.id_pago,
    }
    return JsonResponse(data)


@csrf_exempt
@login_required(login_url="iniciar_sesion")
def realizar_pedido(request):
    """
    Permite al usuario completar su pedido mediante un formulario de checkout.
    Si el formulario es válido, crea la orden y redirige a Mercado Pago para procesar el pago.
    """
    usuario_actual = request.user
    items_carrito = ItemCarrito.objects.filter(usuario=usuario_actual, activo=True)

    if not items_carrito.exists():
        return redirect("tienda")

    total = sum(item.producto.precio * item.cantidad for item in items_carrito)

    if request.method == "POST":
        formulario = FormularioOrden(request.POST)
        if formulario.is_valid():
            cd = formulario.cleaned_data

            orden = Orden(
                usuario=usuario_actual,
                nombre=cd["nombre"],
                apellido=cd["apellido"],
                correo=cd["correo"],
                telefono=cd["telefono"],
                direccion_1=cd.get("direccion_1", ""),
                direccion_2=cd.get("direccion_2", ""),
                ciudad=cd.get("ciudad", ""),
                provincia=cd.get("provincia", ""),
                pais=cd.get("pais", ""),
                nota_orden=cd.get("nota_orden", ""),
                tipo_entrega=cd["tipo_entrega"],
                total_orden=total,
                ip=request.META.get("REMOTE_ADDR", ""),
            )

            # Campos adicionales si el tipo de entrega es envío
            if orden.tipo_entrega == "correo_argentino":
                orden.direccion_envio = cd.get("direccion_envio", "")
                orden.ciudad_envio = cd.get("ciudad_envio", "")
                orden.cp_envio = cd.get("cp_envio", "")

            orden.save()
            orden.numero_orden = timezone.now().strftime("%Y%m%d") + str(orden.id)
            orden.save()

            # Crear preferencia de pago unificada para Mercado Pago
            url_mercado_pago = crear_preferencia_mp(orden, items_carrito)
            return redirect(url_mercado_pago)
    else:
        formulario = FormularioOrden()

    return render(
        request,
        "store/checkout.html",
        {
            "items_carrito": items_carrito,
            "total": total,
            "formulario": formulario,
        },
    )


@csrf_exempt
@login_required(login_url="iniciar_sesion")
def pedido_completo(request):
    """
    Confirma el pedido una vez aprobado el pago en Mercado Pago.
    Crea registros de pago y productos ordenados, actualiza stock y elimina el carrito.
    """
    numero_orden = request.GET.get("external_reference")
    payment_id = request.GET.get("payment_id")

    if not numero_orden or not payment_id:
        return redirect("home")

    try:
        resultado = sdk.payment().get(payment_id)
        datos_pago = resultado["response"]

        if datos_pago["status"] != "approved":
            return redirect("store")

        orden = Orden.objects.get(numero_orden=numero_orden, usuario=request.user)

        if not orden.ordenado:
            # Crear registro de pago
            pago = Pago.objects.create(
                usuario=request.user,
                id_pago=payment_id,
                metodo_pago=datos_pago["payment_method_id"],
                monto_pagado=datos_pago["transaction_amount"],
                estado=datos_pago["status"],
            )

            # Actualizar orden
            orden.pago = pago
            orden.ordenado = True
            orden.estado = "Aceptado"
            orden.save()

            # Crear productos ordenados y actualizar stock
            items = ItemCarrito.objects.filter(usuario=request.user)
            for item in items:
                ProductoOrdenado.objects.create(
                    orden=orden,
                    pago=pago,
                    usuario=request.user,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_producto=float(item.producto.precio),
                )
                item.producto.stock -= item.cantidad
                item.producto.save()

            # Limpiar carrito
            items.delete()

        productos_ordenados = ProductoOrdenado.objects.filter(orden=orden)
        orden.total_orden = sum(
            i.precio_producto * i.cantidad for i in productos_ordenados
        )
        orden.save()

        return render(
            request,
            "orders/order_complete.html",
            {
                "orden": orden,
                "productos_ordenados": productos_ordenados,
                "numero_orden": numero_orden,
                "transID": payment_id,
                "pago": orden.pago,
            },
        )

    except Orden.DoesNotExist:
        return redirect("home")
