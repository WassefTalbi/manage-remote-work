from odoo import models, fields, api
from odoo.http import request


class RemoteWorkDay(models.Model):
    _name = 'remote.work.day'
    _description = 'Remote Work Day'

    date = fields.Date(string='Date', required=True)
    request_id = fields.Many2one('remote.work.request', string='Remote Work Request')