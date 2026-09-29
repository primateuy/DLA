# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "Sale Blanket Order - Fix numbering & editable lines",
    "summary": (
        "Corrige la renumeración al reconfirmar un Acuerdo Comercial "
        "(sale.blanket.order) y permite editar cantidades / agregar "
        "líneas una vez confirmado."
    ),
    "version": "17.0.1.0.0",
    "category": "Sales/Sales",
    "license": "AGPL-3",
    "author": "PrimateUY, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    # IMPORTANTE (17.0): la dependencia técnica sigue llamándose
    # "sale_blanket_order", pero para la serie 17.0 ese módulo vive en el
    # repositorio OCA/sale-workflow (rama 17.0), NO en OCA/sale-blanket
    # (que recién empieza a hospedarlo desde la rama 18.0 en adelante).
    # Instalar sale_blanket_order desde:
    #   https://github.com/OCA/sale-workflow/tree/17.0/sale_blanket_order
    "depends": [
        "sale_blanket_order",
    ],
    "data": [
        "views/sale_blanket_order_views.xml",
        "views/sale_blanket_order_line_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    # Aplican/revierten de forma simétrica el relabel ES de OCA
    # ("Pedido Programado" -> "Acuerdo Comercial"), ver hooks.py.
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
