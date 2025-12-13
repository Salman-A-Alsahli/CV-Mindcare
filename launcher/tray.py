"""
System Tray Icon for CV-Mindcare
-------------------------------
Provides system tray functionality for the launcher.
"""

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from typing import Callable, Optional
import threading


class SystemTray:
    """System tray icon manager."""

    def __init__(
        self, app_window, on_show: Optional[Callable] = None, on_quit: Optional[Callable] = None
    ):
        """
        Initialize system tray icon.

        Args:
            app_window: The main application window
            on_show: Callback when "Show" is clicked
            on_quit: Callback when "Quit" is clicked
        """
        self.app_window = app_window
        self.on_show_callback = on_show
        self.on_quit_callback = on_quit
        self.icon = None
        self.running = False

    def create_icon_image(self):
        """Create a simple icon image."""
        # Create a 64x64 image with a simple design
        size = 64
        image = Image.new("RGB", (size, size), color="#1f538d")
        draw = ImageDraw.Draw(image)

        # Draw a simple "CV" text or logo
        # For now, draw a circle
        padding = 8
        draw.ellipse(
            [padding, padding, size - padding, size - padding],
            fill="#3b8ed0",
            outline="white",
            width=2,
        )

        # Draw a smaller circle in the center
        center_padding = size // 4
        draw.ellipse(
            [center_padding, center_padding, size - center_padding, size - center_padding],
            fill="white",
        )

        return image

    def on_show(self, icon, item):
        """Handle show window action."""
        self.app_window.after(0, self._show_window)

    def _show_window(self):
        """Show the main window (must be called from main thread)."""
        self.app_window.deiconify()
        self.app_window.lift()
        self.app_window.focus_force()
        if self.on_show_callback:
            self.on_show_callback()

    def on_quit(self, icon, item):
        """Handle quit action."""
        self.running = False
        if self.icon:
            icon.stop()
        if self.on_quit_callback:
            self.app_window.after(0, self.on_quit_callback)

    def on_toggle_visibility(self, icon, item):
        """Toggle window visibility."""
        if self.app_window.state() == "withdrawn":
            self.on_show(icon, item)
        else:
            self.app_window.after(0, self.app_window.withdraw)

    def create_menu(self):
        """Create the tray icon menu."""
        return pystray.Menu(
            item("Show", self.on_show, default=True),
            item("Hide", lambda icon, item: self.app_window.after(0, self.app_window.withdraw)),
            pystray.Menu.SEPARATOR,
            item("Quit", self.on_quit),
        )

    def start(self):
        """Start the system tray icon."""
        if self.running:
            return

        self.running = True
        icon_image = self.create_icon_image()
        self.icon = pystray.Icon("CV-Mindcare", icon_image, "CV-Mindcare", self.create_menu())

        # Run icon in separate thread
        icon_thread = threading.Thread(target=self._run_icon, daemon=True)
        icon_thread.start()

    def _run_icon(self):
        """Run the system tray icon (blocking)."""
        if self.icon:
            self.icon.run()

    def stop(self):
        """Stop the system tray icon."""
        self.running = False
        if self.icon:
            self.icon.stop()
            self.icon = None

    def update_tooltip(self, text: str):
        """Update the tray icon tooltip."""
        if self.icon:
            self.icon.title = text


def create_tray_icon(app_window, on_show=None, on_quit=None) -> SystemTray:
    """
    Create and start a system tray icon.

    Args:
        app_window: Main application window
        on_show: Callback for show action
        on_quit: Callback for quit action

    Returns:
        SystemTray instance
    """
    tray = SystemTray(app_window, on_show, on_quit)
    tray.start()
    return tray
