"""
Vistas de la app 'carts' del ecommerce.
Gestiona la lógica del carrito de compras: agregar, quitar, eliminar items y mostrar el carrito.
"""

from django.shortcuts import render, redirect, get_object_or_404
from store.models import Producto
from .models import Carrito, ItemCarrito
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages 


def _id_carrito(request):
    """
    Devuelve el ID de carrito basado en la sesión.
    Si no existe, crea una nueva sesión y la asigna.
    """
    carrito = request.session.session_key
    if not carrito:
        carrito = request.session.create()
    return carrito


@csrf_exempt
def agregar_al_carrito(request, producto_id):
    """
    Agrega un producto al carrito.
    - Valida que el producto tenga stock disponible.
    - Si el usuario está autenticado, el item se asocia a su cuenta.
    - Si ya existe, aumenta la cantidad validando el stock.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad_solicitada = request.POST.get("cantidad") or 1
    cantidad_solicitada = int(cantidad_solicitada)

    # --- INICIO DE CORRECCIÓN ---

    # Valida que el producto esté disponible y tenga al menos 1 unidad de stock
    if not producto.disponible or producto.stock <= 0:
        #Enviar mensaje de error
        messages.error(request, "Este producto no está disponible o no tiene stock.")
        return redirect("carrito")

    try:
        carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
    except Carrito.DoesNotExist:
        carrito = Carrito.objects.create(id_carrito=_id_carrito(request))

    cantidad_existente = 0
    item_carrito = None
    try:
        if request.user.is_authenticated:
            item_carrito = ItemCarrito.objects.get(
                producto=producto, usuario=request.user, carrito=carrito
            )
        else:
            item_carrito = ItemCarrito.objects.get(
                producto=producto, carrito=carrito
            )
        cantidad_existente = item_carrito.cantidad
    except ItemCarrito.DoesNotExist:
        pass

    # 4. Validar el stock total deseado
    cantidad_total_deseada = cantidad_existente + cantidad_solicitada

    if producto.stock < cantidad_total_deseada:
        # No hay suficiente stock
        messages.error(
            request,
            f"No hay suficiente stock. Solo quedan {producto.stock} unidades."
        )
        return redirect("carrito")

    # 5. Crear o actualizar el item
    if item_carrito:
        # Si ya existía (encontrado en paso 3), actualizamos la cantidad
        item_carrito.cantidad = cantidad_total_deseada
        item_carrito.save()
    else:
        # Si no existía, lo creamos con la cantidad solicitada
        if request.user.is_authenticated:
            ItemCarrito.objects.create(
                producto=producto,
                usuario=request.user,
                carrito=carrito,
                cantidad=cantidad_solicitada,
            )
        else:
            ItemCarrito.objects.create(
                producto=producto,
                carrito=carrito,
                cantidad=cantidad_solicitada,
            )
    return redirect("carrito")


def quitar_del_carrito(request, producto_id):
    """
    Quita una unidad del producto especificado del carrito.
    Si la cantidad es 1, elimina el item completamente.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        if request.user.is_authenticated:
            item_carrito = ItemCarrito.objects.filter(
                producto=producto, usuario=request.user
            ).first()
        else:
            carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
            item_carrito = ItemCarrito.objects.filter(
                producto=producto, carrito=carrito
            ).first()

        if item_carrito:
            if item_carrito.cantidad > 1:
                item_carrito.cantidad -= 1
                item_carrito.save()
            else:
                item_carrito.delete()
    except Carrito.DoesNotExist:
        pass
    return redirect("carrito")


def quitar_item_carrito(request, producto_id):
    """
    Elimina completamente un item del carrito, sin importar la cantidad.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        if request.user.is_authenticated:
            item_carrito = ItemCarrito.objects.filter(
                producto=producto, usuario=request.user
            ).first()
        else:
            carrito = Carrito.objects.get(id_carrito=_id_carrito(request))
            item_carrito = ItemCarrito.objects.filter(
                producto=producto, carrito=carrito
            ).first()

        if item_carrito:
            item_carrito.delete()
    except Carrito.DoesNotExist:
        pass
    return redirect("carrito")


@csrf_exempt
def carrito(request, total=0, cantidad=0, items_carrito=None):
    """
    Muestra la vista del carrito.
    Calcula el total y la cantidad de items, y trae productos sugeridos.
    """
    try:
        if request.user.is_authenticated:
            items_carrito = ItemCarrito.objects.filter(
                usuario=request.user, activo=True
            )
        else:
            carrito_obj = Carrito.objects.get(id_carrito=_id_carrito(request))
            items_carrito = ItemCarrito.objects.filter(carrito=carrito_obj, activo=True)

        for item in items_carrito:
            total += item.producto.precio * item.cantidad
            cantidad += item.cantidad
    except ObjectDoesNotExist:
        items_carrito = []

    productos = Producto.objects.filter(disponible=True)[:8]

    contexto = {
        "total": total,
        "cantidad": cantidad,
        "items_carrito": items_carrito,
        "productos": productos,
    }

    return render(request, "store/cart.html", contexto)