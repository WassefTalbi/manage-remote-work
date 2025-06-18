import requests
from odoo import _
from odoo.exceptions import UserError

class ScriptAgent:
    LOCAL_TRACKER_URL = "http://localhost:5050"

    @classmethod
    def pause(cls):
        cls._call("/pause")

    @classmethod
    def resume(cls):
        cls._call("/resume")

    @classmethod
    def checkout(cls):
        cls._call("/trigger_checkout")

    @classmethod
    def _call(cls, endpoint):
        try:
            url = f"{cls.LOCAL_TRACKER_URL}{endpoint}"
            resp = requests.post(url, timeout=3)
            if resp.status_code != 200:
                raise UserError(_("Script agent call failed: %s") % resp.text)
        except requests.exceptions.RequestException as e:
            raise UserError(_("Could not contact tracking agent: %s") % e)
