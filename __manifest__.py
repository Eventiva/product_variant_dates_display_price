# -*- coding: utf-8 -*-
{
    'name': 'Product Variant Dates Display Price',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Display calculated variant price in badges instead of price adjustments',
    'description': """
Product Variant Dates Display Price
===================================

This module modifies the display of price badges on product pages to show the
calculated variant price instead of the price adjustment amount.

Features:
---------
* Shows calculated variant price in badges (e.g., £200 instead of -£400)
* Maintains all existing price calculations
* Only changes the display value in badges
* Works with product variant sale dates functionality

Technical Details:
------------------
* Overrides website sale templates to modify badge display
* Calculates variant price from base price + price adjustments
* Preserves all existing pricing logic and calculations
    """,
    'author': 'Eventiva',
    'website': 'www.eventiva.com',
    'depends': [
        'product_variant_dates',
        'website_sale',
    ],
    'data': [
        'views/website_sale_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'Other proprietary',
}
