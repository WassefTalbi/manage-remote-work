from odoo import models, fields, api
import json
import requests
import re


class ActivityReportWizard(models.TransientModel):
    _name = 'activity.report.wizard'
    _description = 'Activity Report Wizard'

    attendance_id = fields.Many2one('hr.attendance', required=True)
    employee_id = fields.Many2one(related='attendance_id.employee_id')
    check_in = fields.Datetime(related='attendance_id.check_in')
    check_out = fields.Datetime(related='attendance_id.check_out')
    user_activities = fields.One2many(
        related='attendance_id.user_activity_ids',
        readonly=True
    )
    system_usage = fields.One2many(
        related='attendance_id.system_usage_ids',
        readonly=True
    )
    processed_apps = fields.Text(
        compute='_compute_processed_apps',
        string='Analyzed Applications'
    )

    def _classify_application(self, app_name):
        """Classify application using Hugging Face API"""
        try:
            response = requests.post(
                'https://api-inference.huggingface.co/models/facebook/bart-large-mnli',
                headers={'Authorization': 'Bearer YOUR_HF_API_KEY'},
                json={
                    "inputs": app_name,
                    "parameters": {
                        "candidate_labels": [
                            "Development", "DevOps", "Cloud",
                            "Database", "BI", "Data Science",
                            "Learning", "Entertainment", "Administration"
                        ]
                    }
                }
            )
            if response.status_code == 200:
                result = response.json()
                return result['labels'][0]
        except Exception:
            return 'Other'

    def _get_category_style(self, category):
        icons = {
            'Development': ('fa-code', '#4CAF50'),
            'DevOps': ('fa-cogs', '#795548'),
            'Cloud': ('fa-cloud', '#2196F3'),
            'Database': ('fa-database', '#9C27B0'),
            'BI': ('fa-chart-bar', '#FF9800'),
            'Data Science': ('fa-brain', '#E91E63'),
            'Learning': ('fa-graduation-cap', '#009688'),
            'Entertainment': ('fa-gamepad', '#FF5722'),
            'Administration': ('fa-server', '#607D8B'),
            'Other': ('fa-question-circle', '#9E9E9E')
        }
        return icons.get(category, ('fa-question-circle', '#9E9E9E'))

    @api.depends('user_activities.application_usage')
    def _compute_processed_apps(self):
        for record in self:
            apps_data = []
            for activity in record.user_activities:
                if activity.application_usage:
                    print("testing")
                    try:
                        app_dict = json.loads(activity.application_usage)
                        for app_name, duration in app_dict.items():
                            # Handle YouTube videos
                            if 'YouTube - ' in app_name:
                                video_title = app_name.split('YouTube - ')[1]
                                app_type = 'video'
                                content_to_analyze = video_title
                            else:
                                app_type = 'application'
                                content_to_analyze = app_name

                            # Get classification
                            category = self._classify_application(content_to_analyze)
                            icon, color = self._get_category_style(category)

                            # Calculate minutes
                            seconds = float(duration.split()[0])
                            minutes = round(seconds / 60, 1)

                            apps_data.append({
                                'name': video_title if app_type == 'video' else app_name,
                                'type': app_type,
                                'category': category,
                                'icon': icon,
                                'color': color,
                                'minutes': minutes
                            })
                    except Exception as e:
                        continue
            record.processed_apps = json.dumps(apps_data)