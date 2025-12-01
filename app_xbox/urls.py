from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    
    # Nueva ruta de Registro
    path('registro/', views.registro, name='registro'),

    path('videojuegos/', views.lista_videojuegos, name='lista_videojuegos'),
    path('consolas/', views.lista_consolas, name='lista_consolas'),
    path('accesorios/', views.lista_accesorios, name='lista_accesorios'),


    # CRUD Videojuegos
    path('videojuegos/crear/', views.crear_videojuego, name='crear_videojuego'),
    path('videojuegos/editar/<int:id>/', views.editar_videojuego, name='editar_videojuego'),
    path('videojuegos/eliminar/<int:id>/', views.eliminar_videojuego, name='eliminar_videojuego'),
    
    # CARRITO
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<str:tipo>/<int:id_producto>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:id_item>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
    path('carrito/modificar/<int:id_item>/<str:accion>/', views.sumar_restar_item, name='sumar_restar_item'),

    
    # PAGO
    path('checkout/', views.checkout, name='checkout'),
    
    # PERFIL / HISTORIAL
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]
