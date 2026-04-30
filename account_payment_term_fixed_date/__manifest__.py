# -*- coding: utf-8 -*-
{
    'name': 'Payment Term - Fixed Date Formula',
    'version': '17.0.1.9.2',
    'category': 'Accounting/Accounting',
    'summary': 'Adds "Next fixed date" payment term type with fixed or formula-based month/day',
    'description': """
Payment Term Fixed Date Formula
================================
Extends account.payment.term.line with a new delay type:
**"Next fixed date (formula)"**

Allows defining the due date as a fixed calendar date or a formula
relative to the invoice date:

Examples
--------
- **31 de enero proximo**: day=31, month_formula=1  (fixed month 1)
- **30 de junio proximo**: day=30, month_formula=6  (fixed month 6)
- **Ultimo dia del mes + 5**: day=31, month_formula="month+5"
- **Dia 15, dos meses despues**: day=15, month_formula="month+2"

Formula syntax for month_formula
---------------------------------
- A fixed integer 1-12  -> that specific calendar month  (e.g. 1 = January)
- month+N               -> invoice month + N months      (e.g. month+5)
- month-N               -> invoice month - N months

The year is automatically advanced when the computed date has already
passed relative to the invoice date.
    """,
    'author': 'Custom Development',
    'depends': ['account'],
    'data': [
        'views/account_payment_term_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    'post_migrate': 'post_migrate',
}

