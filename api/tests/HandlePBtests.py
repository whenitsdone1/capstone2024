import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # This needs to be here for imports to work correctly
import handle_PB
from app import startup
from flask import Flask
from logging.handlers import RotatingFileHandler
import logging
import signal
import requests
import subprocess
from unittest.mock import patch, Mock
import unittest

# Note that this testing suite requires both PB and the server/app.py to be running.

class TestPocketBaseManagement(unittest.TestCase):
    def setUp(self):
        # Reset the global variable before each test
        handle_PB.pocketbase_process = None
        # Create a mock Flask app with a logger
        self.app = Flask(__name__)
        logs_path = os.path.abspath('logs.txt')
        if not os.path.exists(logs_path):
            open('logs.txt', 'a').close()
        handler: RotatingFileHandler = RotatingFileHandler(
            'logs.txt', maxBytes=100000, backupCount=1)
        handler.setLevel(logging.INFO)
        formatter: logging.Formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        handler.setFormatter(formatter)
        self.app.logger.addHandler(handler)
        self.app.logger.setLevel(logging.INFO)
        self.handler = logging.StreamHandler(sys.stdout)
        self.handler.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

    def tearDown(self):
        handle_PB.pocketbase_process = None

    @patch('handle_PB.subprocess.run')
    @patch('handle_PB.subprocess.Popen')
    @patch('handle_PB.requests.get')
    def test_ensure_pocketbase_running_starts_pocketbase(self, mock_requests_get, mock_popen, mock_subprocess_run):
        """Test that PocketBase starts when not already running."""
        # Simulate `pgrep` returning non-zero exit code (PocketBase not running)
        mock_subprocess_run.return_value.returncode = 1
        # Simulate starting PocketBase
        mock_pocketbase_process = Mock()
        mock_pocketbase_process.pid = 12345
        mock_popen.return_value = mock_pocketbase_process
        # Simulate PocketBase API becoming available after retries
        responses = [requests.ConnectionError(
        ), requests.ConnectionError(), Mock(status_code=200)]
        mock_requests_get.side_effect = responses
        handle_PB.ensure_pocketbase_running(self.app)
        mock_subprocess_run.assert_called_with(
            ['pgrep', '-f', 'pocketbase'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_popen.assert_called_with(
            ['../pocketbase', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(mock_requests_get.call_count, 3)
        self.app.logger.info(
            "PocketBase process not running, attempting to start it...")
        self.app.logger.info(
            f"PocketBase launched, PID: {mock_pocketbase_process.pid}")
        self.app.logger.info("PocketBase is now running and available.")
        self.app.logger.info(
            "Test: test_ensure_pocketbase_running_starts_pocketbase - Successful")

    @patch('handle_PB.subprocess.run')
    @patch('handle_PB.subprocess.Popen')
    def test_ensure_pocketbase_running_already_running(self, mock_popen, mock_subprocess_run):
        """Test that PocketBase does not start again if already running."""
        # Simulate `pgrep` returning zero exit code (PocketBase is running)
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = b'12345\n'
        # Mock Popen for 'kill -0' command
        mock_popen.return_value = Mock()
        handle_PB.ensure_pocketbase_running(self.app)
        # Assertions
        mock_subprocess_run.assert_called_with(
            ['pgrep', '-f', 'pocketbase'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_popen.assert_called_with(['kill', '-0', '12345'])
        self.app.logger.info("PocketBase instance already running, PID: 12345")
        calls = [args[0] for args, _ in mock_popen.call_args_list]
        self.assertNotIn(['../pocketbase', 'serve'], calls)

    @patch('handle_PB.requests.get')
    @patch('handle_PB.subprocess.Popen')
    @patch('handle_PB.subprocess.run')
    def test_ensure_pocketbase_running_timeout(self, mock_requests_get, mock_popen, mock_subprocess_run):
        """Test that an error is raised if PocketBase fails to start in time."""
        # Simulate `pgrep` returning non-zero exit code
        mock_subprocess_run.return_value.returncode = 1
        # Simulate starting PocketBase
        mock_pocketbase_process = Mock()
        mock_pocketbase_process.pid = 12345
        mock_popen.return_value = mock_pocketbase_process
        # Simulate PocketBase API never becoming available
        mock_requests_get.side_effect = requests.ConnectionError()
        with patch('handle_PB.pocketbase_process', None):
            handle_PB.ensure_pocketbase_running(self.app)
        # Assertions
        assert (mock_requests_get.call_count >= 1)
        self.app.logger.error(
            "PocketBase failed to start within the expected time.")

    def test_terminate_pocketbase(self):
        """Test that PocketBase is terminated when the app shuts down."""
        # Simulate pocketbase_process being set
        handle_PB.pocketbase_process = Mock()
        handle_PB.pocketbase_process.pid = 12345
        handle_PB.terminate_pocketbase(self.app)
        # Assertions
        handle_PB.pocketbase_process.terminate.assert_called_once()
        handle_PB.pocketbase_process.wait.assert_called_once()
        self.app.logger.info(
            f"Terminating PocketBase with PID: {handle_PB.pocketbase_process.pid}")
        self.app.logger.info("PocketBase terminated.")

    @patch('handle_PB.os._exit')
    def test_handle_exit_signals(self, mock_os_exit):
        """Test that exit signals are handled properly."""
        with patch('handle_PB.terminate_pocketbase') as mock_terminate_pocketbase:
            signal_number = signal.SIGINT
            frame = Mock()
            handle_PB.handle_exit_signals(signal_number, frame, self.app)
            # Assertions
            self.app.logger.info(
                f"Received signal {signal_number}. Exiting...")
            mock_terminate_pocketbase(self.app)
            mock_os_exit.assert_called_once_with(0)

    @patch('signal.signal')
    @patch('app.ensure_pocketbase_running')
    def test_startup_registers_signal_handlers(self, mock_ensure_pocketbase_running, mock_signal):
        """Test that signal handlers are registered on startup."""
        # Mock Flask app
        result_app = Mock()
        result_app = startup()
        # Assertions
        calls = [
            ((signal.SIGINT, unittest.mock.ANY),),
            ((signal.SIGTERM, unittest.mock.ANY),)
        ]
        mock_signal.assert_has_calls(calls, any_order=True)
        mock_ensure_pocketbase_running.assert_called_once_with(result_app)


if __name__ == '__main__':
    unittest.main()
