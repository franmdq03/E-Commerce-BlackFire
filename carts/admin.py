from django.contrib import admin
from .models import Carrito, ItemCarrito

class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id_carrito', 'fecha_agregado')

class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'carrito', 'cantidad', 'activo')

admin.site.register(Carrito, CarritoAdmin)
admin.site.register(ItemCarrito, ItemCarritoAdmin)
