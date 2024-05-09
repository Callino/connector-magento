# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class WizardModel(models.TransientModel):
    _name = "connector_magento.add_backend.wizard"

    # @api.multi
    def get_default_object(self, model):
        domain = []
        active_ids = self.env.context.get('active_ids', False)
        active_model = self.env.context.get('active_model', False)

        if not active_ids:
            return []
        domain.append(('id', 'in', active_ids))
        export = self.env[active_model]
        if active_model == model:
            return export.search(domain)

    # @api.multi
    def get_default_model(self):
        model = self.env.context.get('active_model', False)
        if model:
            return self.env['ir.model'].search([('model', '=', model)], limit=1).id
        return False

    # @api.multi
    def get_default_backend(self):
        return self.env['magento.backend'].search([], limit=1)

    # @api.multi
    def _get_ids_and_model(self):
        active_model = self.env.context.get('active_model', False)
        if hasattr(self.env[active_model], 'magento_bind_ids'):
            bindings=self.env[active_model].browse(self.env.context.get('active_ids', []))
            return bindings , self.env[active_model].magento_bind_ids._name
        else:
            raise ValueError('Model not supported')

    # @api.multi
    def check_backend_binding(self, to_export_ids=None, dest_model=None):
        if not dest_model or not to_export_ids:
            (to_export_ids, dest_model) = self._get_ids_and_model()
        for model in to_export_ids:
            bind_count = self.env[dest_model].search_count([
                ('odoo_id', '=', model.id),
                ('backend_id', '=', self.backend_id.id)
            ])
            if not bind_count:
                vals = {
                    'odoo_id': model.id,
                    'backend_id': self.backend_id.id
                }
                self.env[dest_model].create(vals)

    backend_id = fields.Many2one(comodel_name='magento.backend', required=True, default=get_default_backend)
    model_id = fields.Many2one('ir.model', default=get_default_model)

    def action_accept(self):
        self.ensure_one()
        self.check_backend_binding()
