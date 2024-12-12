# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models, fields
from odoo.addons.component.core import Component
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)


class MagentoStockItem(models.Model):
    _name = 'magento.stock.item'
    _inherit = 'magento.binding'
    _description = 'Magento Stock Item'

    @api.depends('magento_warehouse_id', 'qty', 'magento_product_binding_id', 'magento_product_binding_id.no_stock_sync')
    def _compute_qty(self):
        for stockitem in self.sudo():
            stock_field = stockitem.magento_warehouse_id.quantity_field or 'virtual_available'
            if stockitem.magento_warehouse_id.calculation_method == 'real':
                product_fields = [stock_field]
                if stockitem.product_type == 'product':
                    record_with_warehouse = stockitem.magento_product_binding_id.odoo_id.with_context(
                        warehouse=stockitem.magento_warehouse_id.odoo_id.id)
                else:
                    record_with_warehouse = stockitem.magento_product_template_binding_id.odoo_id.with_context(
                        warehouse=stockitem.magento_warehouse_id.odoo_id.id)
                result = record_with_warehouse.read(product_fields)[0]
                stockitem.calculated_qty = result[stock_field]
            elif stockitem.magento_warehouse_id.calculation_method == 'fix':
                stockitem.calculated_qty = stockitem.magento_warehouse_id.fixed_quantity

            if stockitem.magento_product_binding_id.backend_id.no_stock_sync:
                # Never export if no stock sync is enabled
                stockitem.should_export = False
                continue
            if stockitem.calculated_qty == stockitem.qty:
                # Do not export when last exported qty is the same as the current
                stockitem.should_export = False
                continue
            stockitem.should_export = True


    magento_product_binding_id = fields.Many2one(comodel_name='magento.product.product',
                                                 string='Product',
                                                 required=False,
                                                 ondelete='cascade')
    magento_product_template_binding_id = fields.Many2one(comodel_name='magento.product.template',
                                                          string='Product Template',
                                                          required=False,
                                                          ondelete='cascade')
    product_type = fields.Selection([
        ('product', 'Product'),
        ('configurable', 'Configurable'),
    ], default='product', string="Product Type")
    magento_warehouse_id = fields.Many2one(comodel_name='magento.stock.warehouse',
                                           string='Warehouse',
                                           required=True,
                                           ondelete='cascade')
    qty = fields.Float(string='Quantity', default=-999)
    calculated_qty = fields.Float(string='Calculated Qty.', compute='_compute_qty', compute_sudo=True)
    should_export = fields.Boolean(string='Should Export', compute='_compute_qty', compute_sudo=True)
    min_sale_qty = fields.Float(string='Min Sale Qty', default=1.0)
    is_qty_decimal = fields.Boolean(string='Decimal Qty.', default=False)
    is_in_stock = fields.Boolean(string='In Stock From Magento')
    min_qty = fields.Float('Min. Qty.', default=0.0)
    backorders = fields.Selection(
        selection=[('use_default', 'Use Default Config'),
                   ('no', 'No Sell'),
                   ('yes', 'Sell Quantity < 0'),
                   ('yes-and-notification', 'Sell Quantity < 0 and '
                                            'Use Customer Notification')],
        string='Manage Inventory Backorders',
        default='use_default',
        required=True,
    )

    def sync_from_magento(self):
        for binding in self:
            binding.with_delay(priority=5).run_sync_from_magento()

    def run_sync_from_magento(self):
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(self.external_id, force=True, binding=self)

    def sync_to_magento(self, force=False):
        for binding in self:
            if force or binding.should_export:
                delayed = binding.with_delay(priority=5).run_sync_to_magento()
                job = self.env['queue.job'].search([('uuid', '=', delayed.uuid)])
                if binding.magento_product_template_binding_id:
                    binding.magento_product_template_binding_id.odoo_id.with_context(connector_no_export=True).job_ids += job
                else:
                    binding.magento_product_binding_id.odoo_id.product_tmpl_id.with_context(connector_no_export=True).job_ids += job

    def run_sync_to_magento(self):
        _logger.info("Stock Item sync to magento got called, ")
        self.ensure_one()
        try:
            with self.backend_id.work_on(self._name) as work:
                exporter = work.component(usage='record.exporter')
                return exporter.run(self)
        except MissingError as e:
            return True


class MagentoStockItemAdapter(Component):
    _name = 'magento.stock.item.adapter'
    _inherit = 'magento.adapter'
    _apply_on = 'magento.stock.item'

    _magento_model = 'stockItems'
    _magento2_model = 'stockItems'
    _magento2_name = 'stockItem'
    _magento2_search = 'stock/search'
    _magento2_key = 'id'
    _admin_path = '/{model}/edit/id/{id}'

    def write(self, id, binding):
        if binding.product_type=='product':
            return "products/%(sku)s/stockItems/%(id)s" % {
                'sku': binding.magento_product_binding_id.external_id,
                'id': binding.external_id
            }
        else:
            return "products/%(sku)s/stockItems/%(id)s" % {
                'sku': binding.magento_product_template_binding_id.external_id,
                'id': binding.external_id
            }

    def read(self, id, binding):
        if binding.product_type=='product':
            return 'stockItems/%(sku)s' % {
                'sku': binding.magento_product_binding_id.external_id,
            }
        else:
            return 'stockItems/%(sku)s' % {
                'sku': binding.magento_product_template_binding_id.external_id,
            }
