from django.contrib import admin
from .models import Categoria, Subcategoria

class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre_categoria',)}
    list_display = ('id', 'nombre_categoria', 'slug', 'creado_en', 'actualizado_en', 'get_subcategorias')
    search_fields = ('nombre_categoria',)

    def get_subcategorias(self, obj):
        return ", ".join([sub.nombre_categoria for sub in obj.subcategorias.all()]) or "-"
    get_subcategorias.short_description = 'Subcategorías'

class SubcategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre_categoria',)}
    list_display = ('id', 'nombre_categoria', 'slug', 'categoria', 'creado_en', 'actualizado_en')
    search_fields = ('nombre_categoria',)

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Subcategoria, SubcategoriaAdmin)