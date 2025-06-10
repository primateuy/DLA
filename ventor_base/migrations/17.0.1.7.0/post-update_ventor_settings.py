from odoo import SUPERUSER_ID, _, api


def migrate(cr, version):

    env = api.Environment(cr, SUPERUSER_ID, {})

    prohibition_on_updating_inventory = env.ref(
        "ventor_base.prohibition_on_updating_inventory",
        False,
    )

    if prohibition_on_updating_inventory:
        prohibition_on_updating_inventory.write(
            {
                "name": "Hide update inventory button",
            }
        )

    manage_packages_ins_inventory = env.ref(
        "ventor_base.manage_packages_ins_inventory",
        False,
    )

    if manage_packages_ins_inventory:
        manage_packages_ins_inventory.write(
            {
                "description": "It shows additional field 'Package' that you can scan to make an inventory in a package. "
                               "Works only if package management settings is active on Odoo side",
            }
        )
