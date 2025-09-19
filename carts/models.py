"""
Modelos de la app 'carts' del ecommerce.
Define los Carritos de los usuarios y los Items dentro de cada carrito.
"""

from django.db import models
from store.models import Producto
from accounts.models import Account


class Carrito(models.Model):
    """Modelo que representa un carrito de compras."""

    id_carrito = models.CharField(max_length=250, blank=True)
    fecha_agregado = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id_carrito


class ItemCarrito(models.Model):
    """Modelo que representa un item dentro de un carrito."""

    usuario = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, null=True)
    cantidad = models.IntegerField()
    activo = models.BooleanField(default=True)

    def subtotal(self):
        """Calcula el subtotal de este item: precio * cantidad."""
        return self.producto.precio * self.cantidad

    def __str__(self):
        return str(self.producto)
