"""
Context processor para la app 'carts'.
Calcula el total de items en el carrito del usuario, 
para mostrarlo en el header u otras partes del ecommerce.
"""

from .models import Carrito, ItemCarrito
from .views import _id_carrito


def contador(request):
    """
    Devuelve un diccionario con el total de items en el carrito.
    - Ignora rutas del admin.
    - Si el usuario está autenticado, cuenta sus items.
    - Si no, cuenta los items del carrito anónimo asociado a la sesión.
    """
    total_items = 0
    if 'admin' in request.path:
        return {}
    try:
        carrito = Carrito.objects.filter(id_carrito=_id_carrito(request))
        if request.user.is_authenticated:
            items_carrito = ItemCarrito.objects.filter(usuario=request.user)
        else:
            items_carrito = ItemCarrito.objects.filter(carrito=carrito[:1])
        for item in items_carrito:
            total_items += item.cantidad
    except Carrito.DoesNotExist:
        total_items = 0
    return dict(total_items=total_items)
