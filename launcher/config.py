"""
Configuration Manager for CV-Mindcare
------------------------------------
Manages application settings and preferences.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Application configuration manager."""

    # Default configuration
    DEFAULT_CONFIG = {
        "backend": {"host": "127.0.0.1", "port": 8000, "auto_start": True},
        "launcher": {"minimize_to_tray": True, "start_minimized": False, "check_updates": True},
        "sensors": {
            "camera_index": 0,
            "microphone_index": None,
            "enable_camera": True,
            "enable_microphone": True,
            "enable_system_monitor": True,
        },
        "ui": {"theme": "dark", "window_width": 700, "window_height": 500},
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config file (defaults to user's home directory)
        """
        if config_path is None:
            # Store config in user's home directory
            home = Path.home()
            config_dir = home / ".cvmindcare"
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_with_defaults(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save()
            return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, loaded_config: Dict) -> Dict:
        """Merge loaded config with defaults to ensure all keys exist."""
        merged = self.DEFAULT_CONFIG.copy()

        for section, values in loaded_config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values

        return merged

    def save(self) -> bool:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            section: Configuration section (e.g., 'backend', 'launcher')
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> bool:
        """
        Set a configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set

        Returns:
            True if saved successfully
        """
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        return self.save()

    def get_backend_url(self) -> str:
        """Get the full backend URL."""
        host = self.get("backend", "host", "127.0.0.1")
        port = self.get("backend", "port", 8000)
        return f"http://{host}:{port}"

    def get_backend_port(self) -> int:
        """Get backend port."""
        return self.get("backend", "port", 8000)

    def set_backend_port(self, port: int) -> bool:
        """Set backend port."""
        if 1024 <= port <= 65535:
            return self.set("backend", "port", port)
        return False

    def should_auto_start_backend(self) -> bool:
        """Check if backend should auto-start."""
        return self.get("backend", "auto_start", True)

    def should_minimize_to_tray(self) -> bool:
        """Check if launcher should minimize to tray."""
        return self.get("launcher", "minimize_to_tray", True)

    def should_check_updates(self) -> bool:
        """Check if auto-update checking is enabled."""
        return self.get("launcher", "check_updates", True)

    def get_camera_index(self) -> int:
        """Get camera device index."""
        return self.get("sensors", "camera_index", 0)

    def get_theme(self) -> str:
        """Get UI theme."""
        return self.get("ui", "theme", "dark")

    def get_window_size(self) -> tuple:
        """Get window size as (width, height)."""
        width = self.get("ui", "window_width", 700)
        height = self.get("ui", "window_height", 500)
        return (width, height)

    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save()

    def export_config(self, path: Path) -> bool:
        """Export configuration to a file."""
        try:
            with open(path, "w") as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False

    def import_config(self, path: Path) -> bool:
        """Import configuration from a file."""
        try:
            with open(path, "r") as f:
                loaded = json.load(f)
            self.config = self._merge_with_defaults(loaded)
            return self.save()
        except:
            return False


# Global config instance
_config_instance = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
