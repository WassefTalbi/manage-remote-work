from odoo import _
from odoo.exceptions import UserError
import requests
class ScriptAgent:

    @classmethod
    def checkin(cls, env, token_str):
        cls._call("/checkin", env, token_str, method='POST')

    @classmethod
    def pause(cls, env):
        cls._call("/pause", env, method='GET')

    @classmethod
    def resume(cls, env):
        cls._call("/resume", env, method='GET')

    @classmethod
    def checkout(cls, env):
        cls._call("/checkout", env, method='GET')

    @classmethod
    def _call(cls, endpoint, env, token_str=None, method='GET'):
        try:
            url = cls._get_static_tracker_url(env) + endpoint
            if method == 'POST':

                headers = {"Content-Type": "application/json"}
                payload = {"token": token_str}
                response = requests.post(url, json=payload, headers=headers, timeout=3)
            else:

                response = requests.get(url, params={"token": token_str}, timeout=3)

            print("Response Body:", response.text)
            if response.status_code != 200:
                raise UserError(_("Script agent call failed: %s") % response.text)
        except requests.exceptions.RequestException as e:
            raise UserError(_("Could not contact tracking agent: %s") % e)

    @classmethod
    def _get_static_tracker_url(cls, env):
        user = env.user
        #static_tracker_url = user.tracker_agent_url
        static_tracker_url = "http://192.168.38.10:5001"
        if not static_tracker_url:
            raise UserError(_("No tracking agent URL defined for this user."))

        return static_tracker_url
