"""
CV-Mindcare Launcher
-------------------
Desktop launcher application for CV-Mindcare system.
Handles system checks and launches the web dashboard.
"""

import sys
import customtkinter as ctk
from pathlib import Path
from system_check import SystemChecker
from process_manager import ProcessManager

class CVMindcareLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("CV-Mindcare System")
        self.geometry("700x500")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize system components
        self.system_checker = SystemChecker()
        self.process_manager = None
        self.checks_passed = False

        # Initialize UI
        self._create_widgets()
        self._layout_widgets()
        
        # Run initial system check
        self.after(500, self._run_system_check)

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="CV-Mindcare System Launcher",
            font=ctk.CTkFont(size=24, weight="bold")
        )

        # Status frame with scrollable text
        self.status_frame = ctk.CTkFrame(self)
        self.status_text = ctk.CTkTextbox(
            self.status_frame,
            height=250,
            font=ctk.CTkFont(size=12, family="Courier New")
        )
        self.status_text.configure(state="disabled")
        
        # Log frame
        self.log_frame = ctk.CTkFrame(self)
        self.log_label = ctk.CTkLabel(
            self.log_frame,
            text="System Log:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            height=80,
            font=ctk.CTkFont(size=10, family="Courier New")
        )
        self.log_text.configure(state="disabled")
        
        # Buttons
        self.check_button = ctk.CTkButton(
            self,
            text="Re-run System Check",
            command=self._run_system_check
        )
        self.start_button = ctk.CTkButton(
            self,
            text="Start Dashboard",
            command=self._start_dashboard,
            state="disabled",
            fg_color="green",
            hover_color="darkgreen"
        )
        self.stop_button = ctk.CTkButton(
            self,
            text="Stop System",
            command=self._stop_system,
            state="disabled",
            fg_color="red",
            hover_color="darkred"
        )

    def _layout_widgets(self):
        """Layout all widgets using grid system."""
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        # Place widgets
        self.title_label.grid(row=0, column=0, pady=15, sticky="ew")
        
        # Status frame
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Log frame
        self.log_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Button layout
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.check_button.grid(row=0, column=0, padx=10, sticky="ew", in_=button_frame)
        self.start_button.grid(row=0, column=1, padx=10, sticky="ew", in_=button_frame)
        self.stop_button.grid(row=0, column=2, padx=10, sticky="ew", in_=button_frame)

    def _add_status_line(self, line: str):
        """Add a line to the status text."""
        self.status_text.configure(state="normal")
        self.status_text.insert("end", line + "\n")
        self.status_text.configure(state="disabled")
        self.status_text.see("end")
    
    def _clear_status(self):
        """Clear the status text."""
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.configure(state="disabled")
    
    def _add_log_line(self, line: str):
        """Add a line to the log text."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see("end")

    def _run_system_check(self):
        """Run system requirements check."""
        self._clear_status()
        self._add_status_line("Running system checks...\n")
        
        # Run checks
        results = self.system_checker.run_all_checks()
        
        # Display results
        for check_name, (status, message) in results.items():
            icon = "✓" if status else "✗"
            self._add_status_line(f"{icon} {message}")
        
        # Check if all passed
        self.checks_passed = self.system_checker.all_passed()
        
        # Update button states
        if self.checks_passed:
            self._add_status_line("\n✓ All system checks passed!")
            self._add_status_line("You can now start the dashboard.")
            self.start_button.configure(state="normal")
            self._add_log_line("System checks passed - ready to start.")
        else:
            self._add_status_line("\n✗ Some checks failed.")
            self._add_status_line("Please resolve the issues before starting.")
            self.start_button.configure(state="disabled")
            self._add_log_line("System checks failed - please fix issues.")

    def _start_dashboard(self):
        """Launch the web dashboard."""
        if not self.checks_passed:
            self._add_log_line("Cannot start: system checks have not passed.")
            return
        
        # Disable start button, enable stop button
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        # Initialize process manager
        if self.process_manager is None:
            self.process_manager = ProcessManager()
        
        # Start backend
        self._add_log_line("Starting backend server...")
        success = self.process_manager.start_backend(log_callback=self._add_log_line)
        
        if success:
            self._add_log_line("Backend started successfully!")
            # Open dashboard in browser
            self.process_manager.open_dashboard(log_callback=self._add_log_line)
        else:
            self._add_log_line("Failed to start backend.")
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def _stop_system(self):
        """Stop the backend system."""
        if self.process_manager is None:
            return
        
        self._add_log_line("Stopping backend server...")
        self.process_manager.stop_backend(log_callback=self._add_log_line)
        
        # Update button states
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
    
    def on_closing(self):
        """Handle window closing."""
        if self.process_manager is not None:
            self._add_log_line("Shutting down...")
            self.process_manager.cleanup()
        self.destroy()

def main():
    app = CVMindcareLauncher()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()