# -*- coding: utf-8 -*-
# Copyright 2013-2017 Camptocamp SA
# Copyright 2019 Callino
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping, only_create
import logging

_logger = logging.getLogger(__name__)


class MagentoStockItemExporter(Component):
    _name = 'magento.stock.item.exporter'
    _inherit = 'magento.exporter'
    _apply_on = ['magento.stock.item']

    def _should_import(self):
        return False

    def _after_export(self):
        self.binding.with_context(connector_no_export=True).qty = self.binding.calculated_qty

    def run(self, binding, *args, **kwargs):
        self.binding = binding.sudo()
        self.external_id = self.binder.to_external(self.binding)
        # Read current stock items for product here to be able to check if it still does exists
        try:
            item = self.backend_adapter.read(self.external_id, binding=binding)
        except Exception as e:
            _logger.info("Stock item not found on read - so delete binding")
            binding.unlink()
            return True
        pbinding = binding.magento_product_binding_id or binding.magento_product_template_binding_id
        if not pbinding or pbinding.magento_status == '2' or not pbinding.active:
            _logger.info("Product is not active anymore - so no need to export here")
            return
        return super(MagentoStockItemExporter, self).run(binding)


class MagentoStockItemExportMapper(Component):
    _name = 'magento.stock.item.export.mapper'
    _inherit = 'magento.export.mapper'
    _apply_on = ['magento.stock.item']

    direct = [
        ('min_sale_qty', 'min_sale_qty'),
        ('is_qty_decimal', 'is_qty_decimal'),
    ]

    @mapping
    def min_qty(self, record):
        return {'min_qty': record.min_qty if record.min_qty else 0.0}

    @mapping
    def backorders(self, record):
        '''
        selection=[('use_default', 'Use Default Config'),
                   ('no', 'No Sell'), = 0
                   ('yes', 'Sell Quantity < 0'), = 1
                   ('yes-and-notification', 'Sell Quantity < 0 and ' = 2
                                            'Use Customer Notification')],
        '''
        if record.backorders == 'use_default':
            return
        map = {
            'no': 0,
            'yes': 1,
            'yes-and-notification': 2
        }
        return {
            'backorders': map[record.backorders],
            'use_config_backorders': False,
        }

    @mapping
    def qty(self, record):
        return {
            'qty': record.calculated_qty,
            'is_in_stock': True if record.product_type == 'configurable' or record.calculated_qty > 0 else False,
        }
