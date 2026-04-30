# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Categoría del producto de la línea
    product_categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Categoría de producto',
        related='product_id.categ_id',
        store=True,
        index=True,
        readonly=True,
    )

    # Vendedor de la factura — se almacena en la línea para poder agrupar/filtrar.
    # Nombre move_user_id para evitar colisión con campos nativos o de otros módulos.
    move_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Vendedor',
        related='move_id.invoice_user_id',
        store=True,
        index=True,
        readonly=True,
    )

    # Equipo de ventas de la factura — mismo criterio de nombre.
    move_team_id = fields.Many2one(
        comodel_name='crm.team',
        string='Equipo de ventas',
        related='move_id.team_id',
        store=True,
        index=True,
        readonly=True,
    )
