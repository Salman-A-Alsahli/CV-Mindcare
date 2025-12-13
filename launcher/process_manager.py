"""
Process Manager for CV-Mindcare Launcher
---------------------------------------
Manages backend server lifecycle and browser integration.
"""

import subprocess
import time
import webbrowser
import requests
from pathlib import Path
from typing import Optional, Callable
import sys
from config import get_config


class ProcessManager:
    """Manages backend process lifecycle."""

    def __init__(self, backend_dir: Optional[Path] = None):
        """
        Initialize process manager.

        Args:
            backend_dir: Path to backend directory (defaults to ../backend)
        """
        if backend_dir is None:
            # Assume launcher is in launcher/ and backend is in backend/
            self.backend_dir = Path(__file__).parent.parent / "backend"
        else:
            self.backend_dir = Path(backend_dir)

        self.process: Optional[subprocess.Popen] = None

        # Get backend URL from config
        self.config = get_config()
        self.backend_url = self.config.get_backend_url()
        self.health_endpoint = f"{self.backend_url}/"

    def start_backend(self, log_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Start the backend server process.

        Args:
            log_callback: Optional callback function for log messages

        Returns:
            True if backend started successfully, False otherwise
        """
        if self.is_backend_running():
            if log_callback:
                log_callback("Backend is already running.")
            return True

        try:
            # Find Python executable
            python_exe = sys.executable

            # Get backend configuration
            backend_host = self.config.get("backend", "host")
            backend_port = self.config.get_backend_port()

            # Build command
            cmd = [
                python_exe,
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                backend_host,
                "--port",
                str(backend_port),
            ]

            if log_callback:
                log_callback(f"Starting backend: {' '.join(cmd)}")

            # Start process
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Wait for backend to be ready
            if log_callback:
                log_callback("Waiting for backend to start...")

            for attempt in range(30):  # 30 seconds timeout
                if self.is_backend_running():
                    if log_callback:
                        log_callback("✓ Backend started successfully!")
                    return True
                time.sleep(1)

            if log_callback:
                log_callback("✗ Backend failed to start within timeout.")
            return False

        except Exception as e:
            if log_callback:
                log_callback(f"✗ Error starting backend: {e}")
            return False

    def stop_backend(self, log_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Stop the backend server process.

        Args:
            log_callback: Optional callback function for log messages

        Returns:
            True if backend stopped successfully
        """
        if self.process is None:
            if log_callback:
                log_callback("No backend process to stop.")
            return True

        try:
            if log_callback:
                log_callback("Stopping backend...")

            self.process.terminate()

            # Wait for process to terminate
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if log_callback:
                    log_callback("Backend did not stop gracefully, forcing...")
                self.process.kill()
                self.process.wait()

            self.process = None

            if log_callback:
                log_callback("✓ Backend stopped.")
            return True

        except Exception as e:
            if log_callback:
                log_callback(f"✗ Error stopping backend: {e}")
            return False

    def is_backend_running(self) -> bool:
        """
        Check if backend is running and responding.

        Returns:
            True if backend is healthy, False otherwise
        """
        try:
            response = requests.get(self.health_endpoint, timeout=2)
            return response.status_code == 200
        except:
            return False

    def get_backend_logs(self) -> tuple[str, str]:
        """
        Get stdout and stderr from backend process.

        Returns:
            Tuple of (stdout, stderr) strings
        """
        if self.process is None:
            return ("", "")

        # Non-blocking read
        stdout_lines = []
        stderr_lines = []

        try:
            # Read available stdout
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                stdout_lines.append(line)

            # Read available stderr
            while True:
                line = self.process.stderr.readline()
                if not line:
                    break
                stderr_lines.append(line)
        except:
            pass

        return ("".join(stdout_lines), "".join(stderr_lines))

    def open_dashboard(self, log_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Open the web dashboard in default browser.

        Args:
            log_callback: Optional callback function for log messages

        Returns:
            True if browser opened successfully
        """
        if not self.is_backend_running():
            if log_callback:
                log_callback("✗ Cannot open dashboard: backend is not running.")
            return False

        try:
            if log_callback:
                log_callback(f"Opening dashboard at {self.backend_url}...")

            # Open in default browser
            webbrowser.open(self.backend_url)

            if log_callback:
                log_callback("✓ Dashboard opened in browser.")
            return True

        except Exception as e:
            if log_callback:
                log_callback(f"✗ Error opening browser: {e}")
            return False

    def cleanup(self):
        """Clean up resources and stop backend if running."""
        self.stop_backend()


# Convenience functions for use in launcher


def start_system(log_callback: Optional[Callable[[str], None]] = None) -> ProcessManager:
    """
    Start the complete CV-Mindcare system.

    Args:
        log_callback: Optional callback for log messages

    Returns:
        ProcessManager instance
    """
    pm = ProcessManager()

    if pm.start_backend(log_callback):
        time.sleep(2)  # Give backend a moment to fully initialize
        pm.open_dashboard(log_callback)

    return pm


def stop_system(pm: ProcessManager, log_callback: Optional[Callable[[str], None]] = None):
    """
    Stop the CV-Mindcare system.

    Args:
        pm: ProcessManager instance
        log_callback: Optional callback for log messages
    """
    pm.stop_backend(log_callback)
