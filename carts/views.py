from django.shortcuts import render, redirect, get_object_or_404
from store.models import Producto
from .models import Carrito, ItemCarrito
from django.core.exceptions import ObjectDoesNotExist

def _id_carrito(request):
    carrito = request.session.session_key
    if not carrito:
        carrito = request.session.create()
    return carrito

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Obtener cantidad del formulario POST
    cantidad = request.POST.get('cantidad')
    if cantidad is None or cantidad == '':
        cantidad = 1
    else:
        cantidad = int(cantidad)

    # Obtener o crear el carrito
    try:
        carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
    except Carrito.DoesNotExist:
        carrito = Carrito.objects.create(id_carrito=_id_carrito(request))
    carrito.save()

    # Agregar el producto al carrito
    if request.user.is_authenticated:
        item_carrito, creado = ItemCarrito.objects.get_or_create(
            producto=producto, usuario=request.user, carrito=carrito,
            defaults={'cantidad': cantidad}
        )
    else:
        item_carrito, creado = ItemCarrito.objects.get_or_create(
            producto=producto, carrito=carrito,
            defaults={'cantidad': cantidad}
        )

    if not creado:
        item_carrito.cantidad += cantidad
        item_carrito.save()

    return redirect('carrito')

def quitar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        if request.user.is_authenticated:
            item_carrito = ItemCarrito.objects.filter(producto=producto, usuario=request.user).first()
        else:
            carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
            item_carrito = ItemCarrito.objects.filter(producto=producto, carrito=carrito).first()

        if item_carrito:
            if item_carrito.cantidad > 1:
                item_carrito.cantidad -= 1
                item_carrito.save()
            else:
                item_carrito.delete()
    except Carrito.DoesNotExist:
        pass
    return redirect('carrito')

def quitar_item_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        if request.user.is_authenticated:
            item_carrito = ItemCarrito.objects.filter(producto=producto, usuario=request.user).first()
        else:
            carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
            item_carrito = ItemCarrito.objects.filter(producto=producto, carrito=carrito).first()

        if item_carrito:
            item_carrito.delete()
    except Carrito.DoesNotExist:
        pass
    return redirect('carrito')


def carrito(request, total=0, cantidad=0, items_carrito=None):
    try:
        if request.user.is_authenticated:
            items_carrito = ItemCarrito.objects.filter(usuario=request.user, activo=True)
        else:
            carrito_obj = Carrito.objects.get(id_carrito=_id_carrito(request))
            items_carrito = ItemCarrito.objects.filter(carrito=carrito_obj, activo=True)
        
        for item in items_carrito:
            total += (item.producto.precio * item.cantidad)
            cantidad += item.cantidad
    except ObjectDoesNotExist:
        items_carrito = []

    productos = Producto.objects.filter(disponible=True)[:8]

    contexto = {
        'total': total,
        'cantidad': cantidad,
        'items_carrito': items_carrito,
        'productos': productos,  
    }

    return render(request, 'store/cart.html', contexto)

