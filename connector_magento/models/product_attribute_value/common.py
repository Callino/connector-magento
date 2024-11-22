import logging
from odoo import models, fields, api
from odoo.addons.component.core import Component
import urllib.request, urllib.parse, urllib.error
_logger = logging.getLogger(__name__)


class MagentoProductAttributevalue(models.Model):
    _name = 'magento.product.attribute.value'
    _inherit = 'magento.binding'
    # _inherits = {'product.attribute.value': 'odoo_id'}
    _description = 'Magento attribute value'

    odoo_id = fields.Many2one(comodel_name='product.attribute.value',
                              string='Product attribute value',
                              required=False, # Was True
                              ondelete='cascade')
    magento_attribute_id = fields.Many2one(comodel_name='magento.product.attribute',
                                       string='Magento Product Attribute',
                                       required=True,
                                       ondelete='cascade',
                                       index=True)
    attribute_id = fields.Many2one(related='magento_attribute_id.odoo_id')
    name = fields.Char(related='odoo_id.name')
    magento_attribute_type = fields.Selection(
         related="magento_attribute_id.frontend_input",
         store=True
        )
    # The real magento code - external_id is a combination of attribute_id + _ + code
    code = fields.Char('Magento Code for the value')
    label = fields.Char('Magento Label')
    main_text_code = fields.Char('Main text code eg. swatch or default value')
    backend_id = fields.Many2one(
        related='magento_attribute_id.backend_id',
        string='Magento Backend',
        readonly=True,
        store=True,
        # override 'magento.binding', can't be INSERTed if True:
        required=False,
    )


class ProductAttributevalue(models.Model):
    _inherit = 'product.attribute.value'

    magento_bind_ids = fields.One2many(
        comodel_name='magento.product.attribute.value',
        inverse_name='odoo_id',
        string='Magento Bindings',
    )


class ProductAttributeValueAdapter(Component):
    _name = 'magento.product.attribute.value.adapter'
    _inherit = 'magento.adapter'
    _apply_on = 'magento.product.attribute.value'

    _magento2_model = 'products/attributes/%(attribute_code)s/options'
    _magento2_search = 'options'
    _magento2_key = 'id'
    _magento2_name = 'option'

    def read(self, id, attributes=None,storeview=None, **kwargs):
        """ Returns the information of a record

        :rtype: dict
        """
        if self.work.magento_api._location.version == '2.0':
            # TODO: storeview_code context in Magento 2.0
            res_admin = super(ProductAttributeValueAdapter, self).read(
                id, attributes=attributes, storeview='all',**kwargs)
            if res_admin:
                for attr in res_admin.get('custom_attributes', []):
                    res_admin[attr['attribute_code']] = attr['value']
            return res_admin
        return super(ProductAttributeValueAdapter, self).read(id, attributes=None,storeview=None)

    def _create_url(self, binding=None):
        return '%s' % (self._magento2_model % {'attributeCode': binding.magento_attribute_id.attribute_code})

    def delete(self, magento_value_id, magento_attribute_id):
        """ Delete a record on the external system """
        if self.work.magento_api._location.version == '2.0':
            res = self._call('%s/%s' % (self._magento2_model % {'attributeCode': magento_attribute_id}, self.escape(magento_value_id)), http_method="delete")
            return res
        return self._call('%s.delete' % self._magento_model, [int(id)])

    def _get_id_from_create(self, result, data=None):
        return data['value']
