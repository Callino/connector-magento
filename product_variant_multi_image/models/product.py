# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('base_product_image_ids')
    def _compute_product_images(self):
        for template in self:
            template.product_image_count = len(template.base_product_image_ids)

    base_product_image_ids = fields.One2many('product.image', 'base_product_tmpl_id', string='Base Images')
    product_image_count = fields.Integer('Image Count', compute='_compute_product_images', store=True)


    def product_images_button(self):
        self.ensure_one()
        # Do check if there is minimum one image for every attribute value with create_image
        for value in self.valid_product_attribute_value_ids.filtered(lambda v: v.create_image):
            image = self.env['product.image'].search(['&', ('attribute_value_id', '=', value.id), ('base_product_tmpl_id', '=', self.id)])
            if not image:
                p = self
                # Search for product variant with image with this value
                for variant in self.product_variant_ids.filtered(lambda v: value.id in v.attribute_value_ids.ids):
                    if variant.image:
                        p = variant
                        break
                # Create dummy image with main image content
                self.env['product.image'].create({
                    'name': self.name,
                    'attribute_value_id': value.id,
                    'base_product_tmpl_id': self.id,
                    'product_tmpl_id': self.id,
                    'image': p.image or None,
                })
        action = self.env.ref('product_variant_multi_image.action_product_image_kanban_view').read()[0]
        action['domain'] = [('base_product_tmpl_id', '=', self.id)]
        ctx = self.env.context.copy()
        ctx['default_product_tmpl_id'] = self.id
        ctx['default_base_product_tmpl_id'] = self.id
        action['context'] = ctx
        return action


class Product(models.Model):
    _inherit = "product.product"

    # Field Declaration
    product_variant_image_ids = fields.One2many('product.image', 'image_product_id', string='Images')


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    create_image = fields.Boolean('Extra Bild', default=False)


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    create_image = fields.Boolean('Extra Bild', related='attribute_id.create_image', store=True)


class ProductImage(models.Model):
    _inherit = 'product.image'
    _order = "sequence, id desc"

    @api.multi
    def _compute_base_product_id(self):
        for image in self:
            if image.product_tmpl_id:
                image.base_product_tmpl_id = image.product_tmpl_id.id
            elif image.image_product_id:
                image.base_product_tmpl_id = image.image_product_id.product_tmpl_id.id

    @api.onchange('attribute_value_id')
    def _onchange_attribute_value_id(self):
        if self.attribute_value_id:
            self.image_product_id = None

    @api.onchange('image_product_id')
    def _onchange_attribute_value_id(self):
        if self.image_product_id:
            self.attribute_value_id = None

    # Field Declaration
    image_product_id = fields.Many2one('product.product', "Product variant Images")
    base_product_tmpl_id = fields.Many2one('product.template', "Base Product Image", compute='_compute_base_product_id', store=True)
    sequence = fields.Integer('Position', default=0, index=True)
    valid_product_attribute_value_ids = fields.Many2many('product.attribute.value', related='base_product_tmpl_id.valid_product_attribute_value_ids')
    is_primary_image = fields.Boolean('Primary image', default=False)
    use_for_template = fields.Boolean('Vorlagenbild', default=True)
    attribute_value_id = fields.Many2one(
        "product.attribute.value",
        string="Attribute",
    )

    @api.model
    def default_get(self, fields):
        defaults = super(ProductImage, self).default_get(fields)
        default_attribute_value_id = self.env.context.get("default_attribute_value_id", None)
        default_product_tmpl_id = self.env.context.get("default_product_tmpl_id", None)
        sequence = 0
        if default_attribute_value_id and default_product_tmpl_id:
            himage = self.search([
                ('product_tmpl_id', '=', default_product_tmpl_id),
                ('attribute_value_id', '=', default_attribute_value_id),
            ], order='sequence DESC', limit=1)
            if himage:
                sequence = himage.sequence + 1
        if default_product_tmpl_id:
            defaults.update({
                'name': self.env['product.template'].browse(default_product_tmpl_id).name,
            })
        defaults.update({
            'sequence': sequence,
        })
        return defaults