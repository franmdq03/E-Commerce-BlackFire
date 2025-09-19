"""
Configuración de la app 'carts' del ecommerce.
Define la app, el tipo de campo por defecto y registra las señales al iniciar la app.
"""

from django.apps import AppConfig


class CartsConfig(AppConfig):
    """Clase de configuración de la app 'carts'."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "carts"

    def ready(self):
        """Importa las señales de la app al iniciar."""
        import carts.signals
