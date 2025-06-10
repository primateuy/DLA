from odoo import SUPERUSER_ID, _, api


def migrate(cr, version):

    env = api.Environment(cr, SUPERUSER_ID, {})

    validate_wave_picking = env.ref("ventor_base.validate_wave_picking", False)
    validate_picking_batch = env.ref("ventor_base.validate_picking_batch", False)
    validate_cluster_picking = env.ref("ventor_base.validate_cluster_picking", False)
    value = {
        "description": "Validate Stock Picking automatically if it completely processed. "
                       "Note: When ON transfers with all skipped items will be validated with initial quantity"
    }
    if validate_wave_picking:
        validate_wave_picking.write(value)
    if validate_picking_batch:
        validate_picking_batch.write(value)
    if validate_cluster_picking:
        validate_cluster_picking.write(value)

    is_qc_installed = env.user.is_module_installed('quality_control')

    if is_qc_installed:
        # BP, CP, WP menus
        ventor_quality_control_settings = env['ventor.option.setting'].search(
            [
                ('technical_name', '=', 'quality_check_per_product_line'),
            ]
        )
        ventor_quality_control_settings.value = env.ref('ventor_base.bool_true')

        # WO operation types:
        stock_picking_type_ids = env['stock.picking.type'].with_context(active_test=False).search([])
        stock_picking_type_ids.quality_check_per_product_line = True
