import subprocess
import os
import signal
from odoo import models, fields, api
from datetime import datetime

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
    SCRIPT_PATH = os.path.expanduser("~/PycharmProjects/ScriptDev/TrackUserSystemApplications.py")
    VENV_PATH = os.path.expanduser("~/PycharmProjects/ScriptDev/.venv/bin/activate")
    def run_script(self):
        try:
            if not os.path.exists(self.SCRIPT_PATH):

                return {"error": f"Script not found: {self.SCRIPT_PATH}"}

            if not os.path.exists(self.VENV_PATH):

                return {"error": f"Virtual environment not found: {self.VENV_PATH}"}

            print("start run the script ..")
            command = f"source {self.VENV_PATH} && python {self.SCRIPT_PATH}"
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable="/bin/bash"
            )
            print(" script running ...")
        except Exception as e:
            print(f"Error running script: {str(e)}")
            return {"error": str(e)}
    def stop_script(self):
        """
        Stop the running script by terminating the process using its PID.
        """

        try:

            command = f"ps aux | grep {self.SCRIPT_PATH.split('/')[-1]} | grep -v grep"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()

            if out:

                pid = int(out.split()[1])
                os.kill(pid, signal.SIGTERM)


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
        """ Start a new Break (creates hr.break record) """
        attendance = self._get_active_attendance()
        if attendance:
            self.stop_script()
            self.env['hr.break'].create({
                'attendance_id': attendance.id,
                'break_start': fields.Datetime.now()
            })
        return self._reload_wizard()
    def end_break(self):
        """ Resume Work (Ends the most recent break) """
        attendance = self._get_active_attendance()
        if attendance:
            self.run_script()
            active_break = self._get_active_break(attendance)
            if active_break and not active_break.break_end:
                break_end_time = fields.Datetime.now()
                break_duration = (break_end_time - active_break.break_start).total_seconds() / 60
                active_break.write({
                    'break_end': break_end_time,
                    'break_duration': break_duration
                })
        return self._reload_wizard()
    def _reload_wizard(self):
        """ Refresh the wizard after performing a break or resume action """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance',
            'view_mode': 'tree',
            'target': 'current',
            'xml': [(self.env.ref('remote_work.hr_attendance_tree_view').id, 'tree')],
            'context': {
                'default_employee_id': self.env.user.employee_id.id,
                'search_default_filter': 1
            }
        }
