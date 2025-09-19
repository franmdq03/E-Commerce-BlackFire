"""
Vistas para la app 'store'.

Incluye funciones para mostrar productos, detalles, búsqueda y página de comunidad.
"""

from django.shortcuts import render, get_object_or_404
from .models import Producto, GaleriaProducto, Marca
from category.models import Categoria
from carts.models import ItemCarrito
from django.db.models import Q
from carts.views import _id_carrito
from django.core.paginator import Paginator
from orders.models import ProductoOrdenado


def tienda(request, categoria_slug=None, subcategoria_slug=None, marca_slug=None):
    """
    Muestra los productos disponibles en la tienda.

    Parámetros opcionales:
    - categoria_slug: filtra productos por categoría.
    - subcategoria_slug: filtra productos por subcategoría.
    - marca_slug: filtra productos por marca.

    Filtra también por rango de precio mediante parámetros GET 'min_precio' y 'max_precio'.
    Implementa paginación de 9 productos por página.
    Retorna render de 'store/store.html' con el contexto de productos y filtros.
    """
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    productos = Producto.objects.filter(disponible=True)

    if categoria_slug is not None:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria)

    if subcategoria_slug is not None:
        from category.models import Subcategoria
        subcategoria = get_object_or_404(Subcategoria, slug=subcategoria_slug)
        productos = productos.filter(subcategoria=subcategoria)

    if marca_slug is not None:
        marca = get_object_or_404(Marca, slug=marca_slug)
        productos = productos.filter(marca=marca)

    min_precio = request.GET.get("min_precio")
    max_precio = request.GET.get("max_precio")

    if min_precio:
        try:
            min_precio_val = float(min_precio)
            productos = productos.filter(precio__gte=min_precio_val)
        except ValueError:
            pass

    if max_precio:
        try:
            max_precio_val = float(max_precio)
            productos = productos.filter(precio__lte=max_precio_val)
        except ValueError:
            pass

    paginator = Paginator(productos, 9)
    page = request.GET.get("page")
    productos_paginados = paginator.get_page(page)
    cantidad_productos = productos.count()

    contexto = {
        "productos": productos_paginados,
        "cantidad_productos": cantidad_productos,
        "categorias": categorias,
        "marcas": marcas,
        "categoria_seleccionada": categoria_slug,
        "subcategoria_seleccionada": subcategoria_slug,
        "marca_seleccionada": marca_slug,
        "min_precio": min_precio or "",
        "max_precio": max_precio or "",
    }
    return render(request, "store/store.html", contexto)


def detalle_producto(request, categoria_slug, producto_slug):
    """
    Muestra el detalle de un producto específico.

    Parámetros:
    - categoria_slug: slug de la categoría del producto.
    - producto_slug: slug del producto a mostrar.

    Incluye:
    - Verificación si el producto está en el carrito del usuario actual.
    - Verificación si el usuario ya ha ordenado el producto.
    - Galería de imágenes del producto.

    Retorna render de 'store/product_detail.html' con contexto.
    """
    try:
        producto_unico = Producto.objects.get(
            categoria__slug=categoria_slug, slug=producto_slug
        )
        en_carrito = ItemCarrito.objects.filter(
            carrito__id_carrito=_id_carrito(request), producto=producto_unico
        ).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            producto_ordenado = ProductoOrdenado.objects.filter(
                usuario=request.user, producto_id=producto_unico.id
            ).exists()
        except ProductoOrdenado.DoesNotExist:
            producto_ordenado = None
    else:
        producto_ordenado = None

    galeria_producto = GaleriaProducto.objects.filter(producto_id=producto_unico.id)

    contexto = {
        "producto_unico": producto_unico,
        "en_carrito": en_carrito,
        "producto_ordenado": producto_ordenado,
        "galeria_producto": galeria_producto,
    }
    return render(request, "store/product_detail.html", contexto)


def buscar(request):
    """
    Permite buscar productos por palabra clave.

    Parámetros GET:
    - keyword: texto a buscar en nombre o detalle del producto.

    Retorna render de 'store/store.html' con los resultados encontrados.
    """
    productos = []
    cantidad_productos = 0
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            productos = Producto.objects.order_by("-creado_en").filter(
                Q(detalle__icontains=keyword) | Q(nombre_producto__icontains=keyword)
            )
            cantidad_productos = productos.count()
    contexto = {
        "productos": productos,
        "cantidad_productos": cantidad_productos,
    }
    return render(request, "store/store.html", contexto)


def comunidad(request):
    """
    Renderiza la página de comunidad.

    Retorna render de 'comunidad/comunidad.html'.
    """
    return render(request, "comunidad/comunidad.html")

