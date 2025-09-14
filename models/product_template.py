# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_cheapest_active_variant_price(self):
        """
        Calculate the cheapest price among all active (non-archived) variants.
        Returns the base price if no active variants exist.
        """
        if not self.product_variant_ids:
            return self.list_price

        # Get all active variants (not archived)
        active_variants = self.product_variant_ids.filtered(lambda v: v.active)

        if not active_variants:
            return self.list_price

        # Calculate the price for each active variant
        cheapest_price = float('inf')

        for variant in active_variants:
            # Get the combination info for this variant
            combination_info = self._get_combination_info(variant.product_template_attribute_value_ids.ids)
            variant_price = combination_info.get('price', 0)

            if variant_price < cheapest_price:
                cheapest_price = variant_price

        # Return the cheapest price, or base price if no valid prices found
        return cheapest_price if cheapest_price != float('inf') else self.list_price
