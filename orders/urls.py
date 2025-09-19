"""
URLs para la app 'orders'.

Define las rutas para realizar pedidos, procesar pagos y mostrar la confirmación de la orden.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Vista para que el usuario complete el formulario y realice la orden
    path('realizar_pedido/', views.realizar_pedido, name='realizar_pedido'),

    # Vista que maneja la integración con Mercado Pago y procesa el pago
    path('pagos/', views.pagos, name='pagos'),

    # Vista de confirmación que se muestra cuando la orden/pago se completó correctamente
    path('pedido_completo/', views.pedido_completo, name='pedido_completo'),
]
