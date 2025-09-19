"""
Señales de la app 'carts' del ecommerce.
Gestionan la limpieza de items en carritos cuando los usuarios inician o cierran sesión.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Carrito, ItemCarrito


@receiver(user_logged_in)
def limpiar_carrito_sesion(sender, user, request, **kwargs):
    """
    Al iniciar sesión, elimina los items anónimos del carrito
    asociados a la sesión actual.
    """
    try:
        carrito = Carrito.objects.get(id_carrito=request.session.session_key)
        ItemCarrito.objects.filter(carrito=carrito, usuario__isnull=True).delete()
    except Carrito.DoesNotExist:
        pass


@receiver(user_logged_out)
def limpiar_carrito_usuario(sender, user, request, **kwargs):
    """
    Al cerrar sesión, elimina todos los items del carrito asociados al usuario.
    """
    ItemCarrito.objects.filter(usuario=user).delete()
