import subprocess
import os
import signal
from odoo import models, fields, api,_
from odoo.exceptions import UserError
from .script_agent import ScriptAgent
class PauseRepriseWizard(models.TransientModel):
    _name = 'pause.reprise.wizard'
    _description = 'Wizard for Employee Break Management'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    break_start = fields.Datetime(string="Break Start Time", compute="_compute_break_start",readonly=True)
    break_end = fields.Datetime(string="Break End Time", readonly=True)
    total_break_time = fields.Float(string="Total Break Time", compute="_compute_total_break_time", store=True)
    disabled_break = fields.Boolean(compute="_compute_disabled_break", store=False)
    disabled_resume = fields.Boolean(compute="_compute_disabled_resume", store=False)
    has_checked_in = fields.Boolean(compute="_compute_has_checked_in", store=False)
    process = None
    SCRIPT_PATH = os.path.expanduser("~/PycharmProjects/ScriptDev/integrated.py")
    VENV_PYTHON = os.path.expanduser("~/PycharmProjects/ScriptDev/.venv/bin/python")

    def run_script(self):
        try:
            script_path = type(self).SCRIPT_PATH
            python_path = type(self).VENV_PYTHON

            if not os.path.exists(script_path):
                raise UserError(_("Script not found at %s") % script_path)
            if not os.path.exists(python_path):
                raise UserError(_("Python binary not found at %s") % python_path)
            process = subprocess.Popen(
                [python_path, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ Script resumed with PID:", process.pid)
        except Exception as e:
            raise UserError(_("Error resuming script: %s") % e)

    def stop_script(self):
        try:
            script_name = self.SCRIPT_PATH.split('/')[-1]
            command = f"ps aux | grep {script_name} | grep -v grep"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, _ = process.communicate()

            if out:
                lines = out.decode().splitlines()
                for line in lines:
                    pid = int(line.split()[1])
                    print(f"Sending SIGINT to PID: {pid}")
                    os.kill(pid, signal.SIGINT)
                    _, status = os.waitpid(pid, 0)
                    print(f"Process {pid} exited with status {status}")
        except Exception as e:
            print(f"Error stopping script: {str(e)}")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        employee = self.env.user.employee_id
        if employee:
            res.update({
                'employee_id': employee.id,
            })
        return res

    @api.depends('employee_id')
    def _compute_break_start(self):
        """ Compute the break start time based on the employee's active break """
        for record in self:
            attendance = record._get_active_attendance()
            if attendance:
                active_break = record._get_active_break(attendance)
                if active_break:
                    record.break_start = active_break.break_start
                else:
                    record.break_start = fields.Datetime.now()
            else:
                record.break_start = False
    @api.depends('employee_id')
    def _compute_has_checked_in(self):
        """ Check if the employee has checked in """
        for record in self:
            attendance = self._get_active_attendance()
            record.has_checked_in = bool(attendance)
    @api.depends('employee_id')
    def _compute_disabled_break(self):
        """ Disable 'Start Break' if already on a break """
        for record in self:
            active_attendance = record._get_active_attendance()
            active_break = record._get_active_break(active_attendance)
            record.disabled_break = bool(active_break and not active_break.break_end)
    @api.depends('employee_id')
    def _compute_disabled_resume(self):
        """ Disable 'Resume Work' if not on a break """
        for record in self:
            active_attendance = record._get_active_attendance()
            active_break = record._get_active_break(active_attendance)
            record.disabled_resume = not (active_break and not active_break.break_end)
    def _get_active_attendance(self):
        """ Get the current active attendance record """
        return self.env['hr.attendance'].search([
            ('employee_id', '=', self.env.user.employee_id.id),
            ('check_out', '=', False)
        ], limit=1)
    def _get_active_break(self, attendance):
        """ Get the most recent break under the given attendance """
        return self.env['hr.break'].search([
            ('attendance_id', '=', attendance.id),
            ('break_end', '=', False)
        ], order="break_start desc", limit=1)
    @api.depends('employee_id')
    def _compute_total_break_time(self):
        """ Compute total break time from all related breaks """
        for record in self:
            active_attendance = record._get_active_attendance()
            if active_attendance:
                total_breaks = sum(active_attendance.break_ids.mapped('break_duration'))
                record.total_break_time = total_breaks
            else:
                record.total_break_time = 0.0

    def start_break(self):
        attendance = self._get_active_attendance()
        if attendance:
            ScriptAgent.pause(self.env)
            #self.stop_script()
            self.env['hr.break'].create({
                'attendance_id': attendance.id,
                'break_start': fields.Datetime.now()
            })
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "⛔ Break Started",
            "message": "🔕 Tracking paused. Break has started.",
                "type": "success",
                "sticky": False,
                "next": self._reload_wizard(),  # Refresh attendance tree
            }
        }

    def end_break(self):
        attendance = self._get_active_attendance()
        if attendance:
            active_break = self._get_active_break(attendance)
            if active_break and not active_break.break_end:
                break_end_time = fields.Datetime.now()
                break_duration = (break_end_time - active_break.break_start).total_seconds() / 60
                active_break.write({
                    'break_end': break_end_time,
                    'break_duration': break_duration
                })
            ScriptAgent.resume(self.env)
            #self.run_script()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "✅ Work Resumed",
                "message": "🔔 Tracking resumed after break.",
                "type": "success",
                "sticky": False,
                "next": self._reload_wizard(),
            }
        }

    def _reload_wizard(self):
        """ Refresh the wizard after performing a break or resume action """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance',
            'view_mode': 'tree',
            'target': 'current',
            'views': [(self.env.ref('remote_work.hr_attendance_tree_view').id, 'tree')],
            'context': {
                'default_employee_id': self.env.user.employee_id.id,
                'search_default_filter': 1
            }
        }
