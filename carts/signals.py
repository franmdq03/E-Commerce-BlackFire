from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Carrito, ItemCarrito

@receiver(user_logged_in)
def limpiar_carrito_sesion(sender, user, request, **kwargs):
    try:
        carrito = Carrito.objects.get(id_carrito=request.session.session_key)
        ItemCarrito.objects.filter(carrito=carrito, usuario__isnull=True).delete()
    except Carrito.DoesNotExist:
        pass

@receiver(user_logged_out)
def limpiar_carrito_usuario(sender, user, request, **kwargs):
    # Elimina todos los items del carrito asociados al usuario que acaba de cerrar sesión
    ItemCarrito.objects.filter(usuario=user).delete()