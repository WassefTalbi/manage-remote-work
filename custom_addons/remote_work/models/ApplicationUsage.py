from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ApplicationUsage(models.Model):
    _name = 'application.usage'
    _description = 'Classified Application Usage'

    name = fields.Char(string='Application Name', required=True)
    category = fields.Char(string='Category')
    icon = fields.Char(string='Icon')
    color = fields.Char(string='Color Code')
    formatted_time = fields.Char(string='Usage Duration')
    activity_id = fields.Many2one('user.activity.detailed', string='Activity',ondelete='cascade')



