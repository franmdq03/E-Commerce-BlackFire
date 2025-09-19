"""
Configuración del panel de administración para la app 'orders'.

Registra los modelos Pago, Orden y ProductoOrdenado para que sean gestionables desde el admin de Django.
"""

from django.contrib import admin
from .models import Pago, Orden, ProductoOrdenado

# Registro de modelos en el admin
admin.site.register(Pago)
admin.site.register(Orden)
admin.site.register(ProductoOrdenado)
