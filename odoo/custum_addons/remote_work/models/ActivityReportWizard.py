from odoo import models, fields, api
import json
import requests



class ActivityReportWizard(models.TransientModel):
    _name = 'activity.report.wizard'
    _description = 'Activity Report Wizard'

    attendance_id = fields.Many2one('hr.attendance', required=True)
    employee_id = fields.Many2one(related='attendance_id.employee_id',)
    check_in = fields.Datetime(related='attendance_id.check_in')
    check_out = fields.Datetime(related='attendance_id.check_out')
    user_activities = fields.One2many(
        related='attendance_id.user_activity_ids',
        readonly=True,
    )
    system_usage = fields.One2many(
        related='attendance_id.system_usage_ids',
        readonly=True,
    )










