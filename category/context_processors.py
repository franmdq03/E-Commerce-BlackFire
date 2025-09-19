"""
Context processor para la app 'category'.
Proporciona todas las categorías al contexto de las plantillas,
permitiendo mostrar enlaces de menú dinámicamente en toda la web.
"""

from .models import Categoria

def menu_links(request):
    links = Categoria.objects.all()
    return dict(links=links)

