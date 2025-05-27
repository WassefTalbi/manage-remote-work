from odoo import models, fields, api
from odoo.http import request
from odoo import http, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    worked_hours = fields.Float(string="Worked Hours", compute="_compute_worked_hours", store=True)
    worked_hours_display = fields.Char(string="Worked Hours ", compute="_compute_worked_hours", store=True)
    break_ids = fields.One2many("hr.break", "attendance_id", string="Breaks")
    total_break_time = fields.Float(string="Total Break Time (minutes)", compute="_compute_total_break_time", store=True)
    is_under_8_hours = fields.Boolean(string="is_under_8_hours ",compute="_compute_is_under_8_hours", store=False)
    user_activity_ids = fields.One2many('user.activity.detailed', 'attendance_id', string='User Activities')
    system_usage_ids = fields.One2many('system.usage.detailed', 'attendance_id', string='System Usage')

    @api.depends('break_ids.break_duration')
    def _compute_total_break_time(self):
        for record in self:
            record.total_break_time = sum(record.break_ids.mapped('break_duration'))

    @api.depends('check_in', 'check_out', 'total_break_time')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                total_seconds = delta.total_seconds()
                total_break_seconds = attendance.total_break_time * 60
                worked_seconds = total_seconds - total_break_seconds
                attendance.worked_hours = worked_seconds / 3600
                hours = int(worked_seconds // 3600)
                minutes = int((worked_seconds % 3600) // 60)
                attendance.worked_hours_display = f"{hours} hours and {minutes} minutes"
            else:
                attendance.worked_hours = 0
                attendance.worked_hours_display = "0 hours and 0 minutes"

    def action_view_attendance_details(self):
        return {
            'name': 'Attendance Details',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.break.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_attendance_id': self.id},
        }

    def action_consulte_activities(self):
        return {
            'name': 'Activity Report',
            'type': 'ir.actions.act_window',
            'res_model': 'activity.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'views': [(self.env.ref('remote_work.view_activity_report_wizard_form').id, 'form')],
            'context': {
                'default_attendance_id': self.id,
            }
        }



    @api.depends('worked_hours')
    def _compute_is_under_8_hours(self):
        for attendance in self:

            if attendance.worked_hours < 8:
                attendance.is_under_8_hours = True
            else:
                attendance.is_under_8_hours = False

    @api.depends('worked_hours')
    def _compute_overtime_hours(self):
        for attendance in self:
            if attendance.worked_hours > 8:
                attendance.overtime_hours = attendance.worked_hours - 8
            else:
                attendance.overtime_hours = 0

