# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleBlanketOrderLine(models.Model):
    _inherit = "sale.blanket.order.line"

    @api.onchange("product_id", "original_uom_qty")
    def onchange_product(self):
        """Iguala la descripción de línea a la de sale.order (variante
        incluida).

        ``sale_blanket_order`` arma "name" a mano: ``self.product_id.name``
        (+ ``[code]`` + ``description_sale``). El problema es que
        ``product.product.name`` está delegado a
        ``product.template.name`` (mecanismo ``_inherits``): es el
        nombre de la PLANTILLA, sin las particularidades de la variante
        (talle, color, etc.). Dos variantes del mismo producto terminan
        con idéntico texto de línea.

        ``sale.order`` resuelve exactamente este caso con
        ``product.product.get_product_multiline_description_sale()``
        (definido en el módulo base ``product``, no en ``sale``: siempre
        disponible), que arma la descripción a partir de
        ``display_name`` — plantilla + "(atributos de variante)", con el
        prefijo "[código]" si corresponde — más ``description_sale`` en
        una segunda línea. Se llama primero a la implementación
        original (no se toca product_uom / price_unit / taxes_id, que
        siguen siendo correctos) y se corrige únicamente "name" después.

        Idioma: igual que ``sale.order.line._compute_name()``, la
        descripción se arma en el idioma del CLIENTE
        (``order_id._get_lang()``: idioma del partner si tiene uno
        configurado y no es el partner público, si no el idioma de
        sesión de quien carga el pedido), no necesariamente en el
        idioma de quien está armando el Acuerdo Comercial. Así, nombre
        de producto, descripción de venta y nombre de la variante
        (todos campos traducibles) salen en el idioma que va a leer el
        cliente en el PDF/portal, igual que en una orden de venta
        estándar.
        """
        result = super().onchange_product()
        if self.product_id:
            line = self
            if self.order_id:
                lang = self.order_id._get_lang()
                if lang != self.env.lang:
                    line = self.with_context(lang=lang)
            self.name = line.product_id.get_product_multiline_description_sale()
        return result

    # Campo relacionado y almacenado para poder mostrar el estado del
    # Acuerdo Comercial en la vista de líneas y, sobre todo, para poder
    # agrupar/filtrar por él (los "group by" de Odoo requieren un campo
    # propio del modelo, no soportan "order_id.state" directamente).
    order_state = fields.Selection(
        related="order_id.state",
        string="Estado del acuerdo",
        store=True,
        readonly=True,
    )

    def write(self, values):
        """Respaldo defensivo a nivel de modelo (no solo de vista).

        Las cantidades de líneas ya existentes se pueden modificar con el
        Acuerdo Comercial confirmado (ver vista), pero el precio unitario
        de una línea EXISTENTE nunca debe cambiar una vez que el pedido
        salió de borrador. Esto protege la integridad del dato aunque el
        cambio de precio llegue por import, RPC u otro módulo, no solo
        desde el formulario.

        Las líneas NUEVAS se agregan vía create() (no pasan por write()),
        por lo que no se ven afectadas por esta restricción y sí pueden
        tener precio propio.
        """
        if "price_unit" in values:
            locked_lines = self.filtered(
                lambda line: line.order_id.state != "draft"
            )
            if locked_lines:
                raise UserError(
                    _(
                        "No se puede modificar el precio de una línea de "
                        "un Acuerdo Comercial que ya no está en borrador. "
                        "Si necesita otro precio, agregue una línea nueva."
                    )
                )
        return super().write(values)

    def unlink(self):
        """No permitir borrar líneas ya existentes fuera de 'draft'.

        El bloqueo NO se puede lograr de forma confiable con el atributo
        delete="..." del <tree> en la vista, porque ese atributo solo
        admite un booleano estático (0/1), no una expresión evaluada por
        registro (verificado contra el código del cliente web de Odoo
        17.0: getActiveActions() en addons/web/static/src/views/utils.js
        sólo hace archParseBoolean() sobre el string literal — mismo
        comportamiento que en 19.0). Por eso el control real vive acá.
        """
        if self.filtered(lambda line: line.order_id.state != "draft"):
            raise UserError(
                _(
                    "No se puede eliminar una línea de un Acuerdo "
                    "Comercial que ya no está en borrador."
                )
            )
        return super().unlink()
