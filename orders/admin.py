from django.contrib import admin
from .models import Pago, Orden, ProductoOrdenado

admin.site.register(Pago)
admin.site.register(Orden)
admin.site.register(ProductoOrdenado)
