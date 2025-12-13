"""
Settings Dialog for CV-Mindcare
-------------------------------
Provides a UI for configuring application settings.
"""

import customtkinter as ctk
from config import get_config


class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog window."""

    def __init__(self, parent, on_save=None):
        """
        Initialize settings dialog.

        Args:
            parent: Parent window
            on_save: Callback function called when settings are saved
        """
        super().__init__(parent)

        self.on_save_callback = on_save
        self.config = get_config()

        # Configure window
        self.title("CV-Mindcare Settings")
        self.geometry("600x500")
        self.resizable(False, False)

        # Make it modal
        self.transient(parent)
        self.grab_set()

        # Create UI
        self._create_widgets()
        self._layout_widgets()
        self._load_current_settings()

        # Center on parent
        self._center_on_parent(parent)

    def _center_on_parent(self, parent):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create all widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Settings", font=ctk.CTkFont(size=20, weight="bold")
        )

        # Tabview for different settings categories
        self.tabview = ctk.CTkTabview(self)
        self.tabview.add("Backend")
        self.tabview.add("Launcher")
        self.tabview.add("Sensors")
        self.tabview.add("UI")

        # === Backend Tab ===
        backend_tab = self.tabview.tab("Backend")

        self.backend_host_label = ctk.CTkLabel(backend_tab, text="Backend Host:", anchor="w")
        self.backend_host_entry = ctk.CTkEntry(backend_tab, placeholder_text="127.0.0.1")

        self.backend_port_label = ctk.CTkLabel(backend_tab, text="Backend Port:", anchor="w")
        self.backend_port_entry = ctk.CTkEntry(backend_tab, placeholder_text="8000")

        self.auto_start_backend_var = ctk.BooleanVar()
        self.auto_start_backend_check = ctk.CTkCheckBox(
            backend_tab, text="Auto-start backend on launch", variable=self.auto_start_backend_var
        )

        # === Launcher Tab ===
        launcher_tab = self.tabview.tab("Launcher")

        self.minimize_to_tray_var = ctk.BooleanVar()
        self.minimize_to_tray_check = ctk.CTkCheckBox(
            launcher_tab,
            text="Minimize to system tray instead of taskbar",
            variable=self.minimize_to_tray_var,
        )

        self.start_minimized_var = ctk.BooleanVar()
        self.start_minimized_check = ctk.CTkCheckBox(
            launcher_tab, text="Start minimized", variable=self.start_minimized_var
        )

        self.check_updates_var = ctk.BooleanVar()
        self.check_updates_check = ctk.CTkCheckBox(
            launcher_tab, text="Check for updates on startup", variable=self.check_updates_var
        )

        # === Sensors Tab ===
        sensors_tab = self.tabview.tab("Sensors")

        self.camera_index_label = ctk.CTkLabel(sensors_tab, text="Camera Index:", anchor="w")
        self.camera_index_entry = ctk.CTkEntry(sensors_tab, placeholder_text="0")

        self.enable_camera_var = ctk.BooleanVar()
        self.enable_camera_check = ctk.CTkCheckBox(
            sensors_tab, text="Enable camera/face detection", variable=self.enable_camera_var
        )

        self.enable_microphone_var = ctk.BooleanVar()
        self.enable_microphone_check = ctk.CTkCheckBox(
            sensors_tab,
            text="Enable microphone/sound analysis",
            variable=self.enable_microphone_var,
        )

        # === UI Tab ===
        ui_tab = self.tabview.tab("UI")

        self.theme_label = ctk.CTkLabel(ui_tab, text="Theme:", anchor="w")
        self.theme_option = ctk.CTkOptionMenu(ui_tab, values=["dark", "light", "system"])

        self.window_width_label = ctk.CTkLabel(ui_tab, text="Window Width:", anchor="w")
        self.window_width_entry = ctk.CTkEntry(ui_tab, placeholder_text="700")

        self.window_height_label = ctk.CTkLabel(ui_tab, text="Window Height:", anchor="w")
        self.window_height_entry = ctk.CTkEntry(ui_tab, placeholder_text="500")

        # Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save",
            command=self._save_settings,
            fg_color="green",
            hover_color="darkgreen",
        )

        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="gray",
            hover_color="darkgray",
        )

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults,
            fg_color="orange",
            hover_color="darkorange",
        )

    def _layout_widgets(self):
        """Layout all widgets."""
        # Title
        self.title_label.pack(pady=15)

        # Tabview
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # Backend tab layout
        self.tabview.tab("Backend")
        self.backend_host_label.pack(anchor="w", padx=20, pady=(15, 5))
        self.backend_host_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.backend_port_label.pack(anchor="w", padx=20, pady=(10, 5))
        self.backend_port_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.auto_start_backend_check.pack(anchor="w", padx=20, pady=10)

        # Launcher tab layout
        self.tabview.tab("Launcher")
        self.minimize_to_tray_check.pack(anchor="w", padx=20, pady=15)
        self.start_minimized_check.pack(anchor="w", padx=20, pady=10)
        self.check_updates_check.pack(anchor="w", padx=20, pady=10)

        # Sensors tab layout
        self.tabview.tab("Sensors")
        self.camera_index_label.pack(anchor="w", padx=20, pady=(15, 5))
        self.camera_index_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.enable_camera_check.pack(anchor="w", padx=20, pady=10)
        self.enable_microphone_check.pack(anchor="w", padx=20, pady=10)

        # UI tab layout
        self.tabview.tab("UI")
        self.theme_label.pack(anchor="w", padx=20, pady=(15, 5))
        self.theme_option.pack(fill="x", padx=20, pady=(0, 15))
        self.window_width_label.pack(anchor="w", padx=20, pady=(10, 5))
        self.window_width_entry.pack(fill="x", padx=20, pady=(0, 10))
        self.window_height_label.pack(anchor="w", padx=20, pady=(10, 5))
        self.window_height_entry.pack(fill="x", padx=20, pady=(0, 10))

        # Buttons
        self.button_frame.pack(fill="x", padx=20, pady=15)
        self.reset_button.pack(side="left", padx=(0, 10))
        self.cancel_button.pack(side="right", padx=(10, 0))
        self.save_button.pack(side="right")

    def _load_current_settings(self):
        """Load current settings from config."""
        # Backend settings
        self.backend_host_entry.insert(0, self.config.get("backend", "host"))
        self.backend_port_entry.insert(0, str(self.config.get("backend", "port")))
        self.auto_start_backend_var.set(self.config.get("backend", "auto_start"))

        # Launcher settings
        self.minimize_to_tray_var.set(self.config.get("launcher", "minimize_to_tray"))
        self.start_minimized_var.set(self.config.get("launcher", "start_minimized"))
        self.check_updates_var.set(self.config.get("launcher", "check_updates"))

        # Sensors settings
        self.camera_index_entry.insert(0, str(self.config.get("sensors", "camera_index")))
        self.enable_camera_var.set(self.config.get("sensors", "enable_camera"))
        self.enable_microphone_var.set(self.config.get("sensors", "enable_microphone"))

        # UI settings
        self.theme_option.set(self.config.get("ui", "theme"))
        self.window_width_entry.insert(0, str(self.config.get("ui", "window_width")))
        self.window_height_entry.insert(0, str(self.config.get("ui", "window_height")))

    def _save_settings(self):
        """Save settings to config."""
        try:
            # Backend settings
            self.config.set("backend", "host", self.backend_host_entry.get())
            self.config.set("backend", "port", int(self.backend_port_entry.get()))
            self.config.set("backend", "auto_start", self.auto_start_backend_var.get())

            # Launcher settings
            self.config.set("launcher", "minimize_to_tray", self.minimize_to_tray_var.get())
            self.config.set("launcher", "start_minimized", self.start_minimized_var.get())
            self.config.set("launcher", "check_updates", self.check_updates_var.get())

            # Sensors settings
            self.config.set("sensors", "camera_index", int(self.camera_index_entry.get()))
            self.config.set("sensors", "enable_camera", self.enable_camera_var.get())
            self.config.set("sensors", "enable_microphone", self.enable_microphone_var.get())

            # UI settings
            self.config.set("ui", "theme", self.theme_option.get())
            self.config.set("ui", "window_width", int(self.window_width_entry.get()))
            self.config.set("ui", "window_height", int(self.window_height_entry.get()))

            # Save to file
            self.config.save()

            # Call callback
            if self.on_save_callback:
                self.on_save_callback()

            # Close dialog
            self.destroy()

        except ValueError as e:
            # Show error dialog for invalid input
            error_dialog = ctk.CTkToplevel(self)
            error_dialog.title("Invalid Input")
            error_dialog.geometry("300x150")

            error_label = ctk.CTkLabel(
                error_dialog, text=f"Invalid input:\n{str(e)}", wraplength=250
            )
            error_label.pack(pady=20)

            ok_button = ctk.CTkButton(error_dialog, text="OK", command=error_dialog.destroy)
            ok_button.pack(pady=10)

            error_dialog.transient(self)
            error_dialog.grab_set()

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        # Confirm with user
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Confirm Reset")
        confirm_dialog.geometry("350x150")

        confirm_label = ctk.CTkLabel(
            confirm_dialog,
            text="Are you sure you want to reset\nall settings to defaults?",
            font=ctk.CTkFont(size=14),
        )
        confirm_label.pack(pady=20)

        def do_reset():
            self.config.reset_to_defaults()
            confirm_dialog.destroy()
            self.destroy()
            if self.on_save_callback:
                self.on_save_callback()

        button_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        yes_button = ctk.CTkButton(
            button_frame,
            text="Yes",
            command=do_reset,
            fg_color="red",
            hover_color="darkred",
            width=100,
        )
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(
            button_frame, text="No", command=confirm_dialog.destroy, width=100
        )
        no_button.pack(side="left", padx=10)

        confirm_dialog.transient(self)
        confirm_dialog.grab_set()


def show_settings_dialog(parent, on_save=None):
    """
    Show the settings dialog.

    Args:
        parent: Parent window
        on_save: Callback when settings are saved
    """
    dialog = SettingsDialog(parent, on_save)
    return dialog
