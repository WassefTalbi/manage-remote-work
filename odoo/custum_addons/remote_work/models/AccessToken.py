from odoo import models, fields, api
import secrets

class AccessToken(models.Model):
    _name = 'access.token'
    _description = 'Access Token for Check-in Session'

    token = fields.Char(required=True, index=True, default=lambda self: secrets.token_urlsafe(32))
    user_id = fields.Many2one('res.users', required=True)
    check_in_time = fields.Datetime(default=fields.Datetime.now)
    is_valid = fields.Boolean(default=True)