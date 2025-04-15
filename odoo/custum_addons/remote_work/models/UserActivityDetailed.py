from odoo import models, fields

class UserActivityDetailed(models.Model):
    _name = 'user.activity.detailed'
    _description = 'User Activity Detailed Log'

    user_id = fields.Many2one('res.users', string='User')
    timestamp = fields.Datetime('Timestamp')
    mouse_clicks = fields.Integer('Mouse Clicks')
    scrolls = fields.Integer('Scrolls')
    movements = fields.Integer('Mouse Movements')
    key_presses = fields.Integer('Key Presses')
    keys = fields.Text('Keys Pressed')
    application_usage = fields.Text('Application Usage')
    attendance_id = fields.Many2one('hr.attendance', string='Attendance Record')