from odoo import models, fields, api
import math
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_cash_rounding_id = fields.Many2one(
        'account.cash.rounding',
        string='Cash Rounding',
    )

    amount_rounding = fields.Monetary(
        string='Rounding',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
    )

    amount_total = fields.Monetary(
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
    )

    # ------------------------------------------------------------------
    # PRIVATE HELPER
    # ------------------------------------------------------------------

    def _get_rounding_values(self):
        """
        Compute (rounding_diff, rounded_total) purely from stored/passed
        values — never reads amount_rounding or amount_total to avoid
        circular or ordering dependencies.

        Always safe to call from any compute method.
        Returns (0.0, raw_total) when no rounding configured.
        """
        self.ensure_one()

        # Read raw sub-totals directly from order lines — same source
        # that super()._compute_amounts() uses — so we never depend on
        # the computed amount_untaxed / amount_tax fields being ready.
        raw_untaxed = sum(
            self.order_line.filtered(
                lambda l: not l.display_type
            ).mapped('price_subtotal')
        )
        raw_tax = sum(
            self.order_line.filtered(
                lambda l: not l.display_type
            ).mapped('price_tax')
        )
        raw_total = raw_untaxed + raw_tax

        if not self.invoice_cash_rounding_id:
            return 0.0, raw_total

        cfg = self.invoice_cash_rounding_id
        precision = cfg.rounding

        if not precision:
            return 0.0, raw_total

        if cfg.rounding_method == 'UP':
            rounded_total = math.ceil(raw_total / precision) * precision
        elif cfg.rounding_method == 'DOWN':
            rounded_total = math.floor(raw_total / precision) * precision
        else:  # HALF-UP
            rounded_total = round(raw_total / precision) * precision

        # Use currency rounding to avoid floating point noise
        rounded_total = self.currency_id.round(rounded_total)
        rounding_diff = self.currency_id.round(rounded_total - raw_total)

        return rounding_diff, rounded_total

    # ------------------------------------------------------------------
    # COMPUTE METHODS
    # ------------------------------------------------------------------

    @api.depends(
        'order_line.price_total',
        'order_line.price_tax',
        'order_line.price_subtotal',
        'invoice_cash_rounding_id',
    )
    def _compute_amounts(self):
        super()._compute_amounts()

        for order in self:
            if not order.invoice_cash_rounding_id:
                # Ensure field is reset if rounding was removed
                order.amount_rounding = 0.0
                continue

            rounding_diff, rounded_total = order._get_rounding_values()
            order.amount_rounding = rounding_diff
            order.amount_total = rounded_total

            _logger.debug(
                "Sale Order %s | diff: %s | rounded total: %s",
                order.name, rounding_diff, rounded_total,
            )

    @api.depends(
        'order_line.price_total',
        'order_line.price_tax',
        'order_line.price_subtotal',
        'invoice_cash_rounding_id',
    )
    def _compute_tax_totals(self):
        """
        After super() builds the tax_totals dict (without rounding),
        patch the Total line keys so the widget shows the rounded value.
        Reads line totals directly via _get_rounding_values() — never
        reads amount_rounding or amount_total to avoid ORM order issues.
        """
        super()._compute_tax_totals()

        for order in self:
            if not order.invoice_cash_rounding_id:
                continue
            if not order.tax_totals:
                continue

            rounding_diff, rounded_total = order._get_rounding_values()

            # Even if diff is zero, patch to keep dict consistent with
            # amount_total in case of floating point edge cases
            tax_totals = dict(order.tax_totals)

            tax_totals['amount_total'] = rounded_total
            tax_totals['formatted_amount_total'] = (
                order.currency_id.format(rounded_total)
            )
            # These keys are read by credit warning and duplicate detection
            tax_totals['total_amount_currency'] = rounded_total
            tax_totals['total_amount'] = rounded_total

            order.tax_totals = tax_totals

            _logger.debug(
                "Sale Order %s | tax_totals patched | rounded: %s | diff: %s",
                order.name, rounded_total, rounding_diff,
            )


    def _prepare_invoice(self):
        """
        Propagate cash rounding to the invoice so Odoo's native invoice
        rounding logic applies correctly on account.move.
        Do NOT patch invoice tax_totals manually — account.move handles
        it natively via _get_tax_totals_summary(cash_rounding=...).
        """
        vals = super()._prepare_invoice()
        if self.invoice_cash_rounding_id:
            vals['invoice_cash_rounding_id'] = self.invoice_cash_rounding_id.id
        return vals