"""
Path selector component for the GUI.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional


class PathSelector:
    """Component for selecting game installation paths."""
    
    def __init__(
        self, 
        parent: tk.Widget, 
        edition_name: str,
        initial_path: str = "",
        on_path_change: Optional[Callable] = None,
        validate_path: Optional[Callable] = None
    ):
        self.parent = parent
        self.edition_name = edition_name
        self.on_path_change = on_path_change
        self.validate_path = validate_path or self._default_validate_path
        
        self._create_widgets(initial_path)
    
    def _create_widgets(self, initial_path: str):
        """Create the path selector widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Game Installation", padding="10")
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Path label
        self.path_label = ttk.Label(
            self.frame, text=f"{self.edition_name} Installation Folder:"
        )
        self.path_label.pack(anchor=tk.W, padx=5)
        
        # Path selection frame
        path_select_frame = ttk.Frame(self.frame)
        path_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Path entry
        self.path_var = tk.StringVar(value=initial_path)
        self.path_entry = ttk.Entry(path_select_frame, textvariable=self.path_var, width=30)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse button
        self.browse_btn = ttk.Button(
            path_select_frame, text="Browse", command=self._browse_path
        )
        self.browse_btn.pack(side=tk.RIGHT)
    
    def _browse_path(self):
        """Open file dialog to browse for game directory."""
        directory = filedialog.askdirectory(
            title=f"Select {self.edition_name} Installation Folder"
        )
        
        if directory:
            if self.validate_path(directory):
                self.path_var.set(directory)
                if self.on_path_change:
                    self.on_path_change(directory)
            else:
                messagebox.showerror(
                    "Invalid Directory",
                    f"The selected directory does not appear to be a valid {self.edition_name} installation.",
                )
    
    def _default_validate_path(self, directory: str) -> bool:
        """Default path validation logic."""
        import os
        
        # Check for executable
        if self.edition_name == "Stronghold Definitive Edition":
            exe_path = os.path.join(directory, "Stronghold 1 Definitive Edition.exe")
            data_folder = os.path.join(directory, "Stronghold 1 Definitive Edition_Data")
        elif self.edition_name == "Stronghold Crusader Definitive Edition":
            exe_path = os.path.join(directory, "Stronghold Crusader Definitive Edition.exe")
            data_folder = os.path.join(directory, "Stronghold Crusader Definitive Edition_Data")
        else:
            # Fallback: just check for any .exe and _Data folder
            exe_path = None
            data_folder = None
            for file in os.listdir(directory):
                if file.endswith(".exe"):
                    exe_path = os.path.join(directory, file)
                if file.endswith("_Data") and os.path.isdir(os.path.join(directory, file)):
                    data_folder = os.path.join(directory, file)
        
        return ((exe_path and os.path.exists(exe_path)) or 
               (data_folder and os.path.isdir(data_folder)))
    
    def get_path(self) -> str:
        """Get the currently selected path."""
        return self.path_var.get()
    
    def set_path(self, path: str):
        """Set the path."""
        self.path_var.set(path)
    
    def set_edition_name(self, edition_name: str):
        """Update the edition name."""
        self.edition_name = edition_name
        self.path_label.config(text=f"{edition_name} Installation Folder:")
    
    def set_validation_callback(self, validate_func: Callable):
        """Set a custom validation function."""
        self.validate_path = validate_func
    
    def set_path_change_callback(self, callback: Callable):
        """Set a callback for when the path changes."""
        self.on_path_change = callback