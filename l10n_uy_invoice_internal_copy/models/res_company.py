# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    internal_copy_watermark = fields.Boolean(
        string='Leyenda en copia interna',
        default=True,
        help='Si está activo, la copia interna de facturas y recibos se '
             'imprime con una leyenda que la identifica como documento sin '
             'valor fiscal. La representación impresa válida ante DGI sigue '
             'siendo la que emite UCFE.',
    )

    internal_copy_watermark_text = fields.Char(
        string='Texto de la leyenda',
        translate=True,
        default=lambda self: _('COPIA INTERNA - SIN VALOR FISCAL'),
        help='Texto que se imprime en la copia interna cuando la leyenda '
             'está activa.',
    )
