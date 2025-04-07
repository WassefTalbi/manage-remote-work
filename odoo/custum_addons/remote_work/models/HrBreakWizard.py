from odoo import models, fields

class HrBreakWizard(models.TransientModel):
    _name = "hr.break.wizard"
    _description = "Breaks Wizard"

    attendance_id = fields.Many2one("hr.attendance", string="Attendance", required=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", related="attendance_id.employee_id")
    check_in = fields.Datetime(string="Check In", related="attendance_id.check_in")
    check_out = fields.Datetime(string="Check Out", related="attendance_id.check_out")
    worked_hours = fields.Float(string="Worked Hours", related="attendance_id.worked_hours")
    total_break_time = fields.Float(string="Total Break Time", related="attendance_id.total_break_time")
    break_ids = fields.One2many("hr.break", "attendance_id", string="Breaks", related="attendance_id.break_ids")