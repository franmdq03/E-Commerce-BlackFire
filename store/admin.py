"""
Configuración del admin para la app 'store'.

Permite administrar productos, galerías y marcas desde el panel de Django.
"""

from django.contrib import admin
from .models import Producto, GaleriaProducto, Marca
import admin_thumbnails


# Miniatura para la galería de productos
@admin_thumbnails.thumbnail('imagen')
class GaleriaProductoInline(admin.TabularInline):
    """
    Inline para mostrar imágenes adicionales de cada producto en el admin.
    """
    model = GaleriaProducto
    extra = 1


class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración de la vista de administración de productos.
    """
    prepopulated_fields = {'slug': ('nombre_producto',)}
    list_display = (
        'codigo', 'nombre_producto', 'slug', 'precio_efectivo', 'precio', 'stock',
        'categoria', 'subcategoria', 'marca', 'actualizado_en', 'disponible'
    )
    inlines = [GaleriaProductoInline]
    search_fields = ('codigo', 'nombre_producto', 'marca__nombre')
    list_filter = ('categoria', 'subcategoria', 'disponible', 'marca')


# Registro de modelos en el admin
admin.site.register(Producto, ProductoAdmin)
admin.site.register(GaleriaProducto)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """
    Configuración de la vista de administración de marcas.
    """
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
