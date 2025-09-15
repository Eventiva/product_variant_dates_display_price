# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.float_utils import float_is_zero


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

        # Local per-call memoization cache for combination info lookups
        ctx = self.env.context
        cache = {}
        pricelist_id = ctx.get('pricelist') or ctx.get('pricelist_id')

        def _get_price_for_ptav_ids(ptav_ids):
            key = (self.id, pricelist_id, tuple(sorted(ptav_ids)))
            if key in cache:
                return cache[key]
            info = self._get_combination_info(ptav_ids)
            price = info.get('price') if isinstance(info, dict) else None
            cache[key] = price
            return price

        # Lazily compute the pricelist-aware base price once
        base_price = None
        def _get_base_price():
            nonlocal base_price
            if base_price is None:
                base_price = _get_price_for_ptav_ids([])
            return base_price

        # If no variants exist at all, use pricelist-aware template price
        if not self.product_variant_ids:
            bp = _get_base_price()
            return bp if bp is not None else self.list_price

        # Only consider website-visible sellable variants (active, sale_ok, website_published)
        sellable_variants = self.product_variant_ids.filtered(
            lambda variant: variant.active and variant.sale_ok and getattr(variant, 'website_published', True)
        )
        if not sellable_variants:
            bp = _get_base_price()
            return bp if bp is not None else self.list_price

        # Compute the cheapest sellable variant price with memoization and normalization
        prices = []
        for variant in sellable_variants:
            price = _get_price_for_ptav_ids(variant.product_template_attribute_value_ids.ids)
            normalized_price = price if price is not None else float('inf')
            # Short-circuit as soon as we hit a zero price using currency precision
            currency = self.currency_id
            if currency:
                precision_digits = getattr(currency, 'decimal_places', None)
                if precision_digits is not None:
                    if float_is_zero(normalized_price, precision_digits=precision_digits):
                        return 0
                else:
                    if float_is_zero(normalized_price, precision_rounding=currency.rounding):
                        return 0
            else:
                # Fallback to 2 decimals if currency is missing from context
                if float_is_zero(normalized_price, precision_digits=2):
                    return 0
            prices.append(normalized_price)

        cheapest_price = min(prices, default=float('inf'))
        if cheapest_price == float('inf'):
            bp = _get_base_price()
            return bp if bp is not None else self.list_price
        return cheapest_price
