"""
URLs para la app 'store'.

Define las rutas principales de la tienda, incluyendo listado de productos,
detalle de producto, búsqueda y secciones por categoría, subcategoría o marca.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Página principal de la tienda
    path('', views.tienda, name='tienda'),

    # Listado de productos por categoría
    path('categoria/<slug:categoria_slug>/', views.tienda, name='productos_por_categoria'),

    # Listado de productos por subcategoría
    path('categoria/<slug:categoria_slug>/subcategoria/<slug:subcategoria_slug>/', views.tienda, name='productos_por_subcategoria'),

    # Listado de productos por marca
    path('marca/<slug:marca_slug>/', views.tienda, name='productos_por_marca'),

    # Página de detalle de un producto específico
    path('categoria/<slug:categoria_slug>/<slug:producto_slug>/', views.detalle_producto, name='detalle_producto'),

    # Ruta para búsqueda de productos
    path('buscar/', views.buscar, name='buscar'),

    # Página de comunidad
    path("comunidad/", views.comunidad, name="comunidad"),
]
