from odoo.addons.component.core import Component


class OnChangeManager(Component):
    _inherit = 'ecommerce.onchange.manager'

    def get_new_values(self, record, on_change_result, model=None):
        vals = on_change_result.get('value', {})
        new_values = {}
        for fieldname, value in vals.items():
            if fieldname not in record:
                if model:
                    column = self.env[model]._fields[fieldname]
                    if column.type == 'many2one' and value:
                        value = value[0]  # many2one are tuple (id, name)
                new_values[fieldname] = value
        return new_values