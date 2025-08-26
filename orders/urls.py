from django.urls import path
from . import views

urlpatterns = [
    path('realizar_pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('pagos/', views.pagos, name='pagos'),
    path('pedido_completo/', views.pedido_completo, name='pedido_completo'),
]