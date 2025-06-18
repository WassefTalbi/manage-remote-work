from odoo import models, fields

import logging

_logger = logging.getLogger(__name__)


class SiteUsageEntry(models.Model):
    _name = 'site.usage.entry'
    _description = 'Website Usage Entry'

    activity_id = fields.Many2one('user.activity.detailed', string='Activity Record', ondelete='cascade')
    name = fields.Char('Website Name')
    duration = fields.Float('Time Spent (seconds)')
    formatted_time = fields.Char('Formatted Time')
    category = fields.Char('Category')
    icon = fields.Char('Icon')
    color = fields.Char('Color')



