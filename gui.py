import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, PhotoImage
import configparser
from PIL import Image, ImageTk
from main import pixelate_edition
import threading


class RetroPixelatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unofficial Retro Patch")
        self.root.resizable(True, True)

        # Set the window icon
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

        # Load configuration
        self.config = configparser.ConfigParser()
        if os.path.exists("config.ini"):
            self.config.read("config.ini")

        # Get available editions from config
        self.editions = [section for section in self.config.sections()]
        if not self.editions:
            self.editions = ["Stronghold Definitive Edition", "Stronghold Crusader Definitive Edition"]
        self.selected_edition = tk.StringVar(value=self.editions[0])

        # Main container frame (now using grid for two columns)
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1, uniform="col")
        main_frame.columnconfigure(1, weight=1, uniform="col")
        main_frame.rowconfigure(0, weight=1)

        # LEFT COLUMN FRAME
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # RIGHT COLUMN FRAME
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- LEFT COLUMN ---
        # Logo (smaller if available)
        logo_path = "assets/icon/urp-small.png" if os.path.exists("assets/icon/urp-small.png") else "assets/icon/urp.png"
        logo_image = PhotoImage(file=logo_path)
        logo_label = ttk.Label(left_frame, image=logo_image)
        logo_label.image = logo_image
        logo_label.pack(pady=(0, 5))

        # Description
        desc_text = ("The Unofficial Retro Patch applies a pixelated look to Stronghold,\n"
                     "giving it a more retro appearance that feels closer to the original game's art style.\n"
                     "This tool modifies the game's texture assets to create a nostalgic experience.\n\n"
                     "Stronghold Definitive Edition & Stronghold Crusader Definitive Edition Logos © Firefly Studios")
        description = ttk.Label(
            left_frame,
            text=desc_text,
            wraplength=300,
            justify="left",
            anchor="center",
        )
        description.pack(fill=tk.X, padx=5, pady=5)

        # Edition selection
        edition_frame = ttk.Frame(left_frame)
        edition_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(edition_frame, text="Select Stronghold Version:").pack(side=tk.TOP, anchor=tk.W, padx=(0, 5))
        self.edition_images = []
        edition_image_paths = [
            "assets/firefly/shde.png",
            "assets/firefly/shcde.png"
        ]
        for path in edition_image_paths:
            if os.path.exists(path):
                img = Image.open(path)
                img.thumbnail((96,48), Image.Resampling.LANCZOS)
                self.edition_images.append(ImageTk.PhotoImage(img))
            else:
                self.edition_images.append(None)
        self.edition_buttons = []
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

        # Game path section
        self.path_frame = ttk.LabelFrame(left_frame, text="Game Installation", padding="10")
        self.path_frame.pack(fill=tk.X, padx=5, pady=5)
        self.path_label = ttk.Label(
            self.path_frame, text=f"{self.selected_edition.get()} Installation Folder:"
        )
        self.path_label.pack(anchor=tk.W, padx=5)
        path_select_frame = ttk.Frame(self.path_frame)
        path_select_frame.pack(fill=tk.X, padx=5, pady=5)
        self.path_var = tk.StringVar()
        self.update_path_var_from_config()
        path_entry = ttk.Entry(path_select_frame, textvariable=self.path_var, width=30)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        browse_btn = ttk.Button(
            path_select_frame, text="Browse", command=self.browse_game_path
        )
        browse_btn.pack(side=tk.RIGHT)

        # --- RIGHT COLUMN ---
        # Preview area
        preview_frame = ttk.LabelFrame(right_frame, text="Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        self.preview_canvas = tk.Label(preview_frame)
        self.preview_canvas.pack(padx=5, pady=5)
        self.preview_image = None
        self.preview_pil = None
        self.load_placeholder_image()
        self.update_preview()

        # Pixelation amount slider
        pixelation_frame = ttk.LabelFrame(right_frame, text="Pixelation Amount", padding="10")
        pixelation_frame.pack(fill=tk.X, padx=5, pady=5)
        self.pixelation_var = tk.DoubleVar(value=0.5)
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

        # Backup management section
        backup_frame = ttk.LabelFrame(right_frame, text="Backup Management", padding="10")
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
        backup_actions = ttk.Frame(right_frame, padding="5")
        backup_actions.pack(fill=tk.X, padx=5, pady=5)
        refresh_btn = ttk.Button(
            backup_actions, text="Refresh Backup List", command=self.refresh_backups
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        restore_btn = ttk.Button(
            backup_actions, text="Restore Selected Backup", command=self.restore_backup
        )
        restore_btn.pack(side=tk.LEFT)

        # --- FOOTER ---
        footer = ttk.Frame(root, padding="5")
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        # Console output/status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. If the GUI becomes unresponsive during pixelation, please wait until the operation completes.")
        status_bar = ttk.Label(
            footer, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        # Restore backup button
        footer_restore_btn = ttk.Button(
            footer, text="Restore Backup", command=self.restore_backup
        )
        footer_restore_btn.pack(side=tk.RIGHT, padx=(5, 0))
        # Apply pixelation button
        footer_pixelate_btn = ttk.Button(
            footer, text="Apply Pixelation", command=self.apply_pixelation_threaded
        )
        footer_pixelate_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Load backup list if path already set
        if self.path_var.get():
            self.refresh_backups()

    def load_placeholder_image(self):
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

    def update_preview(self, event=None):
        value = self.pixelation_var.get()
        # Adapt value to be rounded to two decimal places
        value = round(value, 2)

        self.pixelation_label.config(text=f"Pixelation: {value:.2f} (Recommended: 0.5)")

        # Apply pixelation to the placeholder image
        from pixelation import pixelate_image
        pil_img = pixelate_image(self.preview_pil, value)

        # Zoom into the center of the image
        width, height = pil_img.size
        pixel_offset = int(0.5 * min(width, height))
        left = (width - pixel_offset) // 2
        top = (height - pixel_offset) // 2
        right = left + pixel_offset
        bottom = top + pixel_offset
        pil_img = pil_img.crop((left, top, right, bottom))

        # Resize to fit the preview canvas
        self.preview_image = ImageTk.PhotoImage(pil_img)
        self.preview_canvas.config(image=self.preview_image, width=720, height=360)
        self.preview_canvas.image = self.preview_image

    def select_edition(self, edition):
        self.selected_edition.set(edition)
        for btn, ed in zip(self.edition_buttons, self.editions):
            btn.config(relief=tk.SUNKEN if ed == edition else tk.RAISED)
        self.path_label.config(text=f"{edition} Installation Folder:")
        self.update_path_var_from_config()
        self.refresh_backups()
        self.load_placeholder_image()
        self.update_preview()

    def update_path_var_from_config(self):
        edition = self.selected_edition.get()
        if self.config.has_section(edition):
            target_folder = self.config.get(
                edition, "target_folder", fallback=""
            )
            self.path_var.set(target_folder)
        else:
            self.path_var.set("")

    def on_edition_change(self, event=None):
        # Update label and path field
        self.path_label.config(text=f"{self.selected_edition.get()} Installation Folder:")
        self.update_path_var_from_config()
        self.refresh_backups()

    def browse_game_path(self):
        directory = filedialog.askdirectory(
            title=f"Select {self.selected_edition.get()} Installation Folder"
        )
        if directory:
            self.path_var.set(directory)
            if self.validate_game_directory(directory):
                edition = self.selected_edition.get()
                if not self.config.has_section(edition):
                    self.config.add_section(edition)
                self.config.set(
                    edition, "target_folder", directory
                )
                with open("config.ini", "w") as configfile:
                    self.config.write(configfile)
                self.status_var.set(f"Game path set to: {directory}")
                self.refresh_backups()
            else:
                messagebox.showerror(
                    "Invalid Directory",
                    f"The selected directory does not appear to be a valid {self.selected_edition.get()} installation.",
                )
                self.path_var.set("")

    def validate_game_directory(self, directory):
        # This could be improved to check for each edition's expected files
        edition = self.selected_edition.get()
        if edition == "Stronghold Definitive Edition":
            exe_path = os.path.join(directory, "Stronghold 1 Definitive Edition.exe")
            data_folder = os.path.join(directory, "Stronghold 1 Definitive Edition_Data")
        elif edition == "Stronghold Crusader Definitive Edition":
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
        if (exe_path and os.path.exists(exe_path)) or (data_folder and os.path.isdir(data_folder)):
            return True
        return False

    def refresh_backups(self):
        for item in self.backup_list.get_children():
            self.backup_list.delete(item)
        game_path = self.path_var.get()
        if not game_path or not os.path.exists(game_path):
            return
        backup_files = []
        for root, _, files in os.walk(game_path):
            for file in files:
                if file.endswith(".backup001") or ".backup" in file:
                    backup_files.append(os.path.join(root, file))
        for backup_file in backup_files:
            relative_path = os.path.relpath(backup_file, game_path)
            backup_date = self.get_file_modified_date(backup_file)
            self.backup_list.insert("", "end", values=(relative_path, backup_date))
        if not backup_files:
            self.status_var.set("No backup files found")
        else:
            self.status_var.set(f"Found {len(backup_files)} backup files")

    def get_file_modified_date(self, file_path):
        try:
            mod_time = os.path.getmtime(file_path)
            from datetime import datetime
            return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Unknown"

    def apply_pixelation_threaded(self):
        # Run pixelation in a background thread to keep GUI responsive
        def worker():
            game_path = self.path_var.get()
            if not game_path or not os.path.exists(game_path):
                self.status_var.set("Error: Please select a valid game installation path first.")
                return
            edition = self.selected_edition.get()
            if not self.config.has_section(edition):
                self.config.add_section(edition)
            self.config.set(edition, "target_folder", game_path)
            with open("config.ini", "w") as configfile:
                self.config.write(configfile)
            self.status_var.set("Applying pixelation... This may take a while")
            try:
                pixelate_edition(edition)
                self.status_var.set("Pixelation has been applied successfully!")
                self.refresh_backups()
            except Exception as e:
                self.status_var.set(f"Failed to apply pixelation: {str(e)}")
            finally:
                self.root.after(1000, lambda: self.status_var.set("Ready"))
        threading.Thread(target=worker, daemon=True).start()

    def restore_backup(self):
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

def main():
    root = tk.Tk()
    app = RetroPixelatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
