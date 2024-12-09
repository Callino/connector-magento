# © 2013 Guewen Baconnier,Camptocamp SA,Akretion
# © 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

import logging

_logger = logging.getLogger(__name__)

class MagentoModelBinder(Component):
    """ Bind records and give odoo/magento ids correspondence

    Binding models are models called ``magento.{normal_model}``,
    like ``magento.res.partner`` or ``magento.product.product``.
    They are ``_inherits`` of the normal models and contains
    the Magento ID, the ID of the Magento Backend and the additional
    fields belonging to the Magento instance.
    """
    _name = 'magento.binder'
    _inherit = ['base.binder', 'base.magento.connector']
    _apply_on = [
        'magento.website',
        'magento.store',
        'magento.storeview',
        'magento.res.partner',
        'magento.address',
        'magento.res.partner.category',
        'magento.product.category',
        'magento.product.product',
        'magento.stock.picking',
        'magento.stock.item',
        'magento.stock.warehouse',
        'magento.sale.order',
        'magento.sale.order.line',
        'magento.account.invoice',
        'magento.account.tax',
        'magento.product.attribute.set',
        'magento.product.attribute',
        'magento.product.attribute.value',
        'magento.product.template',
        'magento.product.template.attribute.line',
    ]

    def to_internal(self, external_id, unwrap=False, external_field=None):
        """ Give the Odoo recordset for an external ID

        :param external_id: external ID for which we want
                            the Odoo ID
        :param unwrap: if True, returns the normal record
                       else return the binding record
        :return: a recordset, depending on the value of unwrap,
                 or an empty recordset if the external_id is not mapped
        :rtype: recordset
        """
        context = self.env.context
        if not external_field:
            bindings = self.model.with_context(active_test=False).search(
                [(self._external_field, '=', external_id),
                 (self._backend_field, '=', self.backend_record.id)]
            )
        else:
            bindings = self.model.with_context(active_test=False).search(
                [(external_field, '=', external_id),
                 (self._backend_field, '=', self.backend_record.id)]
            )
        if not bindings:
            if unwrap:
                return self.model.browse()[self._odoo_field]
            return self.model.browse()
        if len(bindings) > 1:
            _logger.error("Got %s bindings for %s with value %s", len(bindings), external_field, external_id)
        bindings.ensure_one()
        if unwrap:
            bindings = bindings[self._odoo_field]
        bindings = bindings.with_context(**context)
        return bindings
