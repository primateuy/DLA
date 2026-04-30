# -*- coding: utf-8 -*-
import re
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_day_formula(formula_str, invoice_day):
    s = (formula_str or '').strip()
    if re.fullmatch(r'\d+', s):
        d = int(s)
        if not 1 <= d <= 31:
            raise ValueError(f"Fixed day must be 1-31, got {d}")
        return d
    m = re.fullmatch(r'day\s*([+-])\s*(\d+)', s, re.IGNORECASE)
    if m:
        sign = 1 if m.group(1) == '+' else -1
        return invoice_day + int(m.group(2)) * sign
    raise ValueError(
        f"Formula de dia invalida: '{s}'.\n"
        "Use un numero 1-31 o una expresion como 'day+5' / 'day-3'."
    )


def _parse_month_formula(formula_str, invoice_month):
    """
    Returns (target_month 1-12, extra_years, is_fixed_behaviour).

    is_fixed_behaviour=True  -> if result < invoice_date: advance +1 year
    is_fixed_behaviour=False -> if result < invoice_date: advance +1 month

    Rules:
      Fixed month (1-12)  -> is_fixed=True
      month+N where N > 0 -> is_fixed=False  (repeating forward offset)
      month+0 or month-N  -> is_fixed=True   (same or past month: yearly cycle)
    """
    s = (formula_str or '').strip()
    if re.fullmatch(r'\d+', s):
        month = int(s)
        if not 1 <= month <= 12:
            raise ValueError(f"Fixed month must be 1-12, got {month}")
        return month, 0, True

    m = re.fullmatch(r'month\s*([+-])\s*(\d+)', s, re.IGNORECASE)
    if m:
        sign = 1 if m.group(1) == '+' else -1
        offset = int(m.group(2)) * sign
        total = invoice_month + offset
        extra_years, target_month = divmod(total - 1, 12)
        # offset > 0: forward relative -> advance by month if past
        # offset <= 0: same or backward -> advance by year if past
        is_fixed = (offset <= 0)
        return target_month + 1, extra_years, is_fixed

    raise ValueError(
        f"Formula de mes invalida: '{s}'.\n"
        "Use un numero 1-12 o una expresion como 'month+5' / 'month-1'."
    )


def _compute_fixed_date(invoice_date, day_formula_str, month_formula_str):
    """
    Compute the next occurrence of the target date from invoice_date.

    Advance logic when candidate < invoice_date:
      is_fixed=True  (fixed month, month+0, month-N) -> +1 year
      is_fixed=False (month+N where N>0)             -> +1 month
    """
    raw_day = _parse_day_formula(day_formula_str, invoice_date.day)
    target_month, extra_years, is_fixed_month = _parse_month_formula(
        month_formula_str, invoice_date.month
    )
    candidate_year = invoice_date.year + extra_years
    last_day = calendar.monthrange(candidate_year, target_month)[1]
    candidate = date(candidate_year, target_month, max(1, min(raw_day, last_day)))

    if candidate < invoice_date:
        if is_fixed_month:
            candidate_year += 1
            last_day = calendar.monthrange(candidate_year, target_month)[1]
            candidate = date(candidate_year, target_month, max(1, min(raw_day, last_day)))
        else:
            candidate = candidate + relativedelta(months=1)
            last_day = calendar.monthrange(candidate.year, candidate.month)[1]
            candidate = date(candidate.year, candidate.month, max(1, min(raw_day, last_day)))

    return candidate


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    delay_type = fields.Selection(
        selection_add=[('fixed_date_formula', 'Fecha fija / formula (proxima ocurrencia)')],
        ondelete={'fixed_date_formula': 'cascade'},
    )

    fixed_day_formula = fields.Char(
        string='Dia objetivo',
        default='31',
        help=(
            "Dia fijo o formula relativa al dia de la factura.\n"
            "\n"
            "Ejemplos:\n"
            "  31      -> dia 31 fijo (se ajusta al ultimo dia del mes)\n"
            "  15      -> dia 15 fijo\n"
            "  day+5   -> dia de factura + 5 dias\n"
            "  day+0   -> mismo dia que la factura\n"
            "  day-3   -> dia de factura - 3 dias\n"
            "\n"
            "El dia se ajusta automaticamente si el mes tiene menos dias."
        ),
    )

    fixed_month_formula = fields.Char(
        string='Mes objetivo',
        default='1',
        help=(
            "Mes fijo o formula relativa al mes de la factura.\n"
            "\n"
            "Mes fijo (numero 1-12):\n"
            "  1       -> enero\n"
            "  6       -> junio\n"
            "  12      -> diciembre\n"
            "\n"
            "Formula relativa:\n"
            "  month+0 -> mismo mes\n"
            "  month+1 -> mes siguiente\n"
            "  month+5 -> 5 meses despues\n"
            "  month-1 -> mes anterior\n"
            "\n"
            "Si la fecha calculada ya paso:\n"
            "  mes fijo, month+0, month-N -> avanza 1 anio\n"
            "  month+N (N>0)              -> avanza 1 mes"
        ),
    )

    @api.constrains('delay_type', 'fixed_day_formula', 'fixed_month_formula')
    def _check_fixed_date_formula(self):
        for line in self:
            if line.delay_type != 'fixed_date_formula':
                continue
            try:
                _parse_day_formula(line.fixed_day_formula or '', 1)
            except ValueError as e:
                raise ValidationError(
                    _("Formula de dia invalida en '%s': %s") % (line.payment_id.name, e)
                ) from e
            try:
                _parse_month_formula(line.fixed_month_formula or '', 1)
            except ValueError as e:
                raise ValidationError(
                    _("Formula de mes invalida en '%s': %s") % (line.payment_id.name, e)
                ) from e

    def _get_due_date(self, date_ref):
        if self.delay_type != 'fixed_date_formula':
            return super()._get_due_date(date_ref)
        if not date_ref:
            return fields.Date.today()
        return _compute_fixed_date(
            invoice_date=date_ref,
            day_formula_str=self.fixed_day_formula or '31',
            month_formula_str=self.fixed_month_formula or '1',
        )


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    def _get_fixed_date_preview(self):
        self.ensure_one()
        today = fields.Date.today()
        lines_info = []
        for line in self.line_ids:
            if line.delay_type == 'fixed_date_formula':
                try:
                    due = _compute_fixed_date(
                        today,
                        line.fixed_day_formula or '31',
                        line.fixed_month_formula or '1',
                    )
                    lines_info.append(f"{line.value_amount:.0f}% -> {due.strftime('%d/%m/%Y')}")
                except Exception:
                    lines_info.append("(formula invalida)")
        return ' | '.join(lines_info) if lines_info else ''
