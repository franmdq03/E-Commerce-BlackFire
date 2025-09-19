"""
Configuración de administración para la app 'category'.
Gestiona la visualización y edición de Categorías y Subcategorías en el admin de Django.
"""

from django.contrib import admin
from .models import Categoria, Subcategoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Categorías.
    - prepopulated_fields: genera automáticamente el slug a partir del nombre.
    - list_display: campos que se muestran en la lista.
    - search_fields: permite búsqueda por nombre de categoría.
    """
    prepopulated_fields = {'slug': ('nombre_categoria',)}
    list_display = ('id', 'nombre_categoria', 'slug', 'creado_en', 'actualizado_en', 'get_subcategorias')
    search_fields = ('nombre_categoria',)

    def get_subcategorias(self, obj):
        """
        Devuelve las subcategorías asociadas a la categoría como string separado por comas.
        """
        return ", ".join([sub.nombre_categoria for sub in obj.subcategorias.all()]) or "-"
    get_subcategorias.short_description = 'Subcategorías'


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Subcategorías.
    - prepopulated_fields: genera automáticamente el slug a partir del nombre.
    - list_display: campos que se muestran en la lista.
    - search_fields: permite búsqueda por nombre de subcategoría.
    """
    prepopulated_fields = {'slug': ('nombre_categoria',)}
    list_display = ('id', 'nombre_categoria', 'slug', 'categoria', 'creado_en', 'actualizado_en')
    search_fields = ('nombre_categoria',)
