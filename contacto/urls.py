from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_contacto, name='vista_contacto'),
    path('exito/', views.vista_contacto_exito, name='contacto_exito'),
]