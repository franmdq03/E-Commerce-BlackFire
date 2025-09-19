"""
Modelos para la app 'store'.

Define las entidades principales de la tienda, incluyendo productos, marcas y galerías de imágenes.
"""

from django.db import models
from category.models import Categoria, Subcategoria


class Marca(models.Model):
    """
    Representa una marca de productos.
    """

    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Representa un producto en la tienda.

    """

    codigo = models.CharField(max_length=50, unique=True, null=True, blank=True)
    nombre_producto = models.CharField(max_length=200, null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
    detalle = models.TextField(max_length=500, blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos_categoria",
        null=True,
        blank=True,
    )
    subcategoria = models.ForeignKey(
        Subcategoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos_subcategoria",
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )
    stock = models.IntegerField(null=True, blank=True)
    disponible = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    precio_efectivo = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagen = models.ImageField(upload_to="fotos/productos", blank=True)

    def __str__(self):
        return f"{self.nombre_producto} ({self.codigo})"


class GaleriaProducto(models.Model):
    """
    Representa imágenes adicionales de un producto.
    """

    producto = models.ForeignKey(Producto, default=None, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="fotos/galeria_productos", max_length=255)

    def __str__(self):
        return self.producto.nombre_producto

    class Meta:
        verbose_name = "galeria_producto"
        verbose_name_plural = "galeria_productos"
