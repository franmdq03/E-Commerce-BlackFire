"""
Módulo de integración con Mercado Pago.

Define la función para crear una preferencia de pago a partir de una orden
y sus items, utilizando el SDK oficial de Mercado Pago.
"""

import mercadopago
from django.conf import settings
from decimal import Decimal

# Inicializa el SDK con el access token configurado en settings.py
sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

def crear_preferencia_mp(orden, items):
    """
    Crea una preferencia de pago en Mercado Pago para la orden proporcionada,
    incluyendo el costo de envío como un ítem extra.
    """
    preference_data = {
        "items": [],
        "back_urls": {
            "success": "https://7a27d56f09e5.ngrok-free.app/orders/pedido_completo/",
            "failure": "https://7a27d56f09e5.ngrok-free.app/store",
            "pending": "https://7a27d56f09e5.ngrok-free.app/store",
        },
        "auto_return": "approved",
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "ticket"},
                {"id": "atm"},
            ]
        },
        "installments": 6,
        "external_reference": str(orden.numero_orden),
    }

    # Productos del carrito
    total_productos = Decimal('0')
    for item in items:
        unit_price = Decimal(str(item.producto.precio))
        preference_data["items"].append({
            "title": getattr(item.producto, "nombre_producto", "Producto"),
            "quantity": item.cantidad,
            "unit_price": float(unit_price),
            "currency_id": "ARS",
        })
        total_productos += unit_price * item.cantidad

    # Agregar costo de envío si existe
    costo_envio = orden.total_orden - total_productos
    if costo_envio > 0:
        preference_data["items"].append({
            "title": "Costo de envío",
            "quantity": 1,
            "unit_price": float(costo_envio),
            "currency_id": "ARS",
        })

    # Crear preferencia con Mercado Pago
    preference_response = sdk.preference().create(preference_data)

    if preference_response.get("status") == 201:
        init_point = preference_response.get("response", {}).get("init_point")
        if init_point:
            return init_point
        else:
            raise Exception("No se encontró 'init_point' en la respuesta de Mercado Pago")
    else:
        raise Exception(f"Error creando preferencia Mercado Pago: {preference_response}")
