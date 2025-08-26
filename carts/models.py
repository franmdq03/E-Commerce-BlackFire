from django.db import models
from store.models import Producto
from accounts.models import Account

class Carrito(models.Model):
    id_carrito = models.CharField(max_length=250, blank=True)
    fecha_agregado = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.id_carrito

class ItemCarrito(models.Model):
    usuario = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, null=True)
    cantidad = models.IntegerField()
    activo = models.BooleanField(default=True)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __unicode__(self):
        return self.producto
