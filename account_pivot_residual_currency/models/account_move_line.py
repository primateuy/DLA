# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # amount_residual_currency existe nativamente en account.move.line
    # como campo stored. Se redefine únicamente para agregar group_operator='sum'
    # que es el atributo que habilita el campo como medida en la vista pivot.
    amount_residual_currency = fields.Monetary(
        group_operator='sum',
    )
