"""
Main window GUI component for the Unofficial Retro Patch application.

This module contains the main application window and its layout components.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, PhotoImage
from PIL import Image, ImageTk
import threading
import time
import gc
from typing import Optional, Callable

from ..core.config import config_manager
from ..core.unity_processor import UnityProcessor
from ..core.file_utils import validate_game_directory, find_backup_files, get_file_modified_date
from ..image_processing import pixelate_image, apply_black_shadows


class MainWindow:
    """Main application window for the Unofficial Retro Patch."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.setup_bindings()
        self.load_initial_state()
    
    def setup_window(self) -> None:
        """Setup the main window properties."""
        self.root.title("Unofficial Retro Patch")
        self.root.geometry("1280x840")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        self.set_window_icon()
    
    def set_window_icon(self) -> None:
        """Set the application icon."""
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
    
    def setup_variables(self) -> None:
        """Setup tkinter variables."""
        # Get available editions from config
        self.editions = config_manager.get_available_editions()
        if not self.editions:
            self.editions = ["Stronghold Definitive Edition", "Stronghold Crusader Definitive Edition"]
        
        self.selected_edition = tk.StringVar(value=self.editions[0])
        self.path_var = tk.StringVar()
        self.pixelation_var = tk.DoubleVar(value=0.5)
        self.black_shadows_var = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. If the GUI becomes unresponsive during pixelation, please wait until the operation completes.")
        
        # GUI state
        self.edition_images = []
        self.edition_buttons = []
        self.preview_image = None
        self.preview_pil = None
        self.progress_bar_visible = False
    
    def create_widgets(self) -> None:
        """Create all GUI widgets."""
        self.create_scrollable_container()
        self.create_left_column()
        self.create_right_column()
        self.create_footer()
    
    def create_scrollable_container(self) -> None:
        """Create the scrollable main container."""
        # Create a canvas and scrollbars for scrolling
        self.container = ttk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.container, borderwidth=0, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.hscroll = ttk.Scrollbar(self.container, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.vscroll.set, xscrollcommand=self.hscroll.set)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside the canvas
        self.main_frame = ttk.Frame(self.canvas, padding="10")
        self.main_frame_id = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.columnconfigure(0, weight=1, uniform="col")
        self.main_frame.columnconfigure(1, weight=1, uniform="col")
        self.main_frame.rowconfigure(0, weight=1)
        
        # Update scrollregion when the size of the frame changes
        def on_frame_configure(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.main_frame.bind("<Configure>", on_frame_configure)
        
        # Make sure the canvas resizes the frame width to match the canvas width
        def on_canvas_configure(event=None):
            self.canvas.itemconfig(self.main_frame_id, width=self.canvas.winfo_width())
        self.canvas.bind("<Configure>", on_canvas_configure)
        
        # Mousewheel scrolling
        def _on_mousewheel(event):
            if event.state & 0x1:  # Shift pressed for horizontal scroll
                self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel)
    
    def create_left_column(self) -> None:
        """Create the left column widgets."""
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.create_logo_description()
        self.create_edition_selection()
        self.create_game_path_section()
        self.create_backup_management()
    
    def create_logo_description(self) -> None:
        """Create the logo and description section."""
        logo_desc_frame = ttk.Frame(self.left_frame)
        logo_desc_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        logo_path = "assets/icon/urp-small.png" if os.path.exists("assets/icon/urp-small.png") else "assets/icon/urp.png"
        logo_image = PhotoImage(file=logo_path)
        self.logo_label = ttk.Label(logo_desc_frame, image=logo_image)
        self.logo_label.image = logo_image
        self.logo_label.pack(side=tk.LEFT, padx=(0, 10), pady=0)
        
        desc_text = ("The Unofficial Retro Patch applies a pixelated look to Stronghold,\n"
                     "giving it a more retro appearance that feels closer to the original game's art style.\n"
                     "This tool modifies the game's texture assets to create a nostalgic experience.\n\n"
                     "Stronghold Definitive Edition &\nStronghold Crusader Definitive Edition © Firefly Studios")
        
        self.description = ttk.Label(
            logo_desc_frame,
            text=desc_text,
            wraplength=1,  # will be set dynamically below
            justify="left",
            anchor="center",
        )
        self.description.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=0)
        
        # Dynamically set wraplength to half the window width minus logo width
        def update_desc_wrap(event=None):
            left_width = self.left_frame.winfo_width()
            logo_width = self.logo_label.winfo_width()
            pad = 40
            wrap = max(200, left_width - logo_width - pad)
            self.description.config(wraplength=wrap)
        
        self.left_frame.bind('<Configure>', update_desc_wrap)
        self.logo_label.bind('<Configure>', update_desc_wrap)
    
    def create_edition_selection(self) -> None:
        """Create the edition selection section."""
        edition_frame = ttk.Frame(self.left_frame)
        edition_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(edition_frame, text="Select Stronghold Version:").pack(side=tk.TOP, anchor=tk.W, padx=(0, 5))
        
        # Load edition images
        edition_image_paths = [
            "assets/firefly/shde.png",
            "assets/firefly/shcde.png"
        ]
        for path in edition_image_paths:
            if os.path.exists(path):
                img = Image.open(path)
                img.thumbnail((96, 48), Image.Resampling.LANCZOS)
                self.edition_images.append(ImageTk.PhotoImage(img))
            else:
                self.edition_images.append(None)
        
        edition_buttons_frame = ttk.Frame(edition_frame)
        edition_buttons_frame.pack(fill=tk.X)
        
        for idx, edition in enumerate(self.editions):
            btn = tk.Button(
                edition_buttons_frame,
                image=self.edition_images[idx] if idx < len(self.edition_images) else None,
                compound="top",
                command=lambda e=edition: self.select_edition(e),
                relief=tk.SUNKEN if self.selected_edition.get() == edition else tk.RAISED,
                width=1,
                height=60
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=5)
            self.edition_buttons.append(btn)
        
        edition_buttons_frame.columnconfigure(0, weight=1)
        edition_buttons_frame.columnconfigure(1, weight=1)
    
    def create_game_path_section(self) -> None:
        """Create the game path selection section."""
        self.path_frame = ttk.LabelFrame(self.left_frame, text="Game Installation", padding="10")
        self.path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.path_label = ttk.Label(
            self.path_frame, text=f"{self.selected_edition.get()} Installation Folder:"
        )
        self.path_label.pack(anchor=tk.W, padx=5)
        
        path_select_frame = ttk.Frame(self.path_frame)
        path_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.update_path_var_from_config()
        path_entry = ttk.Entry(path_select_frame, textvariable=self.path_var, width=30)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(
            path_select_frame, text="Browse", command=self.browse_game_path
        )
        browse_btn.pack(side=tk.RIGHT)
    
    def create_backup_management(self) -> None:
        """Create the backup management section."""
        backup_frame = ttk.LabelFrame(self.left_frame, text="Backup Management", padding="10")
        backup_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.backup_list = ttk.Treeview(
            backup_frame, columns=("file", "date"), show="headings"
        )
        self.backup_list.heading("file", text="Asset File")
        self.backup_list.heading("date", text="Backup Date")
        self.backup_list.column("file", width=180)
        self.backup_list.column("date", width=120)
        self.backup_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        
        scrollbar = ttk.Scrollbar(
            backup_frame, orient=tk.VERTICAL, command=self.backup_list.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backup_list.configure(yscrollcommand=scrollbar.set)
        
        backup_actions = ttk.Frame(self.left_frame, padding="5")
        backup_actions.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = ttk.Button(
            backup_actions, text="Refresh Backup List", command=self.refresh_backups
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        restore_btn = ttk.Button(
            backup_actions, text="Restore Selected Backup", command=self.restore_backup
        )
        restore_btn.pack(side=tk.LEFT)
    
    def create_right_column(self) -> None:
        """Create the right column widgets."""
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.create_preview_area()
        self.create_pixelation_controls()
        self.create_options_section()
    
    def create_preview_area(self) -> None:
        """Create the preview area."""
        preview_frame = ttk.LabelFrame(
            self.right_frame, 
            text="Preview (This just pixelates a screenshot, the actual game will look better)", 
            padding="10"
        )
        preview_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.preview_canvas = tk.Label(preview_frame)
        self.preview_canvas.pack(padx=5, pady=5)
    
    def create_pixelation_controls(self) -> None:
        """Create the pixelation amount controls."""
        pixelation_frame = ttk.LabelFrame(self.right_frame, text="Pixelation Amount", padding="10")
        pixelation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.pixelation_slider = ttk.Scale(
            pixelation_frame,
            from_=0.1,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.pixelation_var,
            command=self.update_preview
        )
        self.pixelation_slider.pack(fill=tk.X, padx=5, pady=5)
        
        self.pixelation_label = ttk.Label(pixelation_frame, text="Pixelation: 0.5")
        self.pixelation_label.pack(anchor=tk.CENTER)
    
    def create_options_section(self) -> None:
        """Create the options section."""
        options_frame = ttk.LabelFrame(self.right_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Black Shadows toggle
        self.black_shadows_checkbox = ttk.Checkbutton(
            options_frame,
            text="Black Shadows",
            variable=self.black_shadows_var,
            command=self.update_preview
        )
        self.black_shadows_checkbox.pack(anchor=tk.W, padx=5, pady=2)
        
        # Add a small note about black shadows
        black_shadows_note = ttk.Label(
            options_frame,
            text="(Replaces semi-transparent shadows with solid black in game textures)",
            font=("", 8),
            foreground="gray"
        )
        black_shadows_note.pack(anchor=tk.W, padx=5, pady=(0, 2))
    
    def create_footer(self) -> None:
        """Create the footer section."""
        footer = ttk.Frame(self.root, padding="5")
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(
            footer, variable=self.progress_var, mode='determinate'
        )
        
        # Console output/status
        status_bar = ttk.Label(
            footer, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Apply pixelation button (right side)
        footer_pixelate_btn = ttk.Button(
            footer, text="Apply Pixelation", command=self.apply_pixelation_threaded
        )
        footer_pixelate_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def setup_bindings(self) -> None:
        """Setup event bindings."""
        pass  # Bindings are set up in individual widget creation methods
    
    def load_initial_state(self) -> None:
        """Load the initial application state."""
        self.load_placeholder_image()
        self.update_preview()
        self.refresh_backups()
    
    def load_placeholder_image(self) -> None:
        """Load the placeholder image for preview."""
        edition = self.selected_edition.get()

        if edition == "Stronghold Definitive Edition":
            placeholder_path = "assets/firefly/shde-screenshot.jpg"
        elif edition == "Stronghold Crusader Definitive Edition":
            placeholder_path = "assets/firefly/shcde-screenshot.jpg"
        else:
            placeholder_path = "assets/firefly/shde-screenshot.jpg"

        if not os.path.exists(placeholder_path):
            messagebox.showerror(
                "Error", f"Placeholder image not found: {placeholder_path}"
            )
            return

        self.preview_pil = Image.open(placeholder_path)
    
    def update_preview(self, event=None) -> None:
        """Update the preview image."""
        value = self.pixelation_var.get()
        value = round(value, 2)

        self.pixelation_label.config(text=f"Pixelation: {value:.2f} (Recommended: 0.5)")

        # Apply pixelation to the placeholder image
        pil_img = pixelate_image(self.preview_pil, value)

        if self.black_shadows_var.get():
            pil_img = apply_black_shadows(pil_img)

        # Make preview square (crop to square center)
        width, height = pil_img.size
        side = min(width, height)
        left = (width - side) // 1.8
        top = (height - side) // 2
        right = left + side
        bottom = top + side
        pil_img = pil_img.crop((left, top, right, bottom))

        self.preview_image = ImageTk.PhotoImage(pil_img)
        self.preview_canvas.config(image=self.preview_image, width=560, height=480)
        self.preview_canvas.image = self.preview_image
    
    def select_edition(self, edition: str) -> None:
        """Select a game edition."""
        self.selected_edition.set(edition)
        for btn, ed in zip(self.edition_buttons, self.editions):
            btn.config(relief=tk.SUNKEN if ed == edition else tk.RAISED)
        self.path_label.config(text=f"{edition} Installation Folder:")
        self.update_path_var_from_config()
        self.refresh_backups()
        self.load_placeholder_image()
        self.update_preview()
    
    def update_path_var_from_config(self) -> None:
        """Update the path variable from configuration."""
        edition = self.selected_edition.get()
        try:
            config = config_manager.get_edition_config(edition)
            self.path_var.set(config.target_folder)
        except ValueError:
            self.path_var.set("")
    
    def browse_game_path(self) -> None:
        """Browse for game installation directory."""
        directory = filedialog.askdirectory(
            title=f"Select {self.selected_edition.get()} Installation Folder"
        )
        if directory:
            self.path_var.set(directory)
            if validate_game_directory(directory, self.selected_edition.get()):
                edition = self.selected_edition.get()
                config_manager.update_edition_path(edition, directory)
                self.status_var.set(f"Game path set to: {directory}")
                self.refresh_backups()
            else:
                messagebox.showerror(
                    "Invalid Directory",
                    f"The selected directory does not appear to be a valid {self.selected_edition.get()} installation.",
                )
                self.path_var.set("")
    
    def refresh_backups(self) -> None:
        """Refresh the backup file list."""
        for item in self.backup_list.get_children():
            self.backup_list.delete(item)
        
        game_path = self.path_var.get()
        if not game_path or not os.path.exists(game_path):
            return
        
        backup_files = find_backup_files(game_path)
        for backup_file in backup_files:
            relative_path = os.path.relpath(backup_file, game_path)
            backup_date = get_file_modified_date(backup_file)
            self.backup_list.insert("", "end", values=(relative_path, backup_date))
        
        if not backup_files:
            self.status_var.set("No backup files found")
        else:
            self.status_var.set(f"Found {len(backup_files)} backup files")
    
    def show_progress_bar(self) -> None:
        """Show the progress bar."""
        if not self.progress_bar_visible:
            self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            self.progress_bar_visible = True
    
    def hide_progress_bar(self) -> None:
        """Hide the progress bar."""
        if self.progress_bar_visible:
            self.progress_bar.pack_forget()
            self.progress_bar_visible = False
    
    def apply_pixelation_threaded(self) -> None:
        """Apply pixelation in a background thread."""
        def worker():
            game_path = self.path_var.get()
            if not game_path or not os.path.exists(game_path):
                self.root.after(0, lambda: self.status_var.set("Error: Please select a valid game installation path first."))
                return
            
            edition = self.selected_edition.get()
            config_manager.update_edition_path(edition, game_path)
            
            # Show progress bar and set initial status
            self.root.after(0, self.show_progress_bar)
            self.root.after(0, lambda: self.progress_var.set(0))
            self.root.after(0, lambda: self.status_var.set("Applying pixelation... This may take a while"))
            
            def gui_logger(msg):
                # Use root.after() for thread-safe GUI updates
                self.root.after(0, lambda: self.status_var.set(str(msg)))
                # Update progress based on message content with throttling
                if "Pixelating texture" in str(msg) and "/" in str(msg):
                    try:
                        # Extract progress from message like "Pixelating texture 1/5"
                        msg_str = str(msg)
                        # Find the part with numbers like "1/5"
                        import re
                        match = re.search(r'(\d+)/(\d+)', msg_str)
                        if match:
                            current, total = map(int, match.groups())
                            progress_percent = (current / total) * 100
                            # Throttle progress updates to every 5% or every texture if less than 20 total
                            if total <= 20 or current % max(1, total // 20) == 0 or current == total:
                                self.root.after(0, lambda: self.progress_var.set(progress_percent))
                    except:
                        pass  # If parsing fails, just continue
            
            try:
                # Get the black shadows option from the GUI
                black_shadows = self.black_shadows_var.get()
                
                # Create processor and apply pixelation
                processor = UnityProcessor(logger=gui_logger)
                files_to_replace = self.pixelate_edition(edition, processor, black_shadows)
                
                gc.collect()  # Run garbage collection to free memory
                time.sleep(1)  # Allow GUI to update before showing completion message
                self.root.after(0, lambda: self.status_var.set("Pixelation has been applied successfully!"))

                self.root.after(0, lambda: self.status_var.set("Replacing files..."))
                self.replace_files(files_to_replace, processor)
                self.root.after(0, lambda: self.status_var.set("Files replaced successfully!"))

                self.root.after(0, self.refresh_backups)
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"Failed to apply pixelation: {str(e)}"))
            finally:
                # Hide progress bar and reset status after a delay
                def cleanup():
                    self.root.after(0, self.hide_progress_bar)
                    self.root.after(0, lambda: self.status_var.set("Ready"))
                self.root.after(1000, cleanup)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def pixelate_edition(self, edition_name: str, processor: UnityProcessor, black_shadows: bool = False):
        """Pixelate a specific edition."""
        config = config_manager.get_edition_config(edition_name)
        
        # Validate paths
        errors = config_manager.validate_edition_paths(config)
        if errors:
            raise FileNotFoundError(f"Configuration errors: {'; '.join(errors)}")
        
        if len(config.pixelate_files) == 0:
            processor.logger(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {edition_name}.")
            return []
        
        # Group files by asset file
        pixelate_asset_files = processor.group_pixelate_files(
            config.pixelate_files, 
            config.target_folder, 
            config.assets_folder, 
            config.masks_folder
        )
        
        # Calculate total textures for progress tracking
        total_textures = sum(len(entries) for entries in pixelate_asset_files.values())
        processor.logger(f"[UNOFFICIAL RETRO PATCH] Total textures to process: {total_textures}")
        
        files_to_replace = []
        processed_total = 0
        
        for asset_file, pixelate_entries in pixelate_asset_files.items():
            try:
                processed_count, temp_file = processor.process_asset_file(
                    asset_file, 
                    pixelate_entries, 
                    config.resize_amount, 
                    black_shadows, 
                    config.debug_pixelated_folder
                )
                
                if temp_file:
                    files_to_replace.append((asset_file, temp_file))
                
                processed_total += processed_count
                
            except Exception as e:
                processor.logger(f"[UNOFFICIAL RETRO PATCH] Failed to process asset file '{asset_file}': {e}")
                continue
        
        return files_to_replace
    
    def replace_files(self, files_to_replace, processor: UnityProcessor):
        """Replace files with their modified versions."""
        processor.logger(f"[UNOFFICIAL RETRO PATCH] Processing {len(files_to_replace)} file replacements...")
        
        for original_file, temp_file in files_to_replace:
            success = processor.replace_file(original_file, temp_file)
            if not success:
                processor.logger(f"[UNOFFICIAL RETRO PATCH] Failed to replace {original_file}")
    
    def restore_backup(self) -> None:
        """Restore a selected backup."""
        selected_items = self.backup_list.selection()
        if not selected_items:
            messagebox.showinfo(
                "No Selection", "Please select a backup file to restore."
            )
            return
        
        item = self.backup_list.item(selected_items[0])
        relative_path = item["values"][0]
        game_path = self.path_var.get()
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