from odoo import models, fields

class SystemUsageDetailed(models.Model):
    _name = 'system.usage.detailed'
    _description = 'System Usage Detailed Log'

    user_id = fields.Many2one('res.users', string='User')
    timestamp = fields.Datetime('Timestamp')
    cpu_usage = fields.Text('CPU Usage')
    memory_used = fields.Char('Memory Used')
    memory_percent = fields.Float('Memory Percent')
    disk_usage = fields.Text('Disk Usage')
    network_sent = fields.Char('Network Sent')
    network_received = fields.Char('Network Received')