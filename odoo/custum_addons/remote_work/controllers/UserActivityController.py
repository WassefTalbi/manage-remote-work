from odoo import http
from odoo.exceptions import AccessDenied
from datetime import datetime
import json
import logging
import os
import google.generativeai as genai


CATEGORY_METADATA = {
    "Entertainment": {
        "icon": "fa-solid fa-film",
        "color": "red"
    },
    "Work": {
        "icon": "fa-solid fa-briefcase",
        "color": "green"
    },
    "Education": {
        "icon": "fa-solid fa-book",
        "color": "blue"
    },
    "Neutral": {
        "icon": "fa-solid fa-question",
        "color": "gray"
    },
    "Unknown": {
        "icon": "fa-solid fa-ban",
        "color": "black"
    },
    "Error": {
        "icon": "fa-solid fa-triangle-exclamation",
        "color": "darkred"
    }
}


_logger = logging.getLogger(__name__)
class UserActivityController(http.Controller):


    def classify_application_gemini(self, app_name):
        model = genai.GenerativeModel('gemini-1.5-flash')
        api_key = http.request.env['ir.config_parameter'].sudo().get_param('google.api_key')
        genai.configure(api_key=api_key)
        prompt = (
            "Classify the following application or YouTube video title into "
            "one of the following categories: [Entertainment, Work, Education, Neutral, Unknown]. "
            "Reply ONLY with the category name."
        )
        input_parts = [
            {"text": f"{prompt}\n\nTitle: {app_name}"}
        ]
        try:
            _logger.info("Sending request to Gemini API...")
            response = model.generate_content(
                contents=input_parts,
                stream=False
            )
            _logger.info("Received response from Gemini API.")
            category_response = response.text.strip()
            for cat in ["Entertainment", "Work", "Education", "Neutral", "Unknown"]:
                if cat.lower() in category_response.lower():
                    return {
                        "category": cat,
                        "icon": CATEGORY_METADATA[cat]["icon"],
                        "color": CATEGORY_METADATA[cat]["color"]
                    }

            return {
                "category": "Unknown",
                "icon": CATEGORY_METADATA["Unknown"]["icon"],
                "color": CATEGORY_METADATA["Unknown"]["color"]
            }
        except Exception as e:
            _logger.exception(f"Error during Gemini classification: {e}")
            return {
                "category": "Error",
                "icon": CATEGORY_METADATA["Error"]["icon"],
                "color": CATEGORY_METADATA["Error"]["color"]
            }

    @http.route("/api/user-activity", methods=["POST"], type="http", auth="none", csrf=False)
    def log_user_activity(self, **post):
        try:
            print("testing in the controller log_user_activity")
            auth_header = http.request.httprequest.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise AccessDenied("Missing of token")
            token_str = auth_header.split('Bearer ')[1]
            token = http.request.env['access.token'].sudo().search([
                ('token', '=', token_str),
                ('is_valid', '=', True)
            ], limit=1)
            if not token:
                raise AccessDenied("Invalid or expired token")
            current_attendance = http.request.env['hr.attendance'].sudo().search([
                ('employee_id.user_id', '=', token.user_id.id),
                ('check_out', '=', False)
            ], limit=1)
            data = json.loads(http.request.httprequest.data)
            print("display the applications used ", data.get('application_usage'))
            if not isinstance(data.get('timestamp'), str):
                raise ValueError("Invalid timestamp format")
            timestamp = datetime.fromisoformat(data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            activity = http.request.env['user.activity.detailed'].sudo().create({
                'user_id': token.user_id.id,
                'attendance_id': current_attendance.id if current_attendance else False,
                'timestamp': timestamp,
                'mouse_clicks': data.get('mouse_clicks'),
                'scrolls': data.get('scrolls'),
                'movements': data.get('movements'),
                'key_presses': data.get('key_presses'),
                'keys': data.get('keys'),

            })
            if data.get('application_usage'):
                apps_to_create = []
                for app in data['application_usage']:
                    classification = self.classify_application_gemini(app.get('name', 'Unknown'))
                    print("into the classification",classification)
                    time_spent = app.get('time_spent', 0)
                    hours, minutes = divmod(time_spent // 60, 60)
                    apps_to_create.append({
                        'name': app.get('name', 'Unknown'),
                        'formatted_time': f"{hours}h {minutes}m" if hours else f"{minutes}m",
                        'category': classification['category'],
                        'icon': classification['icon'],
                         'color': classification['color'],
                        'activity_id': activity.id
                    })
                if apps_to_create:
                    print("apps_to_create")
                    http.request.env['application.usage'].sudo().create(apps_to_create)
            return http.Response(json.dumps({'status': 'success'}), mimetype='application/json')
        except Exception as e:
            _logger.error("API Error: %s", str(e))
            return http.Response(
                json.dumps({'error': str(e)}),
                status=500,
                mimetype='application/json'
            )
    @http.route("/api/system-usage", methods=["POST"], type="http", auth="none", csrf=False)
    def log_system_usage(self, **post):
        print("testing in the controller log_system_usage")
        auth_header = http.request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied("Missing of token")
        token_str = auth_header.split('Bearer ')[1]
        token = http.request.env['access.token'].sudo().search([
            ('token', '=', token_str),
            ('is_valid', '=', True)
        ], limit=1)
        if not token:
            raise AccessDenied("Invalid or expired token")
        current_attendance = http.request.env['hr.attendance'].sudo().search([
            ('employee_id.user_id', '=', token.user_id.id),
            ('check_out', '=', False)
        ], limit=1)
        data = json.loads(http.request.httprequest.data)
        if not isinstance(data.get('timestamp'), str):
            raise ValueError("Invalid timestamp format")
        timestamp = datetime.fromisoformat(data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        http.request.env['system.usage.detailed'].sudo().create({
            'user_id': token.user_id.id,
            'attendance_id': current_attendance.id if current_attendance else False,
            'timestamp': timestamp,
            'cpu_usage': json.dumps(data.get('cpu_usage')),
            'memory_used': data.get('memory_used'),
            'memory_percent': data.get('memory_percent'),
            'disk_usage': data.get('disk_usage'),
            'network_sent': data.get('network_sent'),
            'network_received': data.get('network_received'),
        })
        return print('status success')