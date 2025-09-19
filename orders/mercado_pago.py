"""
Módulo de integración con Mercado Pago.

Define la función para crear una preferencia de pago a partir de una orden
y sus items, utilizando el SDK oficial de Mercado Pago.
"""

import mercadopago
from django.conf import settings

# Inicializa el SDK con el access token configurado en settings.py
sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

def crear_preferencia_mp(orden, items):
    """
    Crea una preferencia de pago en Mercado Pago para la orden proporcionada.

    Parámetros:
    - orden: instancia del modelo Orden que contiene la información de la orden.
    - items: lista de objetos ItemOrden o similar, con producto, cantidad y precio.

    Retorna:
    - URL de init_point para redirigir al usuario a Mercado Pago para pagar.

    Excepciones:
    - Lanza Exception si no se puede crear la preferencia o no se obtiene 'init_point'.
    """
    # Estructura de la preferencia
    preference_data = {
        "items": [],
        "back_urls": {
            "success": "https://7a27d56f09e5.ngrok-free.app/orders/pedido_completo/",
            "failure": "https://7a27d56f09e5.ngrok-free.app/store",
            "pending": "https://7a27d56f09e5.ngrok-free.app/store",
        },
        "auto_return": "approved",  # Retorno automático si se aprueba el pago
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "ticket"},  # Excluye pagos tipo ticket
                {"id": "atm"},     # Excluye pagos vía ATM
            ]
        },
        "installments": 6,  # Número máximo de cuotas
        "external_reference": str(orden.numero_orden),  # Referencia externa para identificar la orden
    }

    # Agregar cada producto de la orden a la preferencia
    for item in items:
        preference_data["items"].append(
            {
                "title": getattr(item.producto, "nombre_producto", "Producto"),
                "quantity": item.cantidad,
                "unit_price": float(item.producto.precio),
                "currency_id": "ARS",
            }
        )

    # Crear la preferencia usando el SDK
    preference_response = sdk.preference().create(preference_data)

    # Verificar que la creación fue exitosa
    if preference_response.get("status") == 201:
        response = preference_response.get("response", {})
        init_point = response.get("init_point")
        if init_point:
            return init_point
        else:
            raise Exception(
                "No se encontró 'init_point' en la respuesta de Mercado Pago"
            )
    else:
        raise Exception(
            f"Error creando preferencia Mercado Pago: {preference_response}"
        )
