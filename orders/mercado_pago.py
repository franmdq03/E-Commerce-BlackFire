import mercadopago
from django.conf import settings

sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)


def crear_preferencia_mp(orden, items):

    preference_data = {
        "items": [],
        "back_urls": {
            "success": "https://118c2186930f.ngrok-free.app/orders/pedido_completo/",
            "failure": "https://118c2186930f.ngrok-free.app/store",
            "pending": "https://118c2186930f.ngrok-free.app/store",
        },
        "auto_return": "approved",  # esto indica que redirige automáticamente si es aprobado
        "payment_methods": {
            "excluded_payment_types": [{"id": "ticket"}, {"id": "atm"}]
        },
        "installments": 6,
        "external_reference": str(orden.numero_orden),
    }

    for item in items:
        preference_data["items"].append(
            {
                "title": getattr(item.producto, "nombre_producto", "Producto"),
                "quantity": item.cantidad,
                "unit_price": float(item.producto.precio),
                "currency_id": "ARS",
            }
        )

    preference_response = sdk.preference().create(preference_data)

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
