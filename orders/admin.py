"""
Configuración del panel de administración para la app 'orders'.

Registra los modelos Pago, Orden y ProductoOrdenado para que sean gestionables desde el admin de Django.
"""

from django.contrib import admin
from .models import Pago, Orden, ProductoOrdenado, BandaEnvio

# Registro de modelos en el admin
admin.site.register(Pago)
admin.site.register(Orden)
admin.site.register(ProductoOrdenado)

@admin.register(BandaEnvio)
class BandaEnvioAdmin(admin.ModelAdmin):
    list_display = ('distancia_hasta', 'costo')
    list_editable = ('costo',) # Permite editar el costo desde la lista
    ordering = ('distancia_hasta',)
    
    # Añade un mensaje de ayuda en el admin
    fieldsets = (
        (None, {
            'fields': ('distancia_hasta', 'costo'),
            'description': """
                <p>Define el costo de envío para distancias <strong>hasta</strong> el valor de KM indicado.</p>
                <p>La lógica buscará la primera banda que cumpla (ordenadas de menor a mayor distancia).</p>
                <p><strong>Importante:</strong> La última banda debe tener una distancia muy alta (ej: 99999) para actuar como el costo "por defecto" para distancias largas.</p>
            """
        }),
    )
