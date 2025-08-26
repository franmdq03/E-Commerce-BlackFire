from django.shortcuts import render
from store.models import Producto
from category.models import Categoria
from django.db.models import Count
import random

def home(request):
    # Obtener 4 categorías con más productos
    categorias = Categoria.objects.annotate(num_productos=Count('productos_categoria')).order_by('-num_productos')[:4]

    # Obtener todos los productos disponibles
    productos_disponibles = list(Producto.objects.filter(disponible=True))

    # Elegir 4 productos al azar
    productos = random.sample(productos_disponibles, min(4, len(productos_disponibles)))

    contexto = {
        "productos": productos,
        "categorias": categorias,
    }

    return render(request, "home.html", contexto)
