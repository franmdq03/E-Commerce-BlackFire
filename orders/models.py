from django.db import models
from accounts.models import Account
from store.models import Producto


class Pago(models.Model):
    """
    Representa un pago realizado por un usuario.
    Contiene información básica como método, monto, estado y fecha de creación.
    """
    
    usuario = models.ForeignKey(Account, on_delete=models.CASCADE)
    id_pago = models.CharField(max_length=100)
    metodo_pago = models.CharField(max_length=100)
    monto_pagado = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id_pago


class Orden(models.Model):
    """
    Representa una orden de compra de un usuario.
    Contiene información de facturación, tipo de entrega, estado de la orden y total.
    Puede estar asociada a un pago.
    """

    ESTADO = (
        ("Nuevo", "Nuevo"),
        ("Aceptado", "Aceptado"),
        ("Completado", "Completado"),
        ("Cancelado", "Cancelado"),
    )

    ENTREGA_CHOICES = (
        ("andreani", "Envío por Andreani"),
        ("retiro", "Retiro en local"),
    )

    usuario = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, blank=True, null=True)
    numero_orden = models.CharField(max_length=20)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(max_length=50)
    direccion_1 = models.CharField(max_length=50)
    direccion_2 = models.CharField(max_length=50, blank=True)
    pais = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    nota_orden = models.CharField(max_length=100, blank=True)
    total_orden = models.FloatField()
    estado = models.CharField(max_length=10, choices=ESTADO, default="Nuevo")
    ip = models.CharField(blank=True, max_length=20)
    ordenado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    tipo_entrega = models.CharField(
        max_length=20, choices=ENTREGA_CHOICES, default="andreani"
    )
    direccion_envio = models.CharField(max_length=255, blank=True, null=True)
    ciudad_envio = models.CharField(max_length=100, blank=True, null=True)
    cp_envio = models.CharField(max_length=20, blank=True, null=True)

    def nombre_completo(self):
        """Devuelve el nombre completo del usuario que realiza la orden."""
        return f"{self.nombre} {self.apellido}"

    def direccion_completa(self):
        """Devuelve la dirección completa de facturación."""
        return f"{self.direccion_1} {self.direccion_2}"

    def __str__(self):
        return self.nombre


class ProductoOrdenado(models.Model):
    """
    Representa un producto específico dentro de una orden.
    Contiene información de cantidad, precio y estado del producto.
    Está asociado a un usuario, un pago y una orden.
    """

    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, blank=True, null=True)
    usuario = models.ForeignKey(Account, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_producto = models.FloatField()
    ordenado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.producto.nombre_producto
