# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
"""Parámetros de sistema (ir.config_parameter) de este módulo.

Se leen siempre con ``get_bool_param`` para tener un único criterio de
interpretación. Los valores por defecto (parámetro inexistente) dejan el
comportamiento IDÉNTICO al de OCA: instalar el módulo no cambia nada
hasta que alguien tilde las opciones en Ajustes > Ventas.
"""

PARAM_AUTO_ASSIGN = "sale_blanket_order_fix.auto_assign_blanket_line"
PARAM_WIZARD_ZERO_QTY = "sale_blanket_order_fix.wizard_zero_qty"
ALL_PARAMS = (PARAM_AUTO_ASSIGN, PARAM_WIZARD_ZERO_QTY)


def get_bool_param(env, key, default):
    """Lee un parámetro booleano; ausente => ``default``."""
    value = env["ir.config_parameter"].sudo().get_param(key, str(default))
    return str(value).strip().lower() not in ("false", "0", "no", "")
