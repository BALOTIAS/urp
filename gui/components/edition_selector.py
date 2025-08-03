"""
Edition selector component for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from ..utils.image_utils import ImageUtils


class EditionSelector:
    """Component for selecting game editions."""
    
    def __init__(self, parent: tk.Widget, editions: List[str], on_edition_change: Optional[Callable] = None):
        self.parent = parent
        self.editions = editions
        self.on_edition_change = on_edition_change
        self.selected_edition = tk.StringVar(value=editions[0] if editions else "")
        self.edition_images = []
        self.edition_buttons = []
        
        self._create_widgets()
        self._load_edition_images()
    
    def _create_widgets(self):
        """Create the edition selector widgets."""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label
        ttk.Label(self.frame, text="Select Stronghold Version:").pack(side=tk.TOP, anchor=tk.W, padx=(0, 5))
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.frame)
        self.buttons_frame.pack(fill=tk.X)
        
        # Create buttons
        for idx, edition in enumerate(self.editions):
            btn = tk.Button(
                self.buttons_frame,
                compound="top",
                command=lambda e=edition: self._select_edition(e),
                relief=tk.SUNKEN if self.selected_edition.get() == edition else tk.RAISED,
                width=1,
                height=60
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=5)
            self.edition_buttons.append(btn)
        
        # Configure grid weights
        for i in range(len(self.editions)):
            self.buttons_frame.columnconfigure(i, weight=1)
    
    def _load_edition_images(self):
        """Load images for each edition."""
        for idx, edition in enumerate(self.editions):
            image = ImageUtils.load_edition_image(edition)
            self.edition_images.append(image)
            
            if idx < len(self.edition_buttons):
                self.edition_buttons[idx].config(image=image)
    
    def _select_edition(self, edition: str):
        """Handle edition selection."""
        self.selected_edition.set(edition)
        
        # Update button appearances
        for btn, ed in zip(self.edition_buttons, self.editions):
            btn.config(relief=tk.SUNKEN if ed == edition else tk.RAISED)
        
        # Call callback if provided
        if self.on_edition_change:
            self.on_edition_change(edition)
    
    def get_selected_edition(self) -> str:
        """Get the currently selected edition."""
        return self.selected_edition.get()
    
    def set_selected_edition(self, edition: str):
        """Set the selected edition."""
        if edition in self.editions:
            self._select_edition(edition)
    
    def update_editions(self, editions: List[str]):
        """Update the list of available editions."""
        self.editions = editions
        self.selected_edition.set(editions[0] if editions else "")
        
        # Clear existing buttons
        for btn in self.edition_buttons:
            btn.destroy()
        self.edition_buttons.clear()
        self.edition_images.clear()
        
        # Recreate buttons
        for idx, edition in enumerate(editions):
            btn = tk.Button(
                self.buttons_frame,
                compound="top",
                command=lambda e=edition: self._select_edition(e),
                relief=tk.SUNKEN if self.selected_edition.get() == edition else tk.RAISED,
                width=1,
                height=60
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=5)
            self.edition_buttons.append(btn)
        
        # Reload images
        self._load_edition_images()
        
        # Update grid weights
        for i in range(len(editions)):
            self.buttons_frame.columnconfigure(i, weight=1)