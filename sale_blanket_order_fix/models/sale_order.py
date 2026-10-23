# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models

from .params import PARAM_AUTO_ASSIGN, get_bool_param


class SaleOrder(models.Model):
    _inherit = "sale.order"

    blanket_manual_mode = fields.Boolean(
        compute="_compute_blanket_manual_mode",
        help="Técnico: True si la determinación automática del acuerdo "
        "está desactivada en Ajustes. Lo usa la vista para mostrar "
        "siempre la columna 'Acuerdo' en las líneas del pedido.",
    )

    def _compute_blanket_manual_mode(self):
        manual = not get_bool_param(self.env, PARAM_AUTO_ASSIGN, True)
        for order in self:
            order.blanket_manual_mode = manual


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _blanket_auto_assign_enabled(self):
        return get_bool_param(self.env, PARAM_AUTO_ASSIGN, True)

    def get_assigned_bo_line(self):
        """Interruptor de la determinación automática del acuerdo.

        En OCA (17.0) esta es la única vía por la que el sistema asigna o
        REASIGNA ``blanket_order_line``: la llaman los onchanges de
        ``product_id`` / ``order_partner_id`` y de ``product_uom`` /
        ``product_uom_qty``. Con el parámetro activo (default) se delega
        tal cual en OCA. Con el parámetro desactivado:

        - Nunca se asigna ni se reasigna un acuerdo: el vínculo lo fija
          solo el usuario (o el asistente "Crear pedido", que escribe el
          vínculo al crear la línea).
        - Único caso en que se limpia el vínculo: si el producto de la
          línea dejó de coincidir con el del acuerdo vinculado (de lo
          contrario OCA lo pisaría de vuelta en
          ``onchange_blanket_order_line`` y fallaría su constraint).
        - Se mantiene el resto del comportamiento: con vínculo se
          conserva precio/impuestos del acuerdo; sin vínculo se recalcula
          el precio con la lista de precios (igual que sin acuerdo).
        - El dominio devuelto para elegir el acuerdo NO exige saldo
          suficiente (``remaining_qty >= 0``): el control de sobreconsumo
          queda en ``action_confirm`` de OCA.
        """
        self.ensure_one()
        if self._blanket_auto_assign_enabled():
            return super().get_assigned_bo_line()
        bol = self.blanket_order_line
        if bol and bol.product_id != self.product_id:
            self.blanket_order_line = False
        self.onchange_blanket_order_line()
        domain = self._get_eligible_bo_lines_domain(0.0)
        return {"domain": {"blanket_order_line": domain}}
