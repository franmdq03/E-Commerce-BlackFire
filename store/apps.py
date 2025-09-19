"""
Configuración de la app 'store'.

Define el nombre de la app y la configuración por defecto para el admin de Django.
"""

from django.apps import AppConfig


class TiendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'Tienda'

