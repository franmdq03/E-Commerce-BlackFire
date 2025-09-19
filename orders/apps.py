"""
Configuración de la app 'orders' para Django.

Define el nombre de la app y el tipo de campo por defecto para los modelos.
"""

from django.apps import AppConfig

class OrdenesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    verbose_name = 'Órdenes'

