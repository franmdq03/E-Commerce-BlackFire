from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import ItemCarrito
from .forms import FormularioOrden
import datetime
from .models import Orden, Pago, ProductoOrdenado
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .mercado_pago import crear_preferencia_mp
import mercadopago
from django.conf import settings
from django.utils import timezone

def pagos(request):
    # Enviar correo de confirmación de pedido al cliente
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


@login_required(login_url='iniciar_sesion')
def realizar_pedido(request, total=0, cantidad=0):
    usuario_actual = request.user
    items_carrito = ItemCarrito.objects.filter(usuario=usuario_actual, activo=True)
    cantidad_carrito = items_carrito.count()

    if cantidad_carrito <= 0:
        return redirect('tienda')

    for item in items_carrito:
        total += (item.producto.precio * item.cantidad)
        cantidad += item.cantidad

    impuesto = (2 * total) / 100
    total_general = total + impuesto

    if request.method == 'POST':
        formulario = FormularioOrden(request.POST)
        if formulario.is_valid():
            cd = formulario.cleaned_data

            orden = Orden(
                usuario=usuario_actual,
                nombre=cd['nombre'],
                apellido=cd['apellido'],
                correo=cd['correo'],
                telefono=cd['telefono'],
                direccion_1=cd.get('direccion_1', ''),
                direccion_2=cd.get('direccion_2', ''),
                ciudad=cd.get('ciudad', ''),
                provincia=cd.get('provincia', ''),
                pais=cd.get('pais', ''),
                nota_orden=cd.get('nota_orden', ''),
                tipo_entrega=cd['tipo_entrega'],
                total_orden=total_general,
                impuesto=impuesto,
                ip=request.META.get('REMOTE_ADDR', ''),
            )

            if orden.tipo_entrega == 'correo_argentino':
                orden.direccion_envio = cd.get('direccion_envio', '')
                orden.ciudad_envio = cd.get('ciudad_envio', '')
                orden.cp_envio = cd.get('cp_envio', '')
            else:
                orden.direccion_envio = ''
                orden.ciudad_envio = ''
                orden.cp_envio = ''

            orden.save()

            fecha_actual = timezone.now().strftime("%Y%m%d")  # mejor usar timezone
            numero_orden = fecha_actual + str(orden.id)
            orden.numero_orden = numero_orden
            orden.save()

            url_mercado_pago = crear_preferencia_mp(orden, items_carrito)

            # No desactivar carrito aquí. Mejor en confirmación pago.

            return redirect(url_mercado_pago)

        else:
            contexto = {
                'items_carrito': items_carrito,
                'total': total,
                'impuesto': impuesto,
                'total_general': total_general,
                'formulario': formulario,
            }
            return render(request, 'store/checkout.html', contexto)

    else:
        formulario = FormularioOrden()
        contexto = {
            'items_carrito': items_carrito,
            'total': total,
            'impuesto': impuesto,
            'total_general': total_general,
            'formulario': formulario,
        }
        return render(request, 'store/checkout.html', contexto)



sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

@login_required(login_url="iniciar_sesion")
def pedido_completo(request):
    numero_orden = request.GET.get("numero_orden")
    payment_id = request.GET.get("payment_id")

    if not numero_orden or not payment_id:
        return redirect("home")

    try:
        resultado = sdk.payment().get(payment_id)
        datos_pago = resultado["response"]

        if datos_pago["status"] == "approved":
            orden = Orden.objects.get(numero_orden=numero_orden, usuario=request.user)

            if not orden.ordenado:
                pago = Pago.objects.create(
                    usuario=request.user,
                    id_pago=payment_id,
                    metodo_pago=datos_pago["payment_method_id"],
                    monto_pagado=datos_pago["transaction_amount"],
                    estado=datos_pago["status"]
                )

                orden.pago = pago
                orden.ordenado = True
                orden.estado = "Aceptado"
                orden.save()

                items = ItemCarrito.objects.filter(usuario=request.user)
                for item in items:
                    ProductoOrdenado.objects.create(
                        orden=orden,
                        pago=pago,
                        usuario=request.user,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_producto=item.producto.precio
                    )

                items.delete()

            productos_ordenados = ProductoOrdenado.objects.filter(orden=orden)
            subtotal = sum(i.precio_producto * i.cantidad for i in productos_ordenados)

            contexto = {
                "orden": orden,
                "productos_ordenados": productos_ordenados,
                "numero_orden": numero_orden,
                "transID": payment_id,
                "pago": orden.pago,
                "subtotal": subtotal,
            }

            return render(request, "orders/order_complete.html", contexto)

        else:
            return redirect("store")

    except Orden.DoesNotExist:
        return redirect("home")

