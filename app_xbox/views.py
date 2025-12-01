from django.shortcuts import render, redirect, get_object_or_404
from .models import Videojuego, Consola, Accesorio, Pedido, PedidoItem
from django.contrib import messages 
from .forms import RegistroForm, VideojuegoForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType


def inicio(request):
    # Traemos los productos para mostrarlos en el inicio (si quieres)
    # O simplemente mostramos la portada. Vamos a traerlos por si acaso.
    consolas = Consola.site_objects.all() if hasattr(Consola, 'site_objects') else Consola.objects.all()
    # Nota: Usamos objects.all() estándar
    consolas = Consola.objects.all()[:3] 
    juegos = Videojuego.objects.all()[:3]
    
    context = {
        'consolas': consolas,
        'juegos': juegos
    }
    return render(request, 'inicio.html', context)
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada para {username}! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'auth/registro.html', {'form': form})
# --- VISTAS DE VIDEOJUEGOS ---
def lista_videojuegos(request):
    juegos = Videojuego.objects.all()
    return render(request, 'videojuegos/lista.html', {'juegos': juegos})

# --- VISTAS DE CONSOLAS ---
def lista_consolas(request):
    consolas = Consola.objects.all()
    return render(request, 'consolas/lista.html', {'consolas': consolas})

# --- VISTAS DE ACCESORIOS ---
def lista_accesorios(request):
    accesorios = Accesorio.objects.all()
    return render(request, 'accesorios/lista.html', {'accesorios': accesorios})

# --- CRUD DE VIDEOJUEGOS ---

@staff_member_required # Solo admin entra aquí
def crear_videojuego(request):
    if request.method == 'POST':
        form = VideojuegoForm(request.POST, request.FILES) # request.FILES es para la imagen
        if form.is_valid():
            form.save()
            messages.success(request, 'Videojuego agregado correctamente.')
            return redirect('lista_videojuegos')
    else:
        form = VideojuegoForm()
    return render(request, 'videojuegos/form.html', {'form': form, 'titulo': 'Crear Nuevo Videojuego'})

@staff_member_required
def editar_videojuego(request, id):
    juego = get_object_or_404(Videojuego, pk=id) # Busca el juego o da error 404
    if request.method == 'POST':
        form = VideojuegoForm(request.POST, request.FILES, instance=juego) # instance carga los datos actuales
        if form.is_valid():
            form.save()
            messages.success(request, 'Videojuego actualizado.')
            return redirect('lista_videojuegos')
    else:
        form = VideojuegoForm(instance=juego)
    return render(request, 'videojuegos/form.html', {'form': form, 'titulo': f'Editar {juego.nombre}'})

@staff_member_required
def eliminar_videojuego(request, id):
    juego = get_object_or_404(Videojuego, pk=id)
    if request.method == 'POST':
        juego.delete()
        messages.success(request, 'Videojuego eliminado.')
        return redirect('lista_videojuegos')
    return render(request, 'videojuegos/eliminar.html', {'juego': juego})

# ==========================================
#            LOGICA DEL CARRITO
# ==========================================

@login_required(login_url='login')
def agregar_carrito(request, tipo, id_producto):
    # 1. Identificar qué modelo es (Videojuego, Consola o Accesorio)
    modelo = None
    if tipo == 'videojuego':
        modelo = Videojuego
    elif tipo == 'consola':
        modelo = Consola
    elif tipo == 'accesorio':
        modelo = Accesorio
    
    if not modelo:
        return redirect('inicio')

    # 2. Obtener el producto específico
    producto = get_object_or_404(modelo, pk=id_producto)

    # 3. Obtener o Crear el Pedido PENDIENTE del usuario
    pedido, created = Pedido.objects.get_or_create(
        cliente=request.user.cliente,
        estado='pendiente'
    )

    # 4. Verificar si ya existe este item en el carrito
    content_type = ContentType.objects.get_for_model(modelo)
    item, created = PedidoItem.objects.get_or_create(
        pedido=pedido,
        content_type=content_type,
        object_id=producto.pk,
        defaults={'precio_unitario': producto.precio}
    )

    # 5. Si ya existía, aumentamos cantidad; si es nuevo, se guarda el default
    if not created:
        item.cantidad += 1
        item.save()
    
    # 6. Calcular total del pedido y guardar mensaje
    pedido.calcular_total()
    messages.success(request, f'{producto.nombre} agregado al carrito.')
    
    # Redirigir a la misma página de donde vino (o al carrito)
    return redirect('ver_carrito')

@login_required(login_url='login')
def ver_carrito(request):
    try:
        # Intentar buscar un pedido pendiente
        pedido = Pedido.objects.get(cliente=request.user.cliente, estado='pendiente')
        items = pedido.items.all()
    except Pedido.DoesNotExist:
        pedido = None
        items = []

    return render(request, 'carrito/ver_carrito.html', {'pedido': pedido, 'items': items})

@login_required(login_url='login')
def eliminar_item_carrito(request, id_item):
    item = get_object_or_404(PedidoItem, pk=id_item)
    # Verificar que el item pertenezca al usuario actual para seguridad
    if item.pedido.cliente.user == request.user:
        item.delete()
        item.pedido.calcular_total() # Recalcular total
        messages.warning(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')

@login_required(login_url='login')
def sumar_restar_item(request, id_item, accion):
    item = get_object_or_404(PedidoItem, pk=id_item)
    
    if item.pedido.cliente.user == request.user:
        if accion == 'sumar':
            item.cantidad += 1
        elif accion == 'restar':
            item.cantidad -= 1
            if item.cantidad < 1: # Si baja de 1, lo borramos
                item.delete()
                return redirect('ver_carrito')
        
        item.save()
        item.pedido.calcular_total()
        
    return redirect('ver_carrito')  

# ==========================================
#            PAGO Y CIERRE
# ==========================================

@login_required(login_url='login')
def checkout(request):
    try:
        pedido = Pedido.objects.get(cliente=request.user.cliente, estado='pendiente')
    except Pedido.DoesNotExist:
        return redirect('inicio')

    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        
        # 1. Guardar datos de envío
        pedido.direccion_envio = direccion
        pedido.estado = 'pagado' # Cambiamos estado para "cerrar" el carrito
        pedido.save()

        # 2. (Opcional) Restar Stock - Lógica Pro
        for item in pedido.items.all():
            producto = item.producto # Accede al objeto real (Juego/Consola)
            if producto.stock >= item.cantidad:
                producto.stock -= item.cantidad
                producto.save()
        
        # 3. Mandar a página de éxito
        return render(request, 'carrito/pedido_completado.html', {'pedido': pedido})

    return render(request, 'carrito/checkout.html', {'pedido': pedido})

@login_required(login_url='login')
def mis_pedidos(request):
    # Mostrar historial de compras (pedidos que NO sean pendientes)
    pedidos = Pedido.objects.filter(cliente=request.user.cliente).exclude(estado='pendiente').order_by('-fecha_pedido')
    return render(request, 'clientes/mis_pedidos.html', {'pedidos': pedidos})