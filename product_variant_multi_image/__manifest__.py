# -*- coding: utf-8 -*-
{
    'name': 'Product variant Multi Image',
    'version': '16.0.0.0.0',
    'category': 'Sales',
    'description': """
Website Product Variant Multi Images.
=========================================================================

    """,
    'author': 'Callino',
    'website': 'https://www.callino.at',
    'depends': ['website_sale'],
    'license': 'AGPL-3',
    'installable': False,
    'data': [
        'views/product_view.xml',
        'views/templates.xml',
        'views/image_kanban.xml',
        'views/product_image.xml',
        'views/attribute.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'product_variant_multi_image/static/src/js/website_sale.js',
            'product_variant_multi_image/static/src/scss/product_variant_multi_image.scss',
        ],
    },
}
