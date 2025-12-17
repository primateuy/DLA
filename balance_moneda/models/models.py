from odoo import models, fields, api

class AccountMoveLine (models.Model):
    # Se extende el modelo 'account.move.line' para agregar funcionalidad personalizada.
    _inherit = 'account.move.line'

    # Campo nuevo: Balance en Moneda
    # Este campo almacena el balance de la línea contable en la moneda definida en la cuenta contable.
    balance_currency = fields.Monetary(
        string = 'Balance en Moneda',                 # Etiqueta que se muestra al usuario.
        currency_field = 'account_currency_id',       # Moneda relacionada, definida en la cuenta contable.
        compute = '_compute_balance_currency',        # Método que calcula el valor del campo.
        store = True                                  # Almacena el valor en la base de datos para uso en búsquedas y vistas.
    )

    # Campo relacionado: Moneda de la Cuenta
    # Este campo toma la moneda definida en la cuenta contable asociada a la línea (`account_id.currency_id`).
    account_currency_id = fields.Many2one(
        'res.currency',                               # Relación con el modelo de monedas en Odoo.
        related = 'account_id.currency_id',           # Relacionado directamente con la moneda de la cuenta contable.
        string = 'Moneda de la Cuenta',               # Etiqueta que se muestra al usuario.
        readonly = True                               # Este campo es de solo lectura porque se calcula automáticamente.
    )

    # Método para calcular el campo `balance_currency`.
    # Dependencias: `debit`, `credit`, `amount_currency`, `currency_id`, `account_currency_id`.
    @api.depends ('debit', 'credit', 'amount_currency', 'currency_id', 'account_currency_id')
    def _compute_balance_currency (self):
        for line in self:
            # Si la cuenta tiene una moneda definida (`account_currency_id`).
            if line.account_currency_id:
                # Si la moneda de la línea coincide con la moneda de la cuenta.
                if line.currency_id == line.account_currency_id:
                    # Usamos el monto en divisa directamente como balance.
                    line.balance_currency = line.amount_currency

                # Si no hay moneda en la línea o es igual a la moneda de la compañía.
                elif not line.currency_id or line.currency_id == line.company_currency_id:
                    # El balance se calcula como el saldo (debe - haber) en la moneda de la compañía.
                    line.balance_currency = line.debit - line.credit

                # Si la moneda de la línea es distinta de la moneda de la cuenta.
                else:
                    # Convertimos el balance (debe - haber) de la moneda de la línea a la moneda de la cuenta.
                    balance = line.debit - line.credit
                    line.balance_currency = line.currency_id._convert(
                        balance,                    # Monto a convertir.
                        line.account_currency_id,   # Moneda destino.
                        line.company_id,            # Compañía a la que pertenece la línea.
                        line.date                   # Fecha para la tasa de conversión.
                    )

            # Si no hay moneda definida en la cuenta.
            else:
                # Calculamos el balance como el saldo (debe - haber) en la moneda de la compañía.
                line.balance_currency = line.debit - line.credit
