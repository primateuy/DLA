# -*- coding: utf-8 -*-
{
    'name': "Balance Moneda",

    'summary': "Este módulo extiende las funcionalidades de los apuntes contables",

    'description': """
Este módulo extiende las funcionalidades de los apuntes contables en Odoo agregando un nuevo campo llamado "Balance en Moneda" (balance_currency),
que calcula y muestra el balance (Debe - Haber) en la moneda definida en la cuenta contable. Además, habilita la visualización de este campo junto con
"Importe en Divisa" (amount_currency) y "Divisa" (currency_id) en las vistas Tree y Pivot. Esto permite un análisis más detallado y específico en diferentes
monedas directamente desde las vistas contables.
    """,

    'author': 'PrimateUY',
    'website': 'https://primate.uy/',
    'category': 'Contabilidad',
    'version': '17.1.0',

    'depends': ['account'],

    'data': [
        'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
    ],

}

