"""
Progress panel component for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class ProgressPanel:
    """Component for displaying progress and status."""
    
    def __init__(self, parent: tk.Widget, on_apply_pixelation: Optional[Callable] = None):
        self.parent = parent
        self.on_apply_pixelation = on_apply_pixelation
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the progress panel widgets."""
        # Main frame
        self.frame = ttk.Frame(self.parent, padding="5")
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var, mode='determinate'
        )
        self.progress_bar_visible = False
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. If the GUI becomes unresponsive during pixelation, please wait until the operation completes.")
        self.status_bar = ttk.Label(
            self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Apply pixelation button
        self.apply_btn = ttk.Button(
            self.frame, text="Apply Pixelation", command=self._apply_pixelation
        )
        self.apply_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _apply_pixelation(self):
        """Handle apply pixelation button click."""
        if self.on_apply_pixelation:
            self.on_apply_pixelation()
    
    def show_progress_bar(self):
        """Show the progress bar."""
        if not self.progress_bar_visible:
            self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.progress_bar_visible = True
    
    def hide_progress_bar(self):
        """Hide the progress bar."""
        if self.progress_bar_visible:
            self.progress_bar.pack_forget()
            self.progress_bar_visible = False
    
    def set_progress(self, value: float):
        """Set the progress bar value (0-100)."""
        self.progress_var.set(value)
    
    def set_status(self, message: str):
        """Set the status message."""
        self.status_var.set(message)
    
    def set_apply_callback(self, callback: Callable):
        """Set the apply pixelation callback."""
        self.on_apply_pixelation = callback
    
    def enable_apply_button(self, enabled: bool = True):
        """Enable or disable the apply button."""
        if enabled:
            self.apply_btn.config(state="normal")
        else:
            self.apply_btn.config(state="disabled")
    
    def update_progress_from_message(self, message: str):
        """Update progress based on message content."""
        if "Pixelating texture" in message and "/" in message:
            try:
                # Extract progress from message like "Pixelating texture 1/5"
                import re
                match = re.search(r'(\d+)/(\d+)', message)
                if match:
                    current, total = map(int, match.groups())
                    progress_percent = (current / total) * 100
                    # Throttle progress updates to every 5% or every texture if less than 20 total
                    if total <= 20 or current % max(1, total // 20) == 0 or current == total:
                        self.set_progress(progress_percent)
            except:
                pass  # If parsing fails, just continue