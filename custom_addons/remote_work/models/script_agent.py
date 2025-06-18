from odoo import _
from odoo.exceptions import UserError
import requests
class ScriptAgent:

    @classmethod
    def pause(cls, env):
        cls._call("/pause", env)

    @classmethod
    def resume(cls, env):
        cls._call("/resume", env)

    @classmethod
    def checkout(cls, env):
        cls._call("/checkout", env)


    @classmethod
    def _call(cls, endpoint, env):
        try:
            url = cls._get_tracker_url(env) + endpoint
            resp = requests.get(url, timeout=3)
            print("Response Body:", resp.text)
            if resp.status_code != 200:
                raise UserError(_("Script agent call failed: %s") % resp.text)
        except requests.exceptions.RequestException as e:
            raise UserError(_("Could not contact tracking agent: %s") % e)

    @classmethod
    def _get_tracker_url(cls, env):
        user = env.user
        url = user.tracker_agent_url
        if not url:
            raise UserError(_("No tracking agent URL defined for this user."))
        if not url.startswith("http"):
            url = f"http://{url}"
        return url.rstrip("/")
