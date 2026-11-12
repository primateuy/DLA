# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models

from .params import PARAM_WIZARD_ZERO_QTY, get_bool_param


class BlanketOrderWizard(models.TransientModel):
    _inherit = "sale.blanket.order.wizard"

    # En OCA 17.0 el default está declarado como referencia directa a la
    # función (``default=_default_lines``): sobrescribir _default_lines()
    # NO alcanzaría, porque el campo conservaría la función original.
    # Se redeclara el default con una lambda que resuelve el método por
    # MRO (en 19.0 OCA ya lo hace así).
    line_ids = fields.One2many(default=lambda self: self._default_lines())

    @api.model
    def _default_lines(self):
        commands = super()._default_lines()
        if get_bool_param(self.env, PARAM_WIZARD_ZERO_QTY, False):
            for command in commands:
                # fields.Command.create(vals) == (0, 0, vals)
                command[2]["qty"] = 0.0
        return commands

    def _prepare_so_line_vals(self, line):
        """Copia la descripción de la línea del acuerdo a la línea del pedido.

        OCA arma ``name`` con ``line.product_id.name``: el nombre de la
        PLANTILLA del producto, ignorando la descripción de la línea del
        acuerdo (``blanket_line_id.name``). Se pierden así la variante, el
        texto de ``description_sale`` y cualquier ajuste manual que el
        usuario haya hecho sobre esa descripción. Se pasa a usar la
        descripción de la línea del acuerdo; si estuviera vacía se
        conserva el valor de OCA.
        """
        vals = super()._prepare_so_line_vals(line)
        description = line.blanket_line_id.name
        if description:
            vals["name"] = description
        return vals
