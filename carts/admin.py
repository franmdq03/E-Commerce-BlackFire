"""
Admin de la app 'carts' del ecommerce.
Permite gestionar en el panel de administración:
- Carritos de usuario
- Items dentro de cada carrito
"""

from django.contrib import admin
from .models import Carrito, ItemCarrito


class CarritoAdmin(admin.ModelAdmin):
    """Configura la visualización de Carrito en admin."""

    list_display = ("id_carrito", "fecha_agregado")


class ItemCarritoAdmin(admin.ModelAdmin):
    """Configura la visualización de los Items de Carrito en admin."""

    list_display = ("producto", "carrito", "cantidad", "activo")


# Registro de modelos en el panel de administración
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(ItemCarrito, ItemCarritoAdmin)
