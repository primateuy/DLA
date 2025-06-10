from odoo import SUPERUSER_ID, _, api


def migrate(cr, version):

    env = api.Environment(cr, SUPERUSER_ID, {})

    pack_all_items = env.ref("ventor_base.pack_all_items", False)
    if pack_all_items:
        pack_all_items.write(
            {
                "description": "Force to pack all items that have a quantity greater than zero"
            }
        )

    users_model = env['res.users']

    external_users = users_model.search([]).filtered(lambda user: not user.has_group('base.group_user'))

    all_ventor_categories = [
        env.ref('ventor_base.module_category_merp_menu_application').id,
        env.ref('ventor_base.module_category_merp_access_application').id,
        env.ref('ventor_base.module_category_ventor_roles').id
    ]

    ventor_groups_ids = env['res.groups'].search([('category_id', 'in', all_ventor_categories)])
    value = [(3, user.id) for user in external_users]

    for group in ventor_groups_ids:
        group.write(
            {
                'users': value,
            }
        )
