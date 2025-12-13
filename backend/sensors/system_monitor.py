"""
System Monitor Module
-------------------
Monitors system resources (CPU, memory, disk).
"""

import psutil
import time
from typing import Dict, List
from datetime import datetime


class SystemMonitor:
    """System resource monitor."""

    def __init__(self):
        """Initialize system monitor."""
        self.start_time = time.time()

    def get_cpu_info(self) -> Dict[str, any]:
        """
        Get CPU usage information.

        Returns:
            Dictionary with CPU metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)

            # Per-core usage
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)

            # CPU frequency
            try:
                freq = psutil.cpu_freq()
                cpu_freq = {
                    "current": freq.current if freq else 0,
                    "min": freq.min if freq else 0,
                    "max": freq.max if freq else 0,
                }
            except:
                cpu_freq = {"current": 0, "min": 0, "max": 0}

            return {
                "percent": cpu_percent,
                "count_logical": cpu_count_logical,
                "count_physical": cpu_count_physical,
                "per_cpu": per_cpu,
                "frequency": cpu_freq,
                "available": True,
            }
        except Exception as e:
            return {"percent": 0, "available": False, "error": str(e)}

    def get_memory_info(self) -> Dict[str, any]:
        """
        Get memory usage information.

        Returns:
            Dictionary with memory metrics
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "total": mem.total,
                "available_bytes": mem.available,
                "used": mem.used,
                "free": mem.free,
                "percent": mem.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": swap.percent,
                "available": True,
            }
        except Exception as e:
            return {"percent": 0, "available": False, "error": str(e)}

    def get_disk_info(self) -> Dict[str, any]:
        """
        Get disk usage information.

        Returns:
            Dictionary with disk metrics
        """
        try:
            disk = psutil.disk_usage("/")

            # Disk I/O statistics
            try:
                io_counters = psutil.disk_io_counters()
                io_stats = {
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                }
            except:
                io_stats = {}

            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
                "io_stats": io_stats,
                "available": True,
            }
        except Exception as e:
            return {"percent": 0, "available": False, "error": str(e)}

    def get_network_info(self) -> Dict[str, any]:
        """
        Get network usage information.

        Returns:
            Dictionary with network metrics
        """
        try:
            net_io = psutil.net_io_counters()

            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
                "available": True,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def get_process_info(self) -> Dict[str, any]:
        """
        Get current process information.

        Returns:
            Dictionary with process metrics
        """
        try:
            process = psutil.Process()

            return {
                "pid": process.pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_percent": process.memory_percent(),
                "memory_info": process.memory_info()._asdict(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time(),
                "available": True,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def get_uptime(self) -> Dict[str, any]:
        """
        Get system uptime.

        Returns:
            Dictionary with uptime information
        """
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time

            # Process uptime
            process_uptime = time.time() - self.start_time

            return {
                "system_uptime_seconds": uptime_seconds,
                "process_uptime_seconds": process_uptime,
                "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
                "available": True,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def get_comprehensive_reading(self) -> Dict[str, any]:
        """
        Get comprehensive system resource reading.

        Returns:
            Dictionary with all system metrics
        """
        return {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "process": self.get_process_info(),
            "uptime": self.get_uptime(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_summary(self) -> Dict[str, any]:
        """
        Get simplified summary of system resources.

        Returns:
            Dictionary with key metrics
        """
        cpu = self.get_cpu_info()
        memory = self.get_memory_info()
        disk = self.get_disk_info()

        return {
            "cpu_percent": cpu.get("percent", 0),
            "memory_percent": memory.get("percent", 0),
            "disk_percent": disk.get("percent", 0),
            "available": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def monitor_continuous(
        self, duration: float = 10.0, interval: float = 1.0
    ) -> List[Dict[str, any]]:
        """
        Monitor system resources continuously.

        Args:
            duration: Total monitoring duration in seconds
            interval: Sampling interval in seconds

        Returns:
            List of system readings
        """
        measurements = []
        start_time = time.time()

        while time.time() - start_time < duration:
            reading = self.get_summary()
            measurements.append(reading)
            time.sleep(interval)

        return measurements

    def get_average_metrics(self, measurements: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Calculate average from multiple measurements.

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Dictionary with average statistics
        """
        if not measurements:
            return {
                "avg_cpu_percent": 0.0,
                "avg_memory_percent": 0.0,
                "avg_disk_percent": 0.0,
                "samples": 0,
            }

        cpu_values = [m.get("cpu_percent", 0) for m in measurements]
        memory_values = [m.get("memory_percent", 0) for m in measurements]
        disk_values = [m.get("disk_percent", 0) for m in measurements]

        return {
            "avg_cpu_percent": round(sum(cpu_values) / len(cpu_values), 2),
            "avg_memory_percent": round(sum(memory_values) / len(memory_values), 2),
            "avg_disk_percent": round(sum(disk_values) / len(disk_values), 2),
            "max_cpu_percent": round(max(cpu_values), 2),
            "max_memory_percent": round(max(memory_values), 2),
            "samples": len(measurements),
        }


# Convenience functions


def get_system_reading() -> Dict[str, any]:
    """
    Get a single system resource reading.

    Returns:
        System metrics dictionary
    """
    monitor = SystemMonitor()
    return monitor.get_summary()


def get_detailed_system_info() -> Dict[str, any]:
    """
    Get detailed system information.

    Returns:
        Comprehensive system metrics
    """
    monitor = SystemMonitor()
    return monitor.get_comprehensive_reading()


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable format.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"
