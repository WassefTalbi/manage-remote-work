from odoo import http
from odoo.exceptions import AccessDenied
from datetime import datetime
import json

class UserActivityController(http.Controller):
    @http.route('/api/test', type='http', auth='none', methods=['POST'], csrf=False)
    def test(self, **post):
        return  print("testing")


    @http.route("/api/user-activity", methods=["POST"], type="http", auth="none", csrf=False)
    def log_user_activity(self, **post):
        print("testing in the controller log_user_activity")
        auth_header = http.request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied("Missing or invalid token")
        token_str = auth_header.split('Bearer ')[1]
        token = http.request.env['access.token'].sudo().search([
            ('token', '=', token_str),
            ('is_valid', '=', True)
        ], limit=1)
        if not token:
            raise AccessDenied("Invalid or expired token")
        data = json.loads(http.request.httprequest.data)
        if not isinstance(data.get('timestamp'), str):
            raise ValueError("Invalid timestamp format")
        timestamp = datetime.fromisoformat(data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        http.request.env['user.activity.detailed'].sudo().create({
            'user_id': token.user_id.id,
            'timestamp': timestamp,
            'mouse_clicks': data.get('mouse_clicks'),
            'scrolls': data.get('scrolls'),
            'movements': data.get('movements'),
            'key_presses': data.get('key_presses'),
            'keys': data.get('keys'),
            'application_usage': json.dumps(data.get('application_usage')),
        })
        return print('status success')

    @http.route("/api/system-usage", methods=["POST"], type="http", auth="none", csrf=False)
    def log_system_usage(self, **post):
        print("testing in the controller log_system_usage")
        auth_header = http.request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied("Missing or invalid token")
        token_str = auth_header.split('Bearer ')[1]
        token = http.request.env['access.token'].sudo().search([
            ('token', '=', token_str),
            ('is_valid', '=', True)
        ], limit=1)
        if not token:
            raise AccessDenied("Invalid or expired token")

        data = json.loads(http.request.httprequest.data)
        if not isinstance(data.get('timestamp'), str):
            raise ValueError("Invalid timestamp format")
        timestamp = datetime.fromisoformat(data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        http.request.env['system.usage.detailed'].sudo().create({
            'user_id': token.user_id.id,
            'timestamp': timestamp,
            'cpu_usage': json.dumps(data.get('cpu_usage')),
            'memory_used': data.get('memory_used'),
            'memory_percent': data.get('memory_percent'),
            'disk_usage': data.get('disk_usage'),
            'network_sent': data.get('network_sent'),
            'network_received': data.get('network_received'),
        })
        return print('status success')