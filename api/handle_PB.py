import requests
import time
import subprocess
from utility_services import get_url
import os
pocketbase_process = None


def ensure_pocketbase_running(app: any, max_retries: int = 10) -> None:
    """
    Ensure PocketBase is running. If not, start it and log the status with PID.
    """
    global pocketbase_process
    try:
        # Check if PocketBase is already running
        result = subprocess.run(
            ['pgrep', '-f', 'pocketbase'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            # PocketBase is running, extract the PID and log it
            pid = result.stdout.decode('utf-8').strip()
            app.logger.info(f"PocketBase instance already running, PID: {pid}")
            pocketbase_process = subprocess.Popen(['kill', '-0', pid])
        else:
            # PocketBase is not running, start it
            app.logger.info(
                "PocketBase process not running, attempting to start it...")
            pocketbase_process = subprocess.Popen(
                ['../pocketbase', 'serve', '--dir', './pb_data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            app.logger.info(
                f"PocketBase launched, PID: {pocketbase_process.pid}")
  # Wait until PocketBase is up and running by polling its API
            for _ in range(max_retries):  # Retry up to 10 times
                try:
                    response = requests.get(f"{get_url()}/api/")
                    if response.status_code == 200:
                        app.logger.info(
                            "PocketBase is now running and available.")
                        break
                except requests.ConnectionError:
                    app.logger.info("PocketBase is still starting up...")
                    time.sleep(10)  # Wait 5 seconds before retrying
            else:
                app.logger.error(
                    "PocketBase failed to start within the expected time.")
                raise RuntimeError("PocketBase did not start in time.")
    except Exception as e:
        app.logger.error(f"Error ensuring PocketBase is running: {e}")


def terminate_pocketbase(app):
    """Terminate the PocketBase process when the app shuts down."""
    global pocketbase_process
    if pocketbase_process is not None:
        app.logger.info(
            f"Terminating PocketBase with PID: {pocketbase_process.pid}")
        for handler in app.logger.handlers:
            handler.flush()
        pocketbase_process.terminate()
        pocketbase_process.wait()  # Ensure it fully terminates
        app.logger.info("PocketBase terminated.")


def handle_exit_signals(signal_number, frame, app):
    """Handle exit signals to ensure PocketBase is terminated."""
    app.logger.info(f"Received signal {signal_number}. Exiting...")
    for handler in app.logger.handlers:
        handler.flush()
    terminate_pocketbase(app)
    for handler in app.logger.handlers:
        handler.flush()
    os._exit(0)
