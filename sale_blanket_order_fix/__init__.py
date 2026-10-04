from . import models

# Odoo busca post_init_hook/uninstall_hook como atributos DIRECTOS del
# paquete del módulo (odoo.addons.sale_blanket_order_fix.post_init_hook),
# no dentro del submódulo hooks. `from . import hooks` no alcanza —hay
# que reexportar los nombres explícitamente.
from .hooks import post_init_hook, uninstall_hook
