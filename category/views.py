"""
Vistas para la app 'category'.

Define la lógica para obtener y mostrar subcategorías de una categoría específica.
"""

from django.shortcuts import render, get_object_or_404
from .models import Categoria

def subcategorias_por_categoria(request, slug):
    """
    Muestra todas las subcategorías de una categoría principal.

    Parámetros:
    - request: objeto HttpRequest.
    - slug: identificador único de la categoría.

    Retorna:
    - Renderiza la plantilla 'subcategorias.html' con la categoría y sus subcategorías.
    """
    categoria_padre = get_object_or_404(Categoria, slug=slug)
    subcategorias = categoria_padre.subcategorias.all()  # gracias a related_name='subcategorias'
    return render(request, 'subcategorias.html', {
        'categoria': categoria_padre,
        'subcategorias': subcategorias,
    })