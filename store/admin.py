from django.contrib import admin
from .models import Producto, GaleriaProducto, Marca
import admin_thumbnails

@admin_thumbnails.thumbnail('imagen')
class GaleriaProductoInline(admin.TabularInline):
    model = GaleriaProducto
    extra = 1

class ProductoAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre_producto',)}
    list_display = ('codigo', 'nombre_producto', 'slug', 'precio', 'stock', 'categoria', 'subcategoria', 'marca', 'actualizado_en', 'disponible')
    inlines = [GaleriaProductoInline]
    search_fields = ('codigo', 'nombre_producto', 'marca__nombre')
    list_filter = ('categoria', 'subcategoria', 'disponible', 'marca')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(GaleriaProducto)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
