from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar, name='registrar'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('panel/', views.panel, name='panel'),
    path('', views.panel, name='panel'),

    path('activar/<uidb64>/<token>/', views.activar, name='activar'),
    path('olvido_contrasena/', views.olvido_contrasena, name='olvido_contrasena'),
    path("validar_restablecer_contrasena/<uidb64>/<token>/",views.validar_restablecer_contrasena,
    name="resetpassword_validate"
),

    path('restablecer_contrasena/', views.restablecer_contrasena, name='restablecer_contrasena'),

    path('mis_ordenes/', views.mis_ordenes, name='mis_ordenes'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('detalle_orden/<int:id_orden>/', views.detalle_orden, name='detalle_orden'),
]