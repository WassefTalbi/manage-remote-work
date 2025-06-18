from odoo import http
from odoo.http import request
import requests

LOCAL_TRACKER_URL = "http://localhost:5001"

class TrackerController(http.Controller):

    @http.route('/track/pause', type='json', auth='user')
    def pause_tracking(self):
        try:
            requests.post(f"{LOCAL_TRACKER_URL}/start_pause")
            return {"status": "paused"}
        except Exception as e:
            return {"error": str(e)}

    @http.route('/track/resume', type='json', auth='user')
    def resume_tracking(self):
        try:
            requests.post(f"{LOCAL_TRACKER_URL}/end_break")
            return {"status": "resumed"}
        except Exception as e:
            return {"error": str(e)}

    @http.route('/track/checkout', type='json', auth='user')
    def checkout(self):
        try:
            requests.post(f"{LOCAL_TRACKER_URL}/checkout")
            return {"status": "checkout_sent"}
        except Exception as e:
            return {"error": str(e)}
