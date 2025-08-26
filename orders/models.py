from django.db import models
from accounts.models import Account
from store.models import Producto

class Pago(models.Model):
    usuario = models.ForeignKey(Account, on_delete=models.CASCADE)
    id_pago = models.CharField(max_length=100)
    metodo_pago = models.CharField(max_length=100)
    monto_pagado = models.CharField(max_length=100) # total pagado
    estado = models.CharField(max_length=100)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id_pago

class Orden(models.Model):
    ESTADO = (
        ('Nuevo', 'Nuevo'),
        ('Aceptado', 'Aceptado'),
        ('Completado', 'Completado'),
        ('Cancelado', 'Cancelado'),
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
    impuesto = models.FloatField()
    estado = models.CharField(max_length=10, choices=ESTADO, default='Nuevo')
    ip = models.CharField(blank=True, max_length=20)
    ordenado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    ENTREGA_CHOICES = (
        ('andreani', 'Envío por Andreani'),
        ('retiro', 'Retiro en local'),
    )

    tipo_entrega = models.CharField(
        max_length=20,
        choices=ENTREGA_CHOICES,
        default='andreani'
    )
    direccion_envio = models.CharField(max_length=255, blank=True, null=True)
    ciudad_envio = models.CharField(max_length=100, blank=True, null=True)
    cp_envio = models.CharField(max_length=20, blank=True, null=True)

    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def direccion_completa(self):
        return f'{self.direccion_1} {self.direccion_2}'

    def __str__(self):
        return self.nombre

class ProductoOrdenado(models.Model):
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