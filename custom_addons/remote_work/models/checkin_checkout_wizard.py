
from odoo import models, fields, api,_
from odoo.exceptions import UserError

from .script_agent import ScriptAgent

import subprocess
import os
import signal
TOKEN_FILE = os.path.expanduser("~/PycharmProjects/ScriptDev/checkin_token.txt")

# def save_token(token):
#     try:
#         with open(TOKEN_FILE, "w") as f:
#             f.write(token)
#         print(f"✅ Token saved to {TOKEN_FILE}")
#     except IOError as e:
#         raise UserError(_("Failed to save token: %s") % e)
class CheckinCheckoutWizard(models.TransientModel):
    _name = 'checkin.checkout.wizard'
    _description = 'Wizard for Employee Check-In/Check-Out'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    check_in = fields.Datetime(string="Check In Time", compute="_compute_check_in" ,readonly=True)
    check_out = fields.Datetime(string="Check Out Time", readonly=True)
    disabled_check_in = fields.Boolean(compute="_compute_disabled_check_in", store=False)
    disabled_check_out = fields.Boolean(compute="_compute_disabled_check_out", store=False)
    is_on_break = fields.Boolean(compute="_compute_is_on_break", store=False)
    actual_check_in = fields.Datetime(string="Actual Check In Time", readonly=True)
    process = None
    SCRIPT_PATH = os.path.expanduser("~/PycharmProjects/ScriptDev/integrated.py")
    VENV_PYTHON = os.path.expanduser("~/PycharmProjects/ScriptDev/.venv/bin/python")

    # def run_script(self, token_str):
    #     try:
    #         script_path = type(self).SCRIPT_PATH
    #         python_path = type(self).VENV_PYTHON
    #
    #         if not os.path.exists(script_path):
    #             raise UserError(_("Script not found at %s") % script_path)
    #         if not os.path.exists(python_path):
    #             raise UserError(_("Python binary not found at %s") % python_path)
    #
    #         save_token(token_str)
    #
    #         process = subprocess.Popen(
    #             [python_path, script_path],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE,
    #             text=True
    #         )
    #         print("✅ Script started with PID:", process.pid)
    #
    #     except Exception as e:
    #         raise UserError(_("Error starting script: %s") % e)
    #
    # def stop_script(self):
    #     try:
    #         script_name = self.SCRIPT_PATH.split('/')[-1]
    #         command = f"ps aux | grep {script_name} | grep -v grep"
    #         process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #         out, _ = process.communicate()
    #
    #         if out:
    #             lines = out.decode().splitlines()
    #             for line in lines:
    #                 pid = int(line.split()[1])
    #                 print(f"Sending SIGINT to PID: {pid}")
    #                 os.kill(pid, signal.SIGINT)
    #
    #                 _, status = os.waitpid(pid, 0)
    #                 print(f"Process {pid} exited with status {status}")
    #
    #     except Exception as e:
    #         print(f"Error stopping script: {str(e)}")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        employee = self.env['hr.employee'].search([], limit=1)
        if employee:
            res.update({
                'employee_id': self.env.user.employee_id.id,
            })
        return res
    @api.depends('employee_id')
    def _compute_check_in(self):
        """ Compute the check-in time based on the employee's attendance """
        for record in self:
            attendance = record._get_attendance_status()
            if attendance:
                record.check_in = attendance.check_in
            else:
                record.check_in = fields.Datetime.now()
    @api.depends('employee_id')
    def _compute_disabled_check_in(self):
        for record in self:
            record.disabled_check_in = bool(record._get_attendance_status())
    @api.depends('employee_id')
    def _compute_disabled_check_out(self):
        for record in self:
            attendance = record._get_attendance_status()
            record.disabled_check_out = not (attendance and not attendance.check_out)
    @api.depends('employee_id')
    def _compute_is_on_break(self):
        for record in self:
            attendance = record._get_attendance_status()
            if attendance:
                active_break = self.env['hr.break'].search([
                    ('attendance_id', '=', attendance.id),
                    ('break_end', '=', False)
                ], limit=1)
                record.is_on_break = bool(active_break)
            else:
                record.is_on_break = False
    def _get_attendance_status(self):
        return self.env['hr.attendance'].search([
            ('employee_id', '=', self.env.user.employee_id.id),
            ('check_out', '=', False)
        ], limit=1)
    def toggle_checkin(self):
        token = self.env['access.token'].create({
            'user_id': self.env.user.id,
        })
        token_str = token.token
        print("token when checkin",token_str)
        #self.run_script(token_str)
        ScriptAgent.checkin(self.env, token_str)
        attendance = self.env['hr.attendance'].create({
            'employee_id': self.env.user.employee_id.id ,
            'check_in': fields.Datetime.now(),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "✅ Check-In Successful",
                'message': "🟢 Tracking script has started.",
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': 'Attendance',
                    'res_model': 'hr.attendance',
                    'view_mode': 'tree',
                    'views': [(self.env.ref('remote_work.hr_attendance_tree_view').id, 'tree')],
                    'target': 'current',
                    'context': {
                        'default_employee_id': self.env.user.employee_id.id,
                    }
                }
            }
        }

    def toggle_checkout(self):
        #self.stop_script()
        ScriptAgent.checkout(self.env)
        attendance = self.env['hr.attendance'].search([
            ('employee_id', '=', self.env.user.employee_id.id),
            ('check_out', '=', False)
        ], limit=1)
        if attendance:
            attendance.write({'check_out': fields.Datetime.now()})

        token = self.env['access.token'].search([
            ('user_id', '=', self.env.user.id),
            ('is_valid', '=', True)
        ], limit=1)
        if token:
            token.is_valid = False

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "⛔ Check-Out Successful",
                'message': "🔴 Tracking script has been stopped.",
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window',
                    'name': 'Attendance',
                    'res_model': 'hr.attendance',
                    'view_mode': 'tree',
                    'views': [(self.env.ref('remote_work.hr_attendance_tree_view').id, 'tree')],
                    'target': 'current',
                    'context': {
                        'default_employee_id': self.env.user.employee_id.id,
                    }
                }
            }
        }




