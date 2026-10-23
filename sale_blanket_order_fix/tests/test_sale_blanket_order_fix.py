# Copyright 2026
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
"""Tests de las correcciones de sale_blanket_order_fix.

Cada test cubre un hallazgo concreto de la revisión técnica de la entrega
17.0.1.2.1. Los que empiezan con ``test_regresion_`` protegen comportamiento
que el módulo rompía; el resto verifica el alcance funcional declarado.
"""
from datetime import date, timedelta

from lxml import etree

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestSaleBlanketOrderFix(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente de prueba"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Lista de prueba", "currency_id": cls.env.company.currency_id.id}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Producto de prueba", "type": "consu", "sale_ok": True}
        )

    def _crear_acuerdo(self, qty=100.0, price=50.0):
        return self.env["sale.blanket.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "validity_date": date.today() + timedelta(days=365),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "original_uom_qty": qty,
                            "price_unit": price,
                            "product_uom": self.product.uom_id.id,
                        },
                    )
                ],
            }
        )

    # --- numeración -----------------------------------------------------

    def test_numero_estable_al_reconfirmar(self):
        """Volver a borrador y reconfirmar no debe cambiar el número."""
        acuerdo = self._crear_acuerdo()
        acuerdo.action_confirm()
        numero = acuerdo.name
        self.assertNotIn(numero, (False, "Draft"))
        for _ in range(3):
            acuerdo.set_to_draft()
            acuerdo.action_confirm()
            self.assertEqual(acuerdo.name, numero)

    def test_numero_manual_se_respeta(self):
        """Un número escrito a mano en borrador sobrevive a la confirmación."""
        acuerdo = self._crear_acuerdo()
        acuerdo.name = "ACME-2026-001"
        acuerdo.action_confirm()
        self.assertEqual(acuerdo.name, "ACME-2026-001")

    # --- líneas de un acuerdo confirmado --------------------------------

    def test_cantidad_editable_con_acuerdo_abierto(self):
        """La cantidad de una línea existente se puede ajustar en 'open'."""
        acuerdo = self._crear_acuerdo()
        acuerdo.action_confirm()
        self.assertEqual(acuerdo.state, "open")
        acuerdo.line_ids[0].write({"original_uom_qty": 150.0})
        self.assertEqual(acuerdo.line_ids[0].original_uom_qty, 150.0)

    def test_precio_bloqueado_con_acuerdo_abierto(self):
        """El precio de una línea existente no se puede cambiar fuera de borrador."""
        acuerdo = self._crear_acuerdo()
        acuerdo.action_confirm()
        with self.assertRaises(UserError):
            acuerdo.line_ids[0].write({"price_unit": 99.0})

    def test_borrado_bloqueado_con_acuerdo_abierto(self):
        """No se puede borrar una línea existente fuera de borrador."""
        acuerdo = self._crear_acuerdo()
        acuerdo.action_confirm()
        with self.assertRaises(UserError):
            acuerdo.line_ids[0].unlink()

    def test_cantidad_no_puede_bajar_de_lo_librado(self):
        """Hallazgo A2: el saldo negativo bloquea confirmar pedidos de venta."""
        acuerdo = self._crear_acuerdo(qty=100.0)
        acuerdo.action_confirm()
        linea = acuerdo.line_ids[0]
        asistente = (
            self.env["sale.blanket.order.wizard"]
            .with_context(active_id=acuerdo.id, active_model="sale.blanket.order")
            .create({})
        )
        asistente.line_ids.write({"qty": 80.0})
        asistente.create_sale_order()
        linea.invalidate_recordset()
        self.assertEqual(linea.ordered_uom_qty, 80.0)
        with self.assertRaises(ValidationError):
            linea.write({"original_uom_qty": 40.0})

    # --- regresiones que introducía la entrega 17.0.1.2.1 ----------------

    def test_regresion_todos_los_campos_de_linea_se_bloquean(self):
        """Hallazgo B1: el xpath compuesto solo aplicaba a product_id."""
        vista = self.env.ref("sale_blanket_order.view_blanket_order_form")
        arch = etree.fromstring(
            self.env["sale.blanket.order"].get_view(vista.id, "form")["arch"]
        )
        readonly = {
            campo.get("name"): campo.get("readonly")
            for campo in arch.xpath("//field[@name='line_ids']//tree/field")
        }
        for nombre in ("product_id", "price_unit", "taxes_id", "date_schedule", "name"):
            self.assertEqual(
                readonly.get(nombre),
                "parent.state != 'draft' and id",
                f"el campo {nombre} quedó sin bloqueo condicional",
            )

    def test_regresion_note_conserva_el_default(self):
        """Hallazgo B2: note = fields.Html() descartaba default=_default_note."""
        campo = self.env["sale.blanket.order"]._fields["note"]
        self.assertEqual(campo.type, "html")
        self.assertIsNotNone(
            campo.default, "note perdió el default de Términos y Condiciones"
        )

    def test_regresion_relabel_es_aplica_con_variante_regional(self):
        """Hallazgo A1: el hook comparaba contra 'es' y la base usa 'es_UY'."""
        from odoo.addons.sale_blanket_order_fix.hooks import _spanish_langs

        self.env.ref("base.lang_es_UY").active = True
        self.assertIn("es_UY", _spanish_langs(self.env))

    def test_regresion_numeracion_es_unica(self):
        """Hallazgo A3: name editable sin constraint permitía duplicados."""
        from psycopg2 import IntegrityError

        from odoo.tools import mute_logger

        primero = self._crear_acuerdo()
        primero.action_confirm()
        segundo = self._crear_acuerdo()
        segundo.action_confirm()
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            segundo.name = primero.name
            segundo.flush_recordset()

    # --- descripción de línea -------------------------------------------

    def test_descripcion_usa_display_name(self):
        """La descripción de línea sale del display_name, no del nombre de plantilla."""
        acuerdo = self._crear_acuerdo()
        linea = acuerdo.line_ids[0]
        linea.onchange_product()
        self.assertIn(self.product.display_name, linea.name or "")
