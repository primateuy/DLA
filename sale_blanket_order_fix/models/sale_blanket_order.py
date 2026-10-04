# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class SaleBlanketOrder(models.Model):
    _inherit = "sale.blanket.order"

    # ``sale_blanket_order`` define "name" como Char(readonly=True): el
    # número queda bloqueado en toda vista salvo que el propio arch lo
    # anule explícitamente. Acá solo tocamos el atributo que cambia; el
    # resto (default="Draft", copy=False) se hereda de la definición
    # original vía el mecanismo estándar de fusión de atributos de Odoo
    # al extender un modelo por herencia clásica. El desbloqueo visual
    # real ocurre en la vista (ver views/sale_blanket_order_views.xml,
    # xpath sobre //h1/field[@name='name']); este cambio a nivel Python
    # es defensivo, para que cualquier vista que no fije "readonly"
    # explícitamente también respete la intención de campo editable.
    name = fields.Char(readonly=False)

    # ``sale_blanket_order`` define "note" como Text plano: se visualiza
    # sin formato. En ``sale.order`` el mismo campo ("Terms and
    # conditions") es un fields.Html, lo que habilita el editor
    # enriquecido (widget html) automáticamente, sin tocar la vista.
    # Html hereda de Text (mismo column_type "text" en PostgreSQL), por
    # lo que el cambio de tipo no requiere migración de columna y es
    # reversible al desinstalar: el campo vuelve a ser Text y el
    # contenido HTML ya guardado se sigue viendo (como texto con las
    # etiquetas visibles), sin pérdida de información.
    # OJO: al cambiar la CLASE del campo (Text -> Html) Odoo descarta
    # todos los atributos de la definición original. En
    # odoo/fields.py::_get_attrs, si `isinstance(self, type(field))` da
    # False se ejecuta `attrs.clear()`; y en Odoo 17 `Html` NO hereda de
    # `Text` (ambas son hermanas bajo `_String`). Sin repetir el default
    # acá, los acuerdos nuevos se crean con Términos y Condiciones
    # vacíos en vez de heredar los de la compañía.
    # Para `name` (Char sobre Char) no hace falta: ahí sí se fusionan.
    note = fields.Html(default=lambda self: self._default_note())

    def _get_lang(self):
        """Idioma a usar para textos traducibles del pedido (producto,
        descripción de venta, etc.), igual que ``sale.order._get_lang()``.

        ``sale_blanket_order`` no define ningún equivalente: sin este
        método, la descripción de línea (ver
        ``sale_blanket_order_line.onchange_product()``) se arma en el
        idioma de sesión de quien está cargando el pedido, no en el del
        cliente — distinto del estándar de Odoo, donde una cotización en
        español armada para un cliente con idioma inglés describe los
        productos en inglés (lo que el cliente va a leer), más allá del
        idioma de quien la carga.
        """
        self.ensure_one()
        if self.partner_id.lang and not self.partner_id.is_public:
            return self.partner_id.lang
        return self.env.lang

    def action_confirm(self):
        """Evita que se reasigne el número al reconfirmar.

        ``sale_blanket_order`` (17.0.2.3.0, OCA/sale-workflow) llama a
        ``ir.sequence.next_by_code`` en CADA ``action_confirm``, sin
        verificar si el pedido ya tenía un ``name`` asignado (idéntico al
        comportamiento verificado en la rama 19.0 del módulo). Esto
        provoca que, al hacer "Volver a borrador" + "Confirmar", el
        Acuerdo Comercial cambie de número.

        Estrategia defensiva: en vez de reimplementar la lógica de
        confirmación (que podría cambiar en próximas versiones de OCA),
        guardamos el nombre ANTES de llamar a ``super()`` y lo restauramos
        DESPUÉS solo si cambió. Si en el futuro OCA corrige este
        comportamiento en el módulo base, ``order.name`` ya será igual a
        ``original_name`` tras el ``super()`` y este método se convierte
        en un no-op transparente: seguirá instalado y funcionando sin
        interferir ni duplicar consumo de secuencia.
        """
        original_names = {order.id: order.name for order in self}
        result = super().action_confirm()
        for order in self:
            original_name = original_names.get(order.id)
            if (
                original_name
                and original_name not in (False, "Draft")
                and order.name != original_name
            ):
                order.name = original_name
        return result
