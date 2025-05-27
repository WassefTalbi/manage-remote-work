import subprocess
import json
import os
import signal
class ScriptRunner:
    def __init__(self, script_path, venv_path):
        self.script_path = script_path
        self.venv_path = venv_path

    def _run_script(self):
        try:
            if not os.path.exists(self.SCRIPT_PATH):
                return {"error": f"Script not found: {self.SCRIPT_PATH}"}

            if not os.path.exists(self.VENV_PATH):
                return {"error": f"Virtual environment not found: {self.VENV_PATH}"}

            activate_venv = f"source {self.VENV_PATH}/bin/activate"
            run_script = f"python {self.SCRIPT_PATH}"

            # Run the script inside a new shell with the venv activated
            process = subprocess.Popen(
                f"{activate_venv} && {run_script}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable="/bin/bash"
            )

            output, error = process.communicate()

            if process.returncode != 0:
                return {"error": error.decode().strip()}

            return json.loads(output.decode().strip()) if output else {}

        except json.JSONDecodeError:
            return {"error": "Invalid JSON output from script"}
        except Exception as e:
            return {"error": str(e)}

    def stop_script(self):
        """
        Stop the running script by terminating the process and deactivating the venv.
        """
        if self.process:
            self.process.send_signal(signal.SIGINT)
            self.process.wait()
            print("Script stopped.")

            activate_venv = f"deactivate"


            # Run the script inside a new shell with the venv activated
            process = subprocess.Popen(
                f"{activate_venv} ",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                executable="/bin/bash"
            )
            print("Please deactivate the virtual environment manually by typing 'deactivate'.")