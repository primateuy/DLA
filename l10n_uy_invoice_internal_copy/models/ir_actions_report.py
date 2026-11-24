# -*- coding: utf-8 -*-
import logging

from odoo import models

# Implementación nativa de Odoo para account. La importamos para poder
# invocarla directamente y saltar los overrides que la localización monta
# encima (l10n_uy_einvoice_uruware intercepta TODO reporte sobre
# account.move / account.payment y devuelve el PDF que emite UCFE).
# Mismo patrón que l10n_uy_einvoice_base_multicountry_fix.
from odoo.addons.account.models.ir_actions_report import (
    IrActionsReport as AccountIrActionsReport,
)

_logger = logging.getLogger(__name__)

# Reportes de copia interna definidos por este módulo. Se identifican por
# report_name porque es el dato que trae el reporte ya resuelto y evita
# tener que leer los xmlid en cada render.
INTERNAL_COPY_REPORT_NAMES = (
    'l10n_uy_invoice_internal_copy.report_invoice_internal_copy',
    'l10n_uy_invoice_internal_copy.report_payment_receipt_internal_copy',
)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _is_internal_copy_report(self, report_ref):
        """Indica si el reporte pedido es una de las copias internas."""
        report = self._get_report(report_ref)
        return report.report_name in INTERNAL_COPY_REPORT_NAMES

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """Genera el PDF de Odoo para los reportes de copia interna.

        Para cualquier otro reporte delega en super(), de modo que el flujo
        de facturación electrónica queda intacto: los reportes estándar
        siguen devolviendo el CFE oficial de UCFE.
        """
        if self._is_internal_copy_report(report_ref):
            _logger.info(
                "Copia interna: se omite la descarga del CFE y se genera el "
                "PDF de Odoo para %s (ids: %s)",
                self._get_report(report_ref).report_name, res_ids,
            )
            return AccountIrActionsReport._render_qweb_pdf_prepare_streams(
                self, report_ref, data, res_ids=res_ids
            )
        return super()._render_qweb_pdf_prepare_streams(
            report_ref, data, res_ids=res_ids
        )
