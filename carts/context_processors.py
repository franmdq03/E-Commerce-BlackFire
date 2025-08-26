from .models import Carrito, ItemCarrito
from .views import _id_carrito

def contador(request):
    total_items = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            carrito = Carrito.objects.filter(id_carrito=_id_carrito(request))
            if request.user.is_authenticated:
                items_carrito = ItemCarrito.objects.all().filter(usuario=request.user)
            else:
                items_carrito = ItemCarrito.objects.all().filter(carrito=carrito[:1])
            for item in items_carrito:
                total_items += item.cantidad
        except Carrito.DoesNotExist:
            total_items = 0
    return dict(total_items=total_items)