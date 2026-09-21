# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import models


class SaleBlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    def action_confirm(self):
        """Evita que se reasigne el número al reconfirmar.

        ``sale_blanket_order`` (17.0.2.3.0, OCA/sale-workflow) llama a
        ``ir.sequence.next_by_code`` en CADA ``action_confirm``, sin
        verificar si el pedido ya tenía un ``name`` asignado (idéntico al
        comportamiento verificado en la rama 19.0 del módulo). Esto
        provoca que, al hacer "Volver a borrador" + "Confirmar", el
        Acuerdo Comercial cambie de número.

        Estrategia defensiva: en vez de reimplementar la lógica de
        confirmación (que podría cambiar en próximas versiones de OCA),
        guardamos el nombre ANTES de llamar a ``super()`` y lo restauramos
        DESPUÉS solo si cambió. Si en el futuro OCA corrige este
        comportamiento en el módulo base, ``order.name`` ya será igual a
        ``original_name`` tras el ``super()`` y este método se convierte
        en un no-op transparente: seguirá instalado y funcionando sin
        interferir ni duplicar consumo de secuencia.
        """
        original_names = {order.id: order.name for order in self}
        result = super().action_confirm()
        for order in self:
            original_name = original_names.get(order.id)
            if (
                original_name
                and original_name not in (False, "Draft")
                and order.name != original_name
            ):
                order.name = original_name
        return result
