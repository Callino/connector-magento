odoo.define('product_variant_multi_image.cart_update', function (require) {
    "use strict";

    var base = require('web_editor.base');
    var website_sale_cart = require('website_sale.cart');
    require('website_sale.website_sale');

    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
        function update_product_variant_image(event_source, product_id) {
            if ($('#o-carousel-product').length) {
                var $indicator = $(event_source).closest('tr.js_product, .oe_website_sale').find('.js_variant_indicator');
                $indicator.addClass('hidden').filter('.js_variant_product_'+ product_id).removeClass('hidden');
            }
        }

        $(oe_website_sale).on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
            var $ul = $(ev.target).closest('.js_add_cart_variants');
            var $parent = $ul.closest('.js_product');
            var values = [];
            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                values.push(+$(this).val());
            });
            var variant_ids = $ul.data("attribute_value_ids");
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    var  product_id = variant_ids[k][0];
                    update_product_variant_image(this,product_id);
                    break;
                }
            }
           
        });
        $('.js_add_cart_variants', oe_website_sale).each(function () {
           $('input.js_variant_change, select.js_variant_change', this).first().trigger('change');
        });
 
     });

});