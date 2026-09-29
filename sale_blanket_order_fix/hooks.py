# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
"""Traducción ES reversible de sale_blanket_order.

En vez de un i18n/es.po (que sobreescribe la traducción de OCA de forma
NO reversible al desinstalar, porque queda escrita sobre registros que
pertenecen a sale_blanket_order, no a este módulo), usamos la API pública
``update_field_translations`` de Odoo 17+ en un ``post_init_hook`` /
``uninstall_hook`` simétrico: instalar aplica "Acuerdo Comercial",
desinstalar restaura exactamente el texto original de OCA
("Pedido Programado"). Así la instalación base queda intacta.

Cada tupla es (xmlid, campo, texto_en_original, es_de_OCA, es_nuevo).
Los textos fueron verificados contra
sale_blanket_order/i18n/es.po (rama 17.0 del repo OCA/sale-workflow —
para 17.0 el módulo vive ahí, no en OCA/sale-blanket; ver README de este
módulo). Se confirmaron idénticos a los de la rama 19.0 (mismos xmlids,
mismos msgid/msgstr) y se verificó que update_field_translations() existe
con la misma firma en odoo/models.py de la rama 17.0 de odoo/odoo.
"""

LANG = "es"

# Campos Char/Text simples (translate=True): ir.model.name,
# ir.actions.act_window.name, ir.ui.menu.name, ir.model.fields.field_description.
_FIELD_TRANSLATIONS = [
    (
        "sale_blanket_order.model_sale_blanket_order",
        "name",
        "Pedido Programado",
        "Acuerdo Comercial",
    ),
    (
        "sale_blanket_order.model_sale_blanket_order_line",
        "name",
        "Línea de Pedido Programado",
        "Línea de Acuerdo Comercial",
    ),
    (
        "sale_blanket_order.field_sale_blanket_order_wizard__blanket_order_id",
        "field_description",
        "Pedido Programado",
        "Acuerdo Comercial",
    ),
    (
        "sale_blanket_order.act_open_blanket_order_view",
        "name",
        "Pedidos Programados",
        "Acuerdos Comerciales",
    ),
    (
        "sale_blanket_order.act_open_sale_blanket_order_lines_view_tree",
        "name",
        "Líneas de Pedido Programado",
        "Líneas de Acuerdo Comercial",
    ),
    (
        "sale_blanket_order.menu_blanket_order_config",
        "name",
        "Pedidos Programados",
        "Acuerdos Comerciales",
    ),
    (
        "sale_blanket_order.menu_sale_blanket_order_line",
        "name",
        "Líneas de Pedido Programado",
        "Líneas de Acuerdo Comercial",
    ),
]

# Términos embebidos dentro de un arch_db (xml_translate): requieren
# update_field_translations("arch_db", {lang: {texto_en: texto_es}}).
_ARCH_TRANSLATIONS = [
    (
        "sale_blanket_order.view_blanket_order_form",
        "Blanket Order",
        "Pedido Programado",
        "Acuerdo Comercial",
    ),
    (
        "sale_blanket_order.sale_config_settings_form_view",
        "Blanket Orders",
        "Pedidos Programados",
        "Acuerdos Comerciales",
    ),
]


def _spanish_is_installed(env):
    return LANG in {code for code, _name in env["res.lang"].get_installed()}


def _apply_translations(env, *, restore):
    """``restore=False`` aplica "Acuerdo Comercial"; ``restore=True``
    vuelve exactamente al texto original de OCA."""
    if not _spanish_is_installed(env):
        # No hay idioma español instalado en esta base: nada que tocar,
        # nada que restaurar.
        return

    for xmlid, field_name, es_oca, es_nuevo in _FIELD_TRANSLATIONS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            record.update_field_translations(
                field_name, {LANG: es_oca if restore else es_nuevo}
            )

    for xmlid, en_term, es_oca, es_nuevo in _ARCH_TRANSLATIONS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            record.update_field_translations(
                "arch_db", {LANG: {en_term: es_oca if restore else es_nuevo}}
            )


def post_init_hook(env):
    """Se ejecuta una sola vez, en la instalación inicial del módulo.

    Nota: si el idioma español se activa DESPUÉS de instalar este
    módulo, este hook no se vuelve a disparar (Odoo solo lo llama en
    'install', no en 'upgrade'). En ese caso alcanza con reinstalar el
    módulo (no tiene datos propios, es una operación segura y barata).
    """
    _apply_translations(env, restore=False)


def uninstall_hook(env):
    """Restaura la traducción original de sale_blanket_order (OCA) para
    dejar la instalación base exactamente como estaba."""
    _apply_translations(env, restore=True)
