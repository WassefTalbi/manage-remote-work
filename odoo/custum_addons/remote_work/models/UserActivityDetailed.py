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
    mouse_clicks = fields.Integer('Mouse Clicks',)
    scrolls = fields.Integer('Scrolls')
    movements = fields.Integer('Mouse Movements')
    key_presses = fields.Integer('Key Presses')
    keys = fields.Text('Keys Pressed')
    attendance_id = fields.Many2one('hr.attendance', string='Attendance Record',ondelete='cascade')
    application_ids = fields.One2many('application.usage', 'activity_id', string='Applications')
    application_summary = fields.Json(string="Application Summary", compute="_compute_application_summary", store=False)

    @api.depends('application_ids')
    def _compute_application_summary(self):
        for record in self:
            apps_data = []
            for app in record.application_ids:
                apps_data.append({
                    'name': app.name,
                    'category': app.category,
                    'icon': app.icon,
                    'color': app.color,
                    'time_spent': app.formatted_time,
                })
            record.application_summary = apps_data




