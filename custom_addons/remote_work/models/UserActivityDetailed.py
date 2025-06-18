from odoo import models, fields,api
import json
import requests
import logging
_logger = logging.getLogger(__name__)
class UserActivityDetailed(models.Model):
    _name = 'user.activity.detailed'
    _description = 'User Activity Detailed Log'

    user_id = fields.Many2one('res.users', string='User')
    timestamp = fields.Datetime('Timestamp')
    attendance_id = fields.Many2one('hr.attendance', string='Attendance Record',ondelete='cascade')
    app_usage_ids = fields.One2many('app.usage.entry', 'activity_id', string='App Usage')
    site_usage_ids = fields.One2many('site.usage.entry', 'activity_id', string='Site Usage')






