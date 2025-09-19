"""
URLs para la app 'contacto'.

Define las rutas para el formulario de contacto y la página de éxito.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal del formulario de contacto
    path('', views.vista_contacto, name='vista_contacto'),

    # Ruta a la página de éxito tras enviar el formulario
    path('exito/', views.vista_contacto_exito, name='contacto_exito'),
]
