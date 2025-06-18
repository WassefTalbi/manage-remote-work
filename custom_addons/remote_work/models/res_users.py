from odoo import models, fields

class ResUsers(models.Model):
    _inherit = "res.users"

    tracker_agent_url = fields.Char(string="Tracking Agent URL", default="http://localhost:5001")
