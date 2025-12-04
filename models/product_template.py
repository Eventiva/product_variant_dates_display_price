# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_cheapest_active_variant_price(self):
        """
        Calculate the cheapest price among all active (non-archived) variants.
        Returns the base price if no active variants exist.
        This method is designed to work in template contexts.
        """
        self.ensure_one()
        
        if not self.product_variant_ids:
            return self.list_price

        # Get all active variants (not archived)
        active_variants = self.product_variant_ids.filtered(lambda v: v.active)

        if not active_variants:
            return self.list_price

        # Simply get the minimum list_price from active variants
        # This avoids complex pricelist calculations that might fail in template context
        variant_prices = active_variants.mapped('list_price')
        variant_prices = [p for p in variant_prices if p > 0]  # Filter out zero/negative prices
        
        if variant_prices:
            return min(variant_prices)
        
        # Fallback to template price
        return self.list_price
