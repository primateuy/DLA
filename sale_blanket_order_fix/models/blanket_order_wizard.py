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
