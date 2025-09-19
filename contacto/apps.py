"""
Configuración de la app 'contacto'.

Define los ajustes y metadatos de la aplicación de contacto.
"""

from django.apps import AppConfig


class ContactoConfig(AppConfig):
    # Campo por defecto para las claves primarias grandes
    default_auto_field = 'django.db.models.BigAutoField'

    # Nombre interno de la app
    name = 'contacto'

    # Nombre legible en el panel de administración
    verbose_name = 'Contacto'

