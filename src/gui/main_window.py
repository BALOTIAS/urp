"""
Main window for the Unofficial Retro Patch GUI.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, PhotoImage
import threading
import time
import gc
from PIL import Image, ImageTk
from typing import Optional, Callable

from ..core.application import Application
from ..config.settings import settings
from .components import (
    EditionSelector,
    PathSelector,
    BackupManager,
    PreviewPanel,
    OptionsPanel,
    ProgressPanel
)


class MainWindow:
    """Main window for the Unofficial Retro Patch application."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the main window.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.setup_window()
        self.setup_application()
        self.setup_components()
        self.setup_layout()
        self.setup_event_handlers()
    
    def setup_window(self) -> None:
        """Setup the main window properties."""
        self.root.title("Unofficial Retro Patch")
        self.root.geometry("1280x840")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # Set window icon
        self.setup_icon()
    
    def setup_icon(self) -> None:
        """Setup the window icon."""
        try:
            if getattr(sys, "frozen", False):
                application_path = sys._MEIPASS
                ico_path = os.path.join(
                    application_path,
                    "assets/icon",
                    "urp.ico" if sys.platform == "win32" else "urp.png",
                )
            else:
                ico_path = os.path.join(
                    "assets/icon", "urp.ico" if sys.platform == "win32" else "urp.png"
                )

            if os.path.exists(ico_path):
                if sys.platform == "win32":
                    self.root.iconbitmap(ico_path)
                else:
                    icon_img = tk.PhotoImage(file=ico_path)
                    self.root.iconphoto(True, icon_img)
        except Exception as e:
            print(f"Could not set application icon: {e}")
    
    def setup_application(self) -> None:
        """Setup the application instance."""
        self.app = Application(logger=self.log_to_gui)
        self.selected_edition = tk.StringVar(value=self.app.get_available_editions()[0])
    
    def setup_components(self) -> None:
        """Setup GUI components."""
        # Create scrollable container
        self.container = ttk.Frame(self.root)
        self.canvas = tk.Canvas(self.container, borderwidth=0, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.hscroll = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vscroll.set, xscrollcommand=self.hscroll.set)
        
        # Main frame inside canvas
        self.main_frame = ttk.Frame(self.canvas, padding="10")
        self.main_frame_id = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # Setup components
        self.edition_selector = EditionSelector(self.main_frame, self.selected_edition, self.app)
        self.path_selector = PathSelector(self.main_frame, self.selected_edition, self.app)
        self.backup_manager = BackupManager(self.main_frame, self.path_selector)
        self.preview_panel = PreviewPanel(self.main_frame, self.selected_edition)
        self.options_panel = OptionsPanel(self.main_frame)
        self.progress_panel = ProgressPanel(self.root, self.apply_pixelation_threaded)
    
    def setup_layout(self) -> None:
        """Setup the window layout."""
        # Pack scrollable container
        self.container.pack(fill=tk.BOTH, expand=True)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure main frame
        self.main_frame.columnconfigure(0, weight=1, uniform="col")
        self.main_frame.columnconfigure(1, weight=1, uniform="col")
        self.main_frame.rowconfigure(0, weight=1)
        
        # Layout components
        self.edition_selector.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.path_selector.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.backup_manager.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        
        self.preview_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.options_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        
        # Pack progress panel at bottom
        self.progress_panel.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup scroll region updates
        self.setup_scroll_handlers()
    
    def setup_scroll_handlers(self) -> None:
        """Setup scroll region update handlers."""
        def on_frame_configure(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        def on_canvas_configure(event=None):
            self.canvas.itemconfig(self.main_frame_id, width=self.canvas.winfo_width())
        
        def on_mousewheel(event):
            if event.state & 0x1:  # Shift pressed for horizontal scroll
                self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.main_frame.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", on_mousewheel)
    
    def setup_event_handlers(self) -> None:
        """Setup event handlers."""
        self.selected_edition.trace("w", self.on_edition_change)
    
    def on_edition_change(self, *args) -> None:
        """Handle edition change."""
        edition = self.selected_edition.get()
        self.path_selector.update_for_edition(edition)
        self.backup_manager.refresh_backups()
        self.preview_panel.load_placeholder_image(edition)
        self.preview_panel.update_preview()
    
    def log_to_gui(self, message: str) -> None:
        """Log message to GUI status bar."""
        self.progress_panel.set_status(message)
    
    def apply_pixelation_threaded(self) -> None:
        """Apply pixelation in a background thread."""
        def worker():
            try:
                # Get current settings
                edition = self.selected_edition.get()
                game_path = self.path_selector.get_path()
                black_shadows = self.options_panel.get_black_shadows()
                
                # Validate game path
                if not game_path or not os.path.exists(game_path):
                    self.root.after(0, lambda: self.progress_panel.set_status(
                        "Error: Please select a valid game installation path first."
                    ))
                    return
                
                # Update configuration
                self.app.set_edition_config(edition, "target_folder", game_path)
                
                # Show progress
                self.root.after(0, self.progress_panel.show_progress)
                self.root.after(0, lambda: self.progress_panel.set_status("Applying pixelation... This may take a while"))
                
                # Process pixelation
                files_to_replace = self.app.pixelate_edition(edition, black_shadows)
                
                # Cleanup memory
                gc.collect()
                time.sleep(1)
                
                self.root.after(0, lambda: self.progress_panel.set_status("Pixelation has been applied successfully!"))
                
                # Replace files
                self.root.after(0, lambda: self.progress_panel.set_status("Replacing files..."))
                self.app.replace_files(files_to_replace)
                self.root.after(0, lambda: self.progress_panel.set_status("Files replaced successfully!"))
                
                # Refresh backups
                self.root.after(0, self.backup_manager.refresh_backups)
                
            except Exception as e:
                self.root.after(0, lambda: self.progress_panel.set_status(f"Failed to apply pixelation: {str(e)}"))
            finally:
                # Hide progress after delay
                def cleanup():
                    self.root.after(0, self.progress_panel.hide_progress)
                    self.root.after(0, lambda: self.progress_panel.set_status("Ready"))
                self.root.after(1000, cleanup)
        
        threading.Thread(target=worker, daemon=True).start()


def main():
    """Main entry point for the GUI."""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()