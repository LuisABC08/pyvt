from django.contrib import admin
from .models import Cliente, Videojuego, Consola, Accesorio, Pedido, PedidoItem

# Esta clase sirve para mostrar columnas bonitas en el panel
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'proveedor_info')
    search_fields = ('nombre',)
    
    # Un pequeño truco para mostrar el proveedor correctamente según el modelo
    def proveedor_info(self, obj):
        if hasattr(obj, 'proveedor'):
            return obj.proveedor
        return "N/A"
    proveedor_info.short_description = 'Proveedor'

# Registramos los modelos
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(PedidoItem)

# Registramos los productos usando la configuración visual de arriba
admin.site.register(Videojuego, ProductoAdmin)
admin.site.register(Accesorio, ProductoAdmin)

# Consola es un poco diferente (no tiene campo 'proveedor' en tu modelo, sino marca/detalles)
class ConsolaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'color')

admin.site.register(Consola, ConsolaAdmin)