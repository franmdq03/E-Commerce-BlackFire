from django.shortcuts import render, get_object_or_404
from .models import Categoria

# Create your views here.

def subcategorias_por_categoria(request, slug):
    categoria_padre = get_object_or_404(Categoria, slug=slug)
    subcategorias = categoria_padre.subcategorias.all()  # gracias a related_name='subcategorias'
    return render(request, 'subcategorias.html', {
        'categoria': categoria_padre,
        'subcategorias': subcategorias,
    })
