"""
GUI components for the Unofficial Retro Patch application.
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, PhotoImage
from PIL import Image, ImageTk
from typing import Optional, Callable

from ..core.application import Application
from ..config.settings import settings
from ..utils.validation_utils import ValidationUtils
from ..utils.file_utils import FileUtils
from ..processing.image_processor import ImageProcessor


class EditionSelector:
    """Component for selecting game editions."""
    
    def __init__(self, parent: tk.Widget, selected_edition: tk.StringVar, app: Application):
        """Initialize the edition selector.
        
        Args:
            parent: Parent widget.
            selected_edition: StringVar for the selected edition.
            app: Application instance.
        """
        self.parent = parent
        self.selected_edition = selected_edition
        self.app = app
        
        self.setup_widget()
    
    def setup_widget(self) -> None:
        """Setup the edition selector widget."""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Title
        ttk.Label(self.frame, text="Select Stronghold Version:").pack(side=tk.TOP, anchor=tk.W, padx=(0, 5))
        
        # Edition buttons
        self.edition_images = []
        self.edition_buttons = []
        
        edition_image_paths = [
            "assets/firefly/shde.png",
            "assets/firefly/shcde.png"
        ]
        
        # Load edition images
        for path in edition_image_paths:
            if os.path.exists(path):
                img = Image.open(path)
                img.thumbnail((96, 48), Image.Resampling.LANCZOS)
                self.edition_images.append(ImageTk.PhotoImage(img))
            else:
                self.edition_images.append(None)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill=tk.X)
        
        editions = self.app.get_available_editions()
        for idx, edition in enumerate(editions):
            btn = tk.Button(
                buttons_frame,
                image=self.edition_images[idx] if idx < len(self.edition_images) else None,
                compound="top",
                command=lambda e=edition: self.select_edition(e),
                relief=tk.SUNKEN if self.selected_edition.get() == edition else tk.RAISED,
                width=1,
                height=60
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=5)
            self.edition_buttons.append(btn)
        
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
    
    def select_edition(self, edition: str) -> None:
        """Select an edition.
        
        Args:
            edition: Name of the edition to select.
        """
        self.selected_edition.set(edition)
        for btn, ed in zip(self.edition_buttons, self.app.get_available_editions()):
            btn.config(relief=tk.SUNKEN if ed == edition else tk.RAISED)


class PathSelector:
    """Component for selecting game installation paths."""
    
    def __init__(self, parent: tk.Widget, selected_edition: tk.StringVar, app: Application):
        """Initialize the path selector.
        
        Args:
            parent: Parent widget.
            selected_edition: StringVar for the selected edition.
            app: Application instance.
        """
        self.parent = parent
        self.selected_edition = selected_edition
        self.app = app
        
        self.setup_widget()
    
    def setup_widget(self) -> None:
        """Setup the path selector widget."""
        self.frame = ttk.LabelFrame(self.parent, text="Game Installation", padding="10")
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Path label
        self.path_label = ttk.Label(self.frame, text=f"{self.selected_edition.get()} Installation Folder:")
        self.path_label.pack(anchor=tk.W, padx=5)
        
        # Path selection frame
        path_select_frame = ttk.Frame(self.frame)
        path_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Path entry
        self.path_var = tk.StringVar()
        self.update_path_var_from_config()
        path_entry = ttk.Entry(path_select_frame, textvariable=self.path_var, width=30)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse button
        browse_btn = ttk.Button(path_select_frame, text="Browse", command=self.browse_game_path)
        browse_btn.pack(side=tk.RIGHT)
    
    def update_path_var_from_config(self) -> None:
        """Update path variable from configuration."""
        edition = self.selected_edition.get()
        config = self.app.get_edition_config(edition)
        self.path_var.set(config.get("target_folder", ""))
    
    def update_for_edition(self, edition: str) -> None:
        """Update the path selector for a specific edition.
        
        Args:
            edition: Name of the edition.
        """
        self.path_label.config(text=f"{edition} Installation Folder:")
        self.update_path_var_from_config()
    
    def get_path(self) -> str:
        """Get the selected path.
        
        Returns:
            Selected path.
        """
        return self.path_var.get()
    
    def browse_game_path(self) -> None:
        """Browse for game installation path."""
        directory = filedialog.askdirectory(
            title=f"Select {self.selected_edition.get()} Installation Folder"
        )
        if directory:
            self.path_var.set(directory)
            if self.validate_game_directory(directory):
                edition = self.selected_edition.get()
                self.app.set_edition_config(edition, "target_folder", directory)
            else:
                messagebox.showerror(
                    "Invalid Directory",
                    f"The selected directory does not appear to be a valid {self.selected_edition.get()} installation.",
                )
                self.path_var.set("")
    
    def validate_game_directory(self, directory: str) -> bool:
        """Validate if a directory is a valid game installation.
        
        Args:
            directory: Path to the directory to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        edition = self.selected_edition.get()
        is_valid, _ = ValidationUtils.validate_game_directory(directory, edition)
        return is_valid


class BackupManager:
    """Component for managing backup files."""
    
    def __init__(self, parent: tk.Widget, path_selector: PathSelector):
        """Initialize the backup manager.
        
        Args:
            parent: Parent widget.
            path_selector: Path selector component.
        """
        self.parent = parent
        self.path_selector = path_selector
        
        self.setup_widget()
    
    def setup_widget(self) -> None:
        """Setup the backup manager widget."""
        self.frame = ttk.LabelFrame(self.parent, text="Backup Management", padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Backup list
        self.backup_list = ttk.Treeview(
            self.frame, columns=("file", "date"), show="headings"
        )
        self.backup_list.heading("file", text="Asset File")
        self.backup_list.heading("date", text="Backup Date")
        self.backup_list.column("file", width=180)
        self.backup_list.column("date", width=120)
        self.backup_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.backup_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backup_list.configure(yscrollcommand=scrollbar.set)
        
        # Actions frame
        backup_actions = ttk.Frame(self.parent, padding="5")
        backup_actions.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        refresh_btn = ttk.Button(backup_actions, text="Refresh Backup List", command=self.refresh_backups)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        restore_btn = ttk.Button(backup_actions, text="Restore Selected Backup", command=self.restore_backup)
        restore_btn.pack(side=tk.LEFT)
    
    def refresh_backups(self) -> None:
        """Refresh the backup list."""
        for item in self.backup_list.get_children():
            self.backup_list.delete(item)
        
        game_path = self.path_selector.get_path()
        if not game_path or not os.path.exists(game_path):
            return
        
        backup_files = FileUtils.find_backup_files(game_path)
        for backup_file, original_file in backup_files:
            relative_path = os.path.relpath(backup_file, game_path)
            backup_date = FileUtils.get_file_modified_date(backup_file) or "Unknown"
            self.backup_list.insert("", "end", values=(relative_path, backup_date))
    
    def restore_backup(self) -> None:
        """Restore a selected backup."""
        selected_items = self.backup_list.selection()
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select a backup file to restore.")
            return
        
        item = self.backup_list.item(selected_items[0])
        relative_path = item["values"][0]
        game_path = self.path_selector.get_path()
        backup_file = os.path.join(game_path, relative_path)
        
        import re
        original_file = re.sub(r"\.backup\d{3}$", "", backup_file)
        
        if not os.path.exists(backup_file):
            messagebox.showerror("Error", f"Backup file not found: {backup_file}")
            return
        
        try:
            if os.path.exists(original_file):
                os.rename(original_file, original_file + ".tmp")
            os.rename(backup_file, original_file)
            if os.path.exists(original_file + ".tmp"):
                os.remove(original_file + ".tmp")
            messagebox.showinfo("Success", f"Successfully restored: {relative_path}")
            self.refresh_backups()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")


class PreviewPanel:
    """Component for previewing pixelation effects."""
    
    def __init__(self, parent: tk.Widget, selected_edition: tk.StringVar):
        """Initialize the preview panel.
        
        Args:
            parent: Parent widget.
            selected_edition: StringVar for the selected edition.
        """
        self.parent = parent
        self.selected_edition = selected_edition
        self.preview_image = None
        self.preview_pil = None
        
        self.setup_widget()
    
    def setup_widget(self) -> None:
        """Setup the preview panel widget."""
        self.frame = ttk.LabelFrame(self.parent, text="Preview", padding="10")
        self.frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Preview canvas
        self.preview_canvas = tk.Label(self.frame)
        self.preview_canvas.pack(padx=5, pady=5)
        
        # Load initial preview
        self.load_placeholder_image(self.selected_edition.get())
        self.update_preview()
    
    def load_placeholder_image(self, edition: str) -> None:
        """Load placeholder image for preview.
        
        Args:
            edition: Name of the edition.
        """
        if edition == "Stronghold Definitive Edition":
            placeholder_path = "assets/firefly/shde-screenshot.jpg"
        elif edition == "Stronghold Crusader Definitive Edition":
            placeholder_path = "assets/firefly/shcde-screenshot.jpg"
        else:
            placeholder_path = "assets/firefly/shde-screenshot.jpg"
        
        if os.path.exists(placeholder_path):
            self.preview_pil = Image.open(placeholder_path)
        else:
            # Create a default placeholder
            self.preview_pil = Image.new("RGB", (400, 300), (128, 128, 128))
    
    def update_preview(self, resize_amount: float = 0.5, black_shadows: bool = False) -> None:
        """Update the preview image.
        
        Args:
            resize_amount: Resize amount for pixelation.
            black_shadows: Whether to apply black shadows.
        """
        if self.preview_pil is None:
            return
        
        # Apply pixelation
        pixelated = ImageProcessor.pixelate_image(self.preview_pil, resize_amount)
        
        # Apply black shadows if enabled
        if black_shadows:
            pixelated = ImageProcessor.apply_black_shadows(pixelated)
        
        # Make preview square (crop to square center)
        width, height = pixelated.size
        side = min(width, height)
        left = (width - side) // 1.8
        top = (height - side) // 2
        right = left + side
        bottom = top + side
        pixelated = pixelated.crop((left, top, right, bottom))
        
        # Convert to PhotoImage
        self.preview_image = ImageTk.PhotoImage(pixelated)
        self.preview_canvas.config(image=self.preview_image, width=560, height=480)
        self.preview_canvas.image = self.preview_image


class OptionsPanel:
    """Component for pixelation options."""
    
    def __init__(self, parent: tk.Widget):
        """Initialize the options panel.
        
        Args:
            parent: Parent widget.
        """
        self.parent = parent
        
        self.setup_widget()
    
    def setup_widget(self) -> None:
        """Setup the options panel widget."""
        self.frame = ttk.LabelFrame(self.parent, text="Options", padding="10")
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Black Shadows toggle
        self.black_shadows_var = tk.BooleanVar(value=True)
        self.black_shadows_checkbox = ttk.Checkbutton(
            self.frame,
            text="Black Shadows",
            variable=self.black_shadows_var
        )
        self.black_shadows_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        
        # Note about black shadows
        black_shadows_note = ttk.Label(
            self.frame,
            text="(Replaces semi-transparent shadows with solid black in game textures)",
            font=("", 8),
            foreground="gray"
        )
        black_shadows_note.pack(anchor=tk.W, padx=5, pady=(0, 2))
    
    def get_black_shadows(self) -> bool:
        """Get the black shadows setting.
        
        Returns:
            True if black shadows are enabled, False otherwise.
        """
        return self.black_shadows_var.get()


class ProgressPanel:
    """Component for progress tracking and status display."""
    
    def __init__(self, parent: tk.Widget, apply_callback: Callable):
        """Initialize the progress panel.
        
        Args:
            parent: Parent widget.
            apply_callback: Callback function for applying pixelation.
        """
        self.parent = parent
        self.apply_callback = apply_callback
        
        self.setup_widget()
    
    def setup_widget(self) -> None:
        """Setup the progress panel widget."""
        self.frame = ttk.Frame(self.parent, padding="5")
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var, mode='determinate'
        )
        self.progress_bar_visible = False
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. If the GUI becomes unresponsive during pixelation, please wait until the operation completes.")
        status_bar = ttk.Label(
            self.frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Apply button
        apply_btn = ttk.Button(self.frame, text="Apply Pixelation", command=self.apply_callback)
        apply_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def show_progress(self) -> None:
        """Show the progress bar."""
        if not self.progress_bar_visible:
            self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.progress_bar_visible = True
    
    def hide_progress(self) -> None:
        """Hide the progress bar."""
        if self.progress_bar_visible:
            self.progress_bar.pack_forget()
            self.progress_bar_visible = False
    
    def set_status(self, message: str) -> None:
        """Set the status message.
        
        Args:
            message: Status message to display.
        """
        self.status_var.set(message)
    
    def set_progress(self, value: float) -> None:
        """Set the progress value.
        
        Args:
            value: Progress value (0.0 to 100.0).
        """
        self.progress_var.set(value)