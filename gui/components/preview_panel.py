"""
Preview panel component for the GUI.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from PIL import Image, ImageTk
from ..utils.image_utils import ImageUtils


class PreviewPanel:
    """Component for displaying pixelation preview."""
    
    def __init__(
        self, 
        parent: tk.Widget,
        on_pixelation_change: Optional[Callable] = None,
        on_black_shadows_change: Optional[Callable] = None
    ):
        self.parent = parent
        self.on_pixelation_change = on_pixelation_change
        self.on_black_shadows_change = on_black_shadows_change
        
        self.preview_image = None
        self.preview_pil = None
        self.current_edition = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the preview panel widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(
            self.parent, 
            text="Preview (This just pixelates a screenshot, the actual game will look better)", 
            padding="10"
        )
        self.frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Preview canvas
        self.preview_canvas = tk.Label(self.frame)
        self.preview_canvas.pack(padx=5, pady=5)
        
        # Pixelation amount frame
        pixelation_frame = ttk.LabelFrame(self.parent, text="Pixelation Amount", padding="10")
        pixelation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Pixelation slider
        self.pixelation_var = tk.DoubleVar(value=0.5)
        self.pixelation_slider = ttk.Scale(
            pixelation_frame,
            from_=0.1,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.pixelation_var,
            command=self._on_pixelation_change
        )
        self.pixelation_slider.pack(fill=tk.X, padx=5, pady=5)
        
        # Pixelation label
        self.pixelation_label = ttk.Label(pixelation_frame, text="Pixelation: 0.5")
        self.pixelation_label.pack(anchor=tk.CENTER)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.parent, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Black shadows toggle
        self.black_shadows_var = tk.BooleanVar(value=True)
        self.black_shadows_checkbox = ttk.Checkbutton(
            options_frame,
            text="Black Shadows",
            variable=self.black_shadows_var,
            command=self._on_black_shadows_change
        )
        self.black_shadows_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        
        # Black shadows note
        black_shadows_note = ttk.Label(
            options_frame,
            text="(Replaces semi-transparent shadows with solid black)",
            font=("", 8),
            foreground="gray"
        )
        black_shadows_note.pack(anchor=tk.W, padx=5, pady=(0, 2))
    
    def _on_pixelation_change(self, event=None):
        """Handle pixelation amount change."""
        self.pixelation_label.config(text=f"Pixelation: {self.pixelation_amount():.2f} (Recommended: 0.5)")
        self._update_preview()
        
        if self.on_pixelation_change:
            self.on_pixelation_change(self.pixelation_amount())
    
    def _on_black_shadows_change(self, event=None):
        """Handle black shadows toggle change."""
        self._update_preview()
        
        if self.on_black_shadows_change:
            self.on_black_shadows_change(self.black_shadows_var.get())
    
    def _update_preview(self):
        """Update the preview image."""
        if not self.preview_pil:
            return
        
        try:
            # Create preview image with current settings
            preview_img = ImageUtils.create_preview_image(
                self.preview_pil,
                self.pixelation_amount(),
                self.black_shadows_var.get()
            )
            
            # Convert to PhotoImage for tkinter
            self.preview_image = ImageTk.PhotoImage(preview_img)
            self.preview_canvas.config(image=self.preview_image, width=560, height=480)
            self.preview_canvas.image = self.preview_image
            
        except Exception as e:
            print(f"Could not update preview: {e}")
    
    def pixelation_amount(self) -> float:
        """Get the current pixelation amount."""
        return round(self.pixelation_var.get(), 2)
    
    def set_pixelation_amount(self, amount: float):
        """Set the pixelation amount."""
        self.pixelation_var.set(amount)
        self._on_pixelation_change()
    
    def get_black_shadows_enabled(self) -> bool:
        """Get whether black shadows are enabled."""
        return self.black_shadows_var.get()
    
    def set_black_shadows_enabled(self, enabled: bool):
        """Set whether black shadows are enabled."""
        self.black_shadows_var.set(enabled)
        self._on_black_shadows_change()
    
    def load_edition_preview(self, edition_name: str):
        """Load preview for a specific edition."""
        self.current_edition = edition_name
        self.preview_pil = ImageUtils.load_placeholder_image(edition_name)
        self._update_preview()
    
    def set_pixelation_change_callback(self, callback: Callable):
        """Set the pixelation change callback."""
        self.on_pixelation_change = callback
    
    def set_black_shadows_change_callback(self, callback: Callable):
        """Set the black shadows change callback."""
        self.on_black_shadows_change = callback