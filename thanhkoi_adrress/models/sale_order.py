# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vn_address = fields.Char(string="Address")
    phone = fields.Char(related="partner_id.phone")



