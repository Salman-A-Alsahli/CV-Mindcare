"""
System Check Module
-----------------
Performs system requirement checks for CV-Mindcare.
"""

import os
import shutil
import psutil
import cv2
import sounddevice as sd
from typing import Dict, Tuple


class SystemRequirements:
    """Defines minimum system requirements."""

    MIN_CPU_CORES = 2
    MIN_RAM_GB = 4
    MIN_DISK_SPACE_GB = 1
    REQUIRED_PACKAGES = [
        "customtkinter",
        "opencv-python",
        "fastapi",
        "uvicorn",
        "sounddevice",
        "numpy",
        "sqlalchemy",
    ]


class SystemChecker:
    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}

    def check_cpu(self) -> Tuple[bool, str]:
        """Check CPU cores."""
        cpu_count = psutil.cpu_count(logical=False)
        status = cpu_count >= SystemRequirements.MIN_CPU_CORES
        message = f"CPU Cores: {cpu_count} {'(OK)' if status else f'(Need {SystemRequirements.MIN_CPU_CORES}+'}"
        return status, message

    def check_ram(self) -> Tuple[bool, str]:
        """Check RAM."""
        ram_gb = psutil.virtual_memory().total / (1024**3)
        status = ram_gb >= SystemRequirements.MIN_RAM_GB
        message = f"RAM: {ram_gb:.1f}GB {'(OK)' if status else f'(Need {SystemRequirements.MIN_RAM_GB}GB+)'}"
        return status, message

    def check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space."""
        disk = os.path.abspath(os.sep)
        free_gb = shutil.disk_usage(disk).free / (1024**3)
        status = free_gb >= SystemRequirements.MIN_DISK_SPACE_GB
        message = f"Disk Space: {free_gb:.1f}GB free {'(OK)' if status else f'(Need {SystemRequirements.MIN_DISK_SPACE_GB}GB+)'}"
        return status, message

    def check_camera(self) -> Tuple[bool, str]:
        """Check camera availability."""
        try:
            cap = cv2.VideoCapture(0)
            status = cap.isOpened()
            cap.release()
            message = f"Camera: {'Available (OK)' if status else 'Not Found'}"
        except Exception as e:
            status = False
            message = f"Camera: Error ({str(e)})"
        return status, message

    def check_microphone(self) -> Tuple[bool, str]:
        """Check microphone availability."""
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d["max_input_channels"] > 0]
            status = len(input_devices) > 0
            message = f"Microphone: {'Available (OK)' if status else 'Not Found'}"
        except Exception as e:
            status = False
            message = f"Microphone: Error ({str(e)})"
        return status, message

    def check_packages(self) -> Tuple[bool, str]:
        """Check required Python packages."""
        missing = []
        for package in SystemRequirements.REQUIRED_PACKAGES:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)

        status = len(missing) == 0
        message = (
            f"Packages: {'All installed (OK)' if status else f'Missing: {", ".join(missing)}'}"
        )
        return status, message

    def run_all_checks(self) -> Dict[str, Tuple[bool, str]]:
        """Run all system checks."""
        self.results = {
            "cpu": self.check_cpu(),
            "ram": self.check_ram(),
            "disk": self.check_disk_space(),
            "camera": self.check_camera(),
            "microphone": self.check_microphone(),
            "packages": self.check_packages(),
        }
        return self.results

    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return all(result[0] for result in self.results.values())

    def get_summary(self) -> str:
        """Get a summary of all check results."""
        if not self.results:
            return "No checks performed yet."

        summary = []
        for check_name, (status, message) in self.results.items():
            summary.append(f"✓ {message}" if status else f"✗ {message}")
        return "\n".join(summary)
