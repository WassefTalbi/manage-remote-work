from odoo import http
from odoo.http import request
import json

class ActivityLogger(http.Controller):

    @http.route('/api/user-activity', type='json', auth='user', methods=['POST'])
    def user_activity(self):
        data = request.httprequest.get_json()
        if not data:
            print("No data received")
            return {"error": "No data received"}
        try:
            user = request.env.user
            if not user.employee_id:
                return {"error": "No employee linked to the authenticated user."}
            request.env['user.activity.detailed'].sudo().create({
                'user_id': user.id,
                'timestamp': data.get("timestamp"),
                'mouse_clicks': data.get("mouse_clicks"),
                'scrolls': data.get("scrolls"),
                'movements': data.get("movements"),
                'key_presses': data.get("key_presses"),
                'keys': json.dumps(data.get("keys")),
                'application_usage': json.dumps(data.get("application_usage"))
            })
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/system-usage', type='json', auth='user', methods=['POST'])
    def system_usage(self):
        data = request.httprequest.get_json()
        if not data:
            print("No data received")
            return {"error": "No data received"}

        try:
            user = request.env.user
            if not user.employee_id:
                return {"error": "No employee linked to the authenticated user."}
            request.env['system.usage.detailed'].sudo().create({
                'user_id': user.id,
                'timestamp': data.get("timestamp"),
                'cpu_usage': data.get("cpu_usage"),
                'memory_used': data.get("memory_used"),
                'memory_percent': data.get("memory_percent"),
                'disk_usage': json.dumps(data.get("disk_usage")),
                'network_sent': data.get("network_sent"),
                'network_received': data.get("network_received")
            })
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}