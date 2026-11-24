{
    'name': 'Sale Order Rounding',
    'version': '17.0.1.0.0',
    'summary': 'Apply cash rounding on Sale Orders and pass rounding values to invoices',
    'description': """
Sale Order Rounding adds cash rounding support to Odoo Sales and displays the rounding amount directly on the Sale Order totals section. It also transfers the rounding configuration and values from the Sale Order to the generated customer invoice.

Main Features:
- Add cash rounding support to Sale Orders
- Display rounding amount in the Sale Order totals section
- Pass Sale Order rounding configuration to customer invoices
- Transfer rounding values from Sale Orders to generated invoices
- Keep Sale Order and Invoice rounding behavior consistent
- Improve pricing clarity before invoice creation

This module is useful for businesses that want to apply cash rounding on quotations and sale orders and ensure the same rounding is carried forward automatically to customer invoices.
    """,
    'category': 'Sales',
    'author': 'Odooverse Global Solutions',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'price': 8.0,
    'currency': 'EUR',
}
