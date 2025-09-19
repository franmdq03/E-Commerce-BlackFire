"""
Modelos para la app 'category'.

Define:
- Categoria: categorías principales de productos, con slug, imagen y fecha de creación/actualización.
- Subcategoria: subcategorías relacionadas a una categoría, permitiendo organizar productos jerárquicamente.
"""

from django.urls import reverse
from django.db import models

class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def get_url(self):
        return reverse('productos_por_categoria', args=[self.slug])

    def __str__(self):
        return self.nombre_categoria

class Subcategoria(models.Model):
    nombre_categoria = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, related_name='subcategorias', on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_categoria} ({self.categoria.nombre_categoria})"
