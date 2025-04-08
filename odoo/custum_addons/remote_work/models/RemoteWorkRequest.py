from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date

class RemoteWorkRequest(models.Model):
    _name = 'remote.work.request'
    _description = 'Remote Work Request'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread','mail.activity.mixin']
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,default=lambda self: self.env.user.employee_id)
    request_date = fields.Date(string='Request Date', default=fields.Date.today(), required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('canceled','Canceled'),
        ('expired','Expired')
    ], string='Status',default='pending',group_expand="_read_group_states")

    @api.model
    def _read_group_states(self,stages,domain,order):
        return ['pending', 'approved', 'rejected']
    @api.model
    def create(self, vals):
        today = date.today()
        if vals.get('start_date'):
            start_date = fields.Date.from_string(vals['start_date'])
            if start_date < today:
                raise UserError("Start date cannot be in the past!")

        if vals.get('start_date') and vals.get('end_date'):
            end_date = fields.Date.from_string(vals['end_date'])
            if end_date < start_date:
                raise UserError("End date cannot be before start date!")
            if end_date < today:
                raise UserError("End date cannot be in the past!")

        return super().create(vals)

    def write(self, vals):
        today = date.today()
        for record in self:
            start_date = fields.Date.from_string(vals.get('start_date', record.start_date))
            end_date = fields.Date.from_string(vals.get('end_date', record.end_date))
            if start_date < today:
                raise UserError("Cannot move start date to the past!")
            if end_date < today:
                raise UserError("Cannot move end date to the past!")
            if end_date < start_date:
                raise UserError("End date must be after start date!")

        return super().write(vals)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        today = date.today()
        for record in self:
            if record.start_date < today:
                raise ValidationError("Start date cannot be in the past!")
            if record.end_date < today:
                raise ValidationError("End date cannot be in the past!")
            if record.end_date < record.start_date:
                raise ValidationError("End date must be after start date!")

    def action_approve(self):
        for record in self:
            if record.state == 'pending':
                record.write({'state': 'approved'})

    def action_reject(self):
        for record in self:
            if record.state == 'pending':
                record.write({'state': 'rejected'})



