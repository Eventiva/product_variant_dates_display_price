# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_cheapest_active_variant_price(self):
        """
        Return the minimal website price among active (non-archived) variants
        according to the current pricelist context. Falls back to the template
        list price when there are no active variants or no computed prices.
        """
        self.ensure_one()

        if not self.product_variant_ids:
            return self.list_price

        active_variants = self.product_variant_ids.filtered(lambda variant: variant.active)
        if not active_variants:
            return self.list_price

        cheapest_price = None
        for variant in active_variants:
            combination_info = self._get_combination_info(variant.product_template_attribute_value_ids.ids)
            variant_price = combination_info.get('price') or 0.0

            if cheapest_price is None or variant_price < cheapest_price:
                cheapest_price = variant_price

        return cheapest_price if cheapest_price is not None else self.list_price
