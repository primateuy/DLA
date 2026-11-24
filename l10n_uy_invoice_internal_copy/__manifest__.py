# -*- coding: utf-8 -*-
{
    'name': 'Copia interna de comprobantes (UY)',
    'version': '17.0.1.0.0',
    'summary': 'Permite imprimir la representación interna de Odoo de facturas '
               'y recibos ya enviados a UCFE, identificada como copia sin valor fiscal',
    'description': """
Copia interna de comprobantes (Uruguay)
=======================================

La localización uruguaya intercepta la impresión de cualquier reporte sobre
``account.move`` y ``account.payment`` y devuelve el PDF oficial que emite
UCFE. Eso impide acceder a la representación interna que genera Odoo.

Este módulo agrega dos reportes adicionales -uno para facturas y otro para
recibos de pago- que sí generan el PDF de Odoo, salteando la intercepción
únicamente para ellos. El flujo oficial de facturación electrónica no se
modifica: los reportes estándar siguen bajando el CFE de UCFE.

La copia lleva una leyenda que la identifica como documento sin valor fiscal.
La leyenda se configura por compañía en Ajustes > Compañías, pestaña
"Conexión CFE".

El acceso a estos reportes está restringido al grupo
"Imprimir copia interna de comprobantes".
    """,
    'author': 'Primate',
    'website': 'https://primate.uy',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'l10n_uy_einvoice_base',
        'l10n_uy_einvoice_uruware',
    ],
    'data': [
        'security/internal_copy_security.xml',
        'report/internal_copy_templates.xml',
        'report/internal_copy_reports.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
