from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError
class HrBreak(models.Model):
    _name = 'hr.break'
    _description = 'Employee Break'

    attendance_id = fields.Many2one('hr.attendance', string="Attendance", required=True, ondelete='cascade')
    break_start = fields.Datetime(string="Break Start Time", required=True)
    break_end = fields.Datetime(string="Break End Time")
    break_duration = fields.Float(string="Break Duration (minutes)", compute="_compute_break_duration", store=True)

    @api.depends('break_start', 'break_end')
    def _compute_break_duration(self):
        for record in self:
            if record.break_start and record.break_end:
                record.break_duration = (record.break_end - record.break_start).total_seconds() / 60
            else:
                record.break_duration = 0.0

