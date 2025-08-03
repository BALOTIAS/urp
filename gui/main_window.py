"""
Main window for the Unofficial Retro Patch GUI.
"""

import tkinter as tk
from tkinter import ttk, PhotoImage
import threading
import time
import os
import sys
from typing import Optional

from .components.edition_selector import EditionSelector
from .components.path_selector import PathSelector
from .components.backup_manager_ui import BackupManagerUI
from .components.preview_panel import PreviewPanel
from .components.progress_panel import ProgressPanel
from .utils.image_utils import ImageUtils
from core.main_processor import MainProcessor
from core.config_manager import ConfigManager


class RetroPixelatorGUI:
    """Main GUI application for the Unofficial Retro Patch."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.main_processor = MainProcessor()
        
        # Initialize GUI components
        self.setup_components()
        self.setup_callbacks()
        
        # Load initial data
        self.load_initial_data()
    
    def setup_window(self):
        """Setup the main window."""
        self.root.title("Unofficial Retro Patch (v1.0.0)")
        self.root.geometry("1280x840")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # Set window icon
        self.set_window_icon()
    
    def set_window_icon(self):
        """Set the window icon."""
        try:
            icon_image = ImageUtils.load_icon_image("urp")
            if icon_image:
                if sys.platform == "win32":
                    self.root.iconbitmap("assets/icon/urp.ico")
                else:
                    self.root.iconphoto(True, icon_image)
        except Exception as e:
            print(f"Could not set application icon: {e}")
    
    def setup_components(self):
        """Setup all GUI components."""
        # Create scrollable container
        self.setup_scrollable_container()
        
        # Create main content frame
        self.main_frame = ttk.Frame(self.canvas)
        self.main_frame_id = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.columnconfigure(0, weight=1, uniform="col")
        self.main_frame.columnconfigure(1, weight=1, uniform="col")
        self.main_frame.rowconfigure(0, weight=1)
        
        # Create left and right columns
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Setup components
        self.setup_left_column()
        self.setup_right_column()
        self.setup_progress_panel()
        
        # Update scrollregion when frame size changes
        def on_frame_configure(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.main_frame.bind("<Configure>", on_frame_configure)
        
        # Make canvas resize frame width to match canvas width
        def on_canvas_configure(event=None):
            self.canvas.itemconfig(self.main_frame_id, width=self.canvas.winfo_width())
        self.canvas.bind("<Configure>", on_canvas_configure)
    
    def setup_scrollable_container(self):
        """Setup scrollable container for the main content."""
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        hscroll = ttk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mousewheel scrolling
        def _on_mousewheel(event):
            if event.state & 0x1:  # Shift pressed for horizontal scroll
                self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel)
    
    def setup_left_column(self):
        """Setup the left column components."""
        # Logo and description
        self.setup_logo_and_description()
        
        # Edition selector
        editions = self.config_manager.get_editions()
        if not editions:
            editions = ["Stronghold Definitive Edition", "Stronghold Crusader Definitive Edition"]
        
        self.edition_selector = EditionSelector(
            self.left_frame, 
            editions, 
            on_edition_change=self.on_edition_change
        )
        
        # Path selector
        self.path_selector = PathSelector(
            self.left_frame,
            editions[0],
            initial_path=self.config_manager.get_edition_target_folder(editions[0]),
            on_path_change=self.on_path_change,
            validate_path=self.validate_game_directory
        )
        
        # Backup manager
        self.backup_manager = BackupManagerUI(
            self.left_frame,
            on_refresh=self.refresh_backups,
            on_restore=self.restore_backup
        )
    
    def setup_right_column(self):
        """Setup the right column components."""
        # Preview panel
        self.preview_panel = PreviewPanel(
            self.right_frame,
            on_pixelation_change=self.on_pixelation_change,
            on_black_shadows_change=self.on_black_shadows_change
        )
    
    def setup_progress_panel(self):
        """Setup the progress panel."""
        self.progress_panel = ProgressPanel(
            self.root,
            on_apply_pixelation=self.apply_pixelation_threaded
        )
    
    def setup_logo_and_description(self):
        """Setup the logo and description section."""
        logo_desc_frame = ttk.Frame(self.left_frame)
        logo_desc_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Load logo
        logo_path = "assets/icon/urp-small.png" if os.path.exists("assets/icon/urp-small.png") else "assets/icon/urp.png"
        if os.path.exists(logo_path):
            logo_image = PhotoImage(file=logo_path)
            logo_label = ttk.Label(logo_desc_frame, image=logo_image)
            logo_label.image = logo_image
            logo_label.pack(side=tk.LEFT, padx=(0, 10), pady=0)
        
        # Description
        desc_text = ("The Unofficial Retro Patch applies a pixelated look to Stronghold,\n"
                     "giving it a more retro appearance that feels closer to the original game's art style.\n"
                     "This tool modifies the game's texture assets to create a nostalgic experience.\n\n"
                     "Made with <3 by BALOTIAS.\n\n"
                     "Stronghold Definitive Edition &\nStronghold Crusader Definitive Edition © Firefly Studios")
        
        description = ttk.Label(
            logo_desc_frame,
            text=desc_text,
            wraplength=1,  # will be set dynamically
            justify="left",
            anchor="center",
        )
        description.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=0)
        
        # Dynamic wraplength
        def update_desc_wrap(event=None):
            left_width = self.left_frame.winfo_width()
            logo_width = logo_label.winfo_width() if 'logo_label' in locals() else 100
            pad = 40
            wrap = max(200, left_width - logo_width - pad)
            description.config(wraplength=wrap)
        
        self.left_frame.bind('<Configure>', update_desc_wrap)
        if 'logo_label' in locals():
            logo_label.bind('<Configure>', update_desc_wrap)
    
    def setup_callbacks(self):
        """Setup component callbacks."""
        # Set callbacks for components
        self.preview_panel.set_pixelation_change_callback(self.on_pixelation_change)
        self.preview_panel.set_black_shadows_change_callback(self.on_black_shadows_change)
        self.progress_panel.set_apply_callback(self.apply_pixelation_threaded)
    
    def load_initial_data(self):
        """Load initial data for the GUI."""
        # Load initial preview
        selected_edition = self.edition_selector.get_selected_edition()
        self.preview_panel.load_edition_preview(selected_edition)
        
        # Load initial backups
        self.refresh_backups()
    
    def on_edition_change(self, edition: str):
        """Handle edition change."""
        # Update path selector
        self.path_selector.set_edition_name(edition)
        self.path_selector.set_path(self.config_manager.get_edition_target_folder(edition))
        
        # Update preview
        self.preview_panel.load_edition_preview(edition)
        
        # Refresh backups
        self.refresh_backups()
    
    def on_path_change(self, path: str):
        """Handle path change."""
        edition = self.edition_selector.get_selected_edition()
        self.config_manager.set_edition_target_folder(edition, path)
        self.progress_panel.set_status(f"Game path set to: {path}")
        self.refresh_backups()
    
    def on_pixelation_change(self, amount: float):
        """Handle pixelation amount change."""
        # This can be used for real-time updates if needed
        pass
    
    def on_black_shadows_change(self, enabled: bool):
        """Handle black shadows toggle change."""
        # This can be used for real-time updates if needed
        pass
    
    def validate_game_directory(self, directory: str) -> bool:
        """Validate that a directory is a valid game installation."""
        return self.main_processor.validate_edition_directory(
            self.edition_selector.get_selected_edition(), 
            directory
        )
    
    def refresh_backups(self):
        """Refresh the backup list."""
        edition = self.edition_selector.get_selected_edition()
        backups = self.main_processor.find_backups_for_edition(edition)
        self.backup_manager.update_backups(backups)
        
        if not backups:
            self.progress_panel.set_status("No backup files found")
        else:
            self.progress_panel.set_status(f"Found {len(backups)} backup files")
    
    def restore_backup(self, relative_path: str):
        """Restore a backup file."""
        edition = self.edition_selector.get_selected_edition()
        game_path = self.path_selector.get_path()
        backup_file = os.path.join(game_path, relative_path)
        
        import re
        original_file = re.sub(r"\.backup\d{3}$", "", backup_file)
        
        if not os.path.exists(backup_file):
            self.backup_manager.show_message(f"Backup file not found: {backup_file}", "error")
            return
        
        try:
            success = self.main_processor.restore_backup(backup_file, original_file)
            if success:
                self.backup_manager.show_message(f"Successfully restored: {relative_path}", "info")
                self.refresh_backups()
            else:
                self.backup_manager.show_message("Failed to restore backup", "error")
        except Exception as e:
            self.backup_manager.show_message(f"Failed to restore backup: {str(e)}", "error")
    
    def apply_pixelation_threaded(self):
        """Apply pixelation in a background thread."""
        def worker():
            try:
                # Get current settings
                edition = self.edition_selector.get_selected_edition()
                game_path = self.path_selector.get_path()
                pixelation_amount = self.preview_panel.pixelation_amount()
                black_shadows = self.preview_panel.get_black_shadows_enabled()
                
                # Validate path
                if not game_path or not os.path.exists(game_path):
                    self.root.after(0, lambda: self.progress_panel.set_status("Error: Please select a valid game installation path first."))
                    return
                
                # Save configuration
                self.config_manager.set_edition_target_folder(edition, game_path)
                
                # Show progress
                self.root.after(0, self.progress_panel.show_progress_bar)
                self.root.after(0, lambda: self.progress_panel.set_progress(0))
                self.root.after(0, lambda: self.progress_panel.set_status("Applying pixelation... This may take a while"))
                self.root.after(0, lambda: self.progress_panel.enable_apply_button(False))
                
                # Logger for GUI updates
                def gui_logger(msg):
                    self.root.after(0, lambda: self.progress_panel.set_status(str(msg)))
                    self.root.after(0, lambda: self.progress_panel.update_progress_from_message(str(msg)))
                
                # Apply pixelation
                self.main_processor.pixelate_edition(
                    edition,
                    logger=gui_logger,
                    resize_amount=pixelation_amount,
                    black_shadows=black_shadows
                )
                
                # Show completion
                self.root.after(0, lambda: self.progress_panel.set_status("Pixelation has been applied successfully!"))
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.progress_panel.set_status(f"Failed to apply pixelation: {error_msg}"))
            finally:
                # Cleanup
                def cleanup():
                    self.root.after(0, self.progress_panel.hide_progress_bar)
                    self.root.after(0, lambda: self.progress_panel.set_status("Ready"))
                    self.root.after(0, lambda: self.progress_panel.enable_apply_button(True))
                self.root.after(1000, cleanup)
        
        threading.Thread(target=worker, daemon=True).start()