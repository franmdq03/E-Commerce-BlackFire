"""
Rutas de la app 'carts' del ecommerce.
Define las URLs relacionadas con el carrito de compras, incluyendo:
- Vista del carrito
- Agregar productos
- Quitar productos o cantidades
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.carrito, name='carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('quitar/<int:producto_id>/', views.quitar_del_carrito, name='quitar_del_carrito'),
    path('quitar_item/<int:producto_id>/', views.quitar_item_carrito, name='quitar_item_carrito'),
]
