from odoo import models, api
from datetime import datetime, timedelta

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    @api.model
    def _register_hook(self):
        """
        Automatically generate planning slots when the module is loaded for the first time.
        """
        super()._register_hook()

        # Check if planning slots have already been generated
        if not self.env['ir.config_parameter'].get_param('remote_work.planning_slots_generated'):
            # Define the start date (today) and end date (e.g., 1 year from today)
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=365)

            # Generate planning slots
            self.generate_planning_slots(start_date, end_date)

            # Mark planning slots as generated
            self.env['ir.config_parameter'].set_param('my_module.planning_slots_generated', True)

    @api.model
    def generate_planning_slots(self, start_date, end_date):
        """
        Generate planning slots for all employees from start_date to end_date.
        Workdays: Sunday to Thursday.
        Holidays: 20 Mars, 9 Avril, 25 Juillet.
        """
        # Define holidays
        holidays = [
            datetime.strptime(f'{datetime.now().year}-03-20', '%Y-%m-%d').date(),  # 20 Mars
            datetime.strptime(f'{datetime.now().year}-04-09', '%Y-%m-%d').date(),  # 9 Avril
            datetime.strptime(f'{datetime.now().year}-07-25', '%Y-%m-%d').date(),  # 25 Juillet
        ]

        # Get all employees
        employees = self.env['hr.employee'].search([])

        # Loop through each day from start_date to end_date
        current_date = start_date
        while current_date <= end_date:
            # Check if the current date is a workday (Sunday to Thursday) and not a holiday
            if current_date.weekday() in [6, 0, 1, 2, 3] and current_date not in holidays:  # Sunday=6, Monday=0, etc.
                for employee in employees:
                    # Create a planning slot for the employee
                    self.create({
                        'employee_id': employee.id,
                        'start_datetime': datetime.combine(current_date, datetime.min.time()),
                        'end_datetime': datetime.combine(current_date, datetime.min.time()) + timedelta(hours=8),
                        'allocated_hours': 8,
                        'state': 'published',
                    })
            # Move to the next day
            current_date += timedelta(days=1)