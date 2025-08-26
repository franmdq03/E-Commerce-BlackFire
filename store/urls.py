from django.urls import path
from . import views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('categoria/<slug:categoria_slug>/', views.tienda, name='productos_por_categoria'),
    path('categoria/<slug:categoria_slug>/subcategoria/<slug:subcategoria_slug>/', views.tienda, name='productos_por_subcategoria'),
    path('marca/<slug:marca_slug>/', views.tienda, name='productos_por_marca'),
    path('categoria/<slug:categoria_slug>/<slug:producto_slug>/', views.detalle_producto, name='detalle_producto'),
    path('buscar/', views.buscar, name='buscar'),
]
