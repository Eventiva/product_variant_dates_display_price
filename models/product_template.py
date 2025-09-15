# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_cheapest_active_variant_price(self):
        """
        Return the minimal website price among active (non-archived) variants
        according to the current pricelist context. Falls back to the template
        combination price when there are no sellable variants or no computed
        variant prices, and finally to list price if no pricelist-aware price
        is available.
        """
        self.ensure_one()

        # Per-request/pricelist memoization cache for combination info lookups
        ctx = self.env.context
        cache = ctx.setdefault('_cheapest_variant_cache', {})
        pricelist_id = ctx.get('pricelist') or ctx.get('pricelist_id')

        def _get_price_for_ptav_ids(ptav_ids):
            key = (self.id, pricelist_id, tuple(sorted(ptav_ids)))
            if key in cache:
                return cache[key]
            info = self._get_combination_info(ptav_ids)
            price = info.get('price') if isinstance(info, dict) else None
            cache[key] = price
            return price

        # If no variants exist at all, use pricelist-aware template price
        if not self.product_variant_ids:
            base_price = _get_price_for_ptav_ids([])
            return base_price if base_price is not None else self.list_price

        # Only consider sellable variants for website price (active and sale_ok)
        sellable_variants = self.product_variant_ids.filtered(lambda variant: variant.active and variant.sale_ok)
        if not sellable_variants:
            base_price = _get_price_for_ptav_ids([])
            return base_price if base_price is not None else self.list_price

        # Compute the cheapest sellable variant price with memoization and normalization
        prices = []
        for variant in sellable_variants:
            price = _get_price_for_ptav_ids(variant.product_template_attribute_value_ids.ids)
            normalized_price = price if price is not None else float('inf')
            # Short-circuit as soon as we hit a zero price
            if normalized_price == 0:
                return 0
            prices.append(normalized_price)

        cheapest_price = min(prices, default=float('inf'))
        if cheapest_price == float('inf'):
            base_price = _get_price_for_ptav_ids([])
            return base_price if base_price is not None else self.list_price
        return cheapest_price
