from odoo import SUPERUSER_ID, _, api


def migrate(cr, version):

    env = api.Environment(cr, SUPERUSER_ID, {})

    hide_products_quantity = env.ref("ventor_base.hide_products_quantity", False)
    if hide_products_quantity.value == env.ref("ventor_base.bool_true"):
        start_count_from_zero = env.ref("ventor_base.start_count_from_zero", False)
        if start_count_from_zero:
            start_count_from_zero.value = env.ref("ventor_base.bool_true")
