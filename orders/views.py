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
import requests
from django.http import JsonResponse

from carts.models import ItemCarrito
from .forms import FormularioOrden
from .models import Orden, Pago, ProductoOrdenado, BandaEnvio
from .mercado_pago import crear_preferencia_mp
from decimal import Decimal


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
    usuario_actual = request.user
    items_carrito = ItemCarrito.objects.filter(usuario=usuario_actual, activo=True)

    if not items_carrito.exists():
        return redirect("tienda")

    total_productos = sum(item.producto.precio * item.cantidad for item in items_carrito)

    if request.method == "POST":
        formulario = FormularioOrden(request.POST)
        if formulario.is_valid():
            cd = formulario.cleaned_data

            # 🔹 Tomamos el costo de envío del formulario (hidden input)
            costo_envio = float(request.POST.get("costo_envio", 0))
            costo_envio = Decimal(str(costo_envio))
            total = total_productos + costo_envio

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

            if orden.tipo_entrega == "domicilio" or orden.tipo_entrega == "correo_argentino":
                orden.direccion_envio = cd.get("direccion_envio", "")
                orden.ciudad_envio = cd.get("ciudad_envio", "")
                orden.cp_envio = cd.get("cp_envio", "")

            orden.save()
            orden.numero_orden = timezone.now().strftime("%Y%m%d") + str(orden.id)
            orden.save()

            url_mercado_pago = crear_preferencia_mp(orden, items_carrito)
            return redirect(url_mercado_pago)
    else:
        formulario = FormularioOrden()
        costo_envio = 0
        total = total_productos

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
    
    # Coordenadas del local (puedes reemplazar por las tuyas)
COORDENADAS_LOCAL = (-38.0055, -57.5426)  # Mar del Plata como ejemplo

def calcular_envio(request):
    """Calcula el costo de envío en base a la distancia entre el local y la ciudad destino."""
    destino = request.GET.get('destino')

    if not destino:
        return JsonResponse({'error': 'No se proporcionó una ciudad de destino.'}, status=400)

    try:
        # 1️⃣ Obtener coordenadas del destino (API gratuita de Nominatim)
        geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={destino},Argentina"
        geo_resp = requests.get(geo_url, headers={'User-Agent': 'ecommerce-envio/1.0'})
        geo_data = geo_resp.json()

        if not geo_data:
            return JsonResponse({'error': 'No se encontró la ubicación ingresada.'}, status=404)

        lat_destino = float(geo_data[0]['lat'])
        lon_destino = float(geo_data[0]['lon'])

        # 2️⃣ Calcular distancia entre local y destino (API OSRM gratuita)
        osrm_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{COORDENADAS_LOCAL[1]},{COORDENADAS_LOCAL[0]};{lon_destino},{lat_destino}?overview=false"
        )
        osrm_resp = requests.get(osrm_url)
        osrm_data = osrm_resp.json()

        if "routes" not in osrm_data or not osrm_data["routes"]:
            return JsonResponse({'error': 'No se pudo calcular la distancia.'}, status=500)

        distancia_km = osrm_data["routes"][0]["distance"] / 1000.0  # metros → km

        # 3️⃣ Lógica de bandas (dinámica desde la DB)      
        bandas = BandaEnvio.objects.order_by('distancia_hasta')
        if not bandas.exists():
            # Si no hay bandas configuradas en el admin, retorna un error
            return JsonResponse({'error': 'Los costos de envío no están configurados.'}, status=500)

        costo_envio = 0
        for banda in bandas:
            if distancia_km <= banda.distancia_hasta:
                costo_envio = banda.costo
                break # Encuentra la primera banda que coincide y sale
        else:
            # Si la distancia es mayor que todas las bandas (ej: 500km),
            # usa el costo de la última banda configurada.
            costo_envio = bandas.last().costo

        return JsonResponse({
            'costo_envio': costo_envio,
            'distancia_km': round(distancia_km, 1),
            'mensaje': f"Distancia aproximada: {round(distancia_km, 1)} km"
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)