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
    app_usage_ids = fields.One2many(
        'app.usage.entry',
        compute='_compute_applications',
        string='Applications Used',
        store=False
    )
    site_usage_ids = fields.One2many(
        'site.usage.entry',
        compute='_compute_sites',
        string='Websites Visited',
        store=False
    )

    @api.depends('attendance_id')
    def _compute_applications(self):
        for wizard in self:
            activity = self.env['user.activity.detailed'].search([
                ('attendance_id', '=', wizard.attendance_id.id)
            ])
            wizard.app_usage_ids = activity.app_usage_ids

    @api.depends('attendance_id')
    def _compute_sites(self):
        for wizard in self:
            activity = self.env['user.activity.detailed'].search([
                ('attendance_id', '=', wizard.attendance_id.id)
            ])
            wizard.site_usage_ids = activity.site_usage_ids









