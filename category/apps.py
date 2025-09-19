"""
Configuración de la app 'category' para el proyecto.
Define el nombre y el verbose_name que se mostrará en el admin de Django.
"""

from django.apps import AppConfig

class CategoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'
    verbose_name = 'Categoría'
