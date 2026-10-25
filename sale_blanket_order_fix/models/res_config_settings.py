# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models

from .params import (
    PARAM_AUTO_ASSIGN,
    PARAM_WIZARD_ZERO_QTY,
    get_bool_param,
)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Este booleano NO usa config_parameter= a propósito: Odoo borra el
    # parámetro cuando se guarda False, y al releerlo aplicaría de nuevo
    # el default True (imposible de destildar). Se guarda explícitamente
    # "True"/"False" en get_values()/set_values().
    blanket_auto_assign_line = fields.Boolean(
        string="Determinación automática del acuerdo en líneas de pedido",
        help="Tildado (comportamiento estándar de OCA): al cargar o "
        "modificar una línea del pedido de venta, el sistema busca y "
        "asigna solo el Acuerdo Comercial.\n"
        "Destildado: no se asigna ni se reasigna nunca; el usuario "
        "elige el acuerdo a mano en la línea.",
    )
    blanket_wizard_zero_qty = fields.Boolean(
        string="Cantidad a pedir inicial en cero (asistente de pedido)",
        config_parameter=PARAM_WIZARD_ZERO_QTY,
        help="Tildado: el asistente 'Crear pedido' del Acuerdo Comercial "
        "propone cantidad 0 en cada línea y el usuario debe cargarla.\n"
        "Destildado (estándar de OCA): propone el saldo pendiente.",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        res["blanket_auto_assign_line"] = get_bool_param(
            self.env, PARAM_AUTO_ASSIGN, True
        )
        return res

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            PARAM_AUTO_ASSIGN, "True" if self.blanket_auto_assign_line else "False"
        )
