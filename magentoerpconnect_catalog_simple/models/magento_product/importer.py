# -*- coding: utf-8 -*-
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from openerp import models, fields
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)
from openerp.addons.magentoerpconnect.product import (
    ProductImportMapper)
from openerp.addons.magentoerpconnect.backend import magento


@magento
class ProductImportMapper(ProductImportMapper):

    _model_name = 'magento.product.product'

    direct = ProductImportMapper.direct + [
        ('meta_title','website_meta_title'),
        ('url_key','url_key'),
        ('meta_description','website_meta_description'),
        ('meta_keyword','website_meta_keywords'),        
        ]

