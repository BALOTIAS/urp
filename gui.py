import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, PhotoImage
import configparser
from PIL import Image, ImageTk
from main import pixelate_edition


class RetroPixelatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Unofficial Retro Patch")
        self.root.resizable(True, True)

        # Set the window icon
        try:
            # If running as frozen executable, use the included icon
            if getattr(sys, "frozen", False):
                application_path = sys._MEIPASS
                ico_path = os.path.join(
                    application_path,
                    "assets/icon",
                    "urp.ico" if sys.platform == "win32" else "urp.png",
                )
            else:
                # Use the icon in the project folder
                ico_path = os.path.join(
                    "assets/icon", "urp.ico" if sys.platform == "win32" else "urp.png"
                )

            if os.path.exists(ico_path):
                # For Windows
                if sys.platform == "win32":
                    self.root.iconbitmap(ico_path)
                # For macOS and Linux
                else:
                    icon_img = tk.PhotoImage(file=ico_path)
                    self.root.iconphoto(True, icon_img)
        except Exception as e:
            print(f"Could not set application icon: {e}")

        # Load configuration
        self.config = configparser.ConfigParser()
        if os.path.exists("config.ini"):
            self.config.read("config.ini")

        # Main container frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo section
        logo_image = PhotoImage(file="assets/icon/urp.png")
        logo_label = ttk.Label(main_frame, image=logo_image)
        logo_label.image = logo_image

        # Description section
        desc_frame = ttk.Frame(main_frame, padding="10")
        desc_frame.pack(fill=tk.X, padx=5, pady=5)

        desc_text = """The Unofficial Retro Patch applies a pixelated look to Stronghold Definitive Edition,
giving it a more retro appearance that feels closer to the original game's art style.
This tool modifies the game's texture assets to create a nostalgic experience."""

        description = ttk.Label(
            desc_frame,
            image=logo_image,
            text=desc_text,
            wraplength=550,
            justify="left",
            anchor="center",
            compound="left",
        )
        description.pack(fill=tk.X, padx=5, pady=5)

        # Game path section
        path_frame = ttk.LabelFrame(main_frame, text="Game Installation", padding="10")
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        path_label = ttk.Label(
            path_frame, text="Stronghold Definitive Edition Installation Folder:"
        )
        path_label.pack(anchor=tk.W, padx=5)

        path_select_frame = ttk.Frame(path_frame)
        path_select_frame.pack(fill=tk.X, padx=5, pady=5)

        self.path_var = tk.StringVar()
        if self.config.has_section("Stronghold Definitive Edition"):
            target_folder = self.config.get(
                "Stronghold Definitive Edition", "target_folder", fallback=""
            )
            self.path_var.set(target_folder)

        path_entry = ttk.Entry(path_select_frame, textvariable=self.path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        browse_btn = ttk.Button(
            path_select_frame, text="Browse", command=self.browse_game_path
        )
        browse_btn.pack(side=tk.RIGHT)

        # Actions section
        actions_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Pixelate button
        pixelate_btn = ttk.Button(
            actions_frame, text="Apply Pixelation", command=self.apply_pixelation
        )
        pixelate_btn.pack(fill=tk.X, padx=5, pady=5)

        # Backup management section
        backup_frame = ttk.LabelFrame(
            actions_frame, text="Backup Management", padding="10"
        )
        backup_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.backup_list = ttk.Treeview(
            backup_frame, columns=("file", "date"), show="headings"
        )
        self.backup_list.heading("file", text="Asset File")
        self.backup_list.heading("date", text="Backup Date")
        self.backup_list.column("file", width=250)
        self.backup_list.column("date", width=200)
        self.backup_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))

        # Add scrollbar to the backup list
        scrollbar = ttk.Scrollbar(
            backup_frame, orient=tk.VERTICAL, command=self.backup_list.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backup_list.configure(yscrollcommand=scrollbar.set)

        # Backup actions frame
        backup_actions = ttk.Frame(actions_frame, padding="5")
        backup_actions.pack(fill=tk.X, padx=5, pady=5)

        refresh_btn = ttk.Button(
            backup_actions, text="Refresh Backup List", command=self.refresh_backups
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))

        restore_btn = ttk.Button(
            backup_actions, text="Restore Selected Backup", command=self.restore_backup
        )
        restore_btn.pack(side=tk.LEFT)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load backup list if path already set
        if self.path_var.get():
            self.refresh_backups()

    def browse_game_path(self):
        directory = filedialog.askdirectory(
            title="Select Stronghold Definitive Edition Installation Folder"
        )
        if directory:
            self.path_var.set(directory)

            # Check if the selected directory looks like a Stronghold DE installation
            if self.validate_game_directory(directory):
                # Save to config
                if not self.config.has_section("Stronghold Definitive Edition"):
                    self.config.add_section("Stronghold Definitive Edition")
                self.config.set(
                    "Stronghold Definitive Edition", "target_folder", directory
                )

                with open("config.ini", "w") as configfile:
                    self.config.write(configfile)

                self.status_var.set(f"Game path set to: {directory}")
                self.refresh_backups()
            else:
                messagebox.showerror(
                    "Invalid Directory",
                    "The selected directory does not appear to be a valid Stronghold Definitive Edition installation.",
                )
                self.path_var.set("")

    def validate_game_directory(self, directory):
        # Check for some expected files/folders to validate it's a Stronghold DE installation
        exe_path = os.path.join(directory, "Stronghold 1 Definitive Edition.exe")
        data_folder = os.path.join(directory, "Stronghold 1 Definitive Edition_Data")

        if os.path.exists(exe_path) or os.path.isdir(data_folder):
            return True
        return False

    def refresh_backups(self):
        # Clear current list
        for item in self.backup_list.get_children():
            self.backup_list.delete(item)

        game_path = self.path_var.get()
        if not game_path or not os.path.exists(game_path):
            return

        # Recursively find all backup files
        backup_files = []
        for root, _, files in os.walk(game_path):
            for file in files:
                if file.endswith(".backup001") or ".backup" in file:
                    backup_files.append(os.path.join(root, file))

        # Add to list with file info
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

    def apply_pixelation(self):
        game_path = self.path_var.get()
        if not game_path or not os.path.exists(game_path):
            messagebox.showerror(
                "Error", "Please select a valid game installation path first."
            )
            return

        # Update config with the correct path
        if not self.config.has_section("Stronghold Definitive Edition"):
            self.config.add_section("Stronghold Definitive Edition")

        self.config.set("Stronghold Definitive Edition", "target_folder", game_path)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

        # Run pixelation in a separate thread to avoid freezing UI
        self.status_var.set("Applying pixelation... This may take a while")
        self.root.update()

        try:
            # Run pixelation
            pixelate_edition("Stronghold Definitive Edition")
            messagebox.showinfo("Success", "Pixelation has been applied successfully!")
            # Refresh backup list
            self.refresh_backups()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply pixelation: {str(e)}")
        finally:
            self.status_var.set("Ready")

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

        # Get the original file path by removing .backup### suffix
        import re

        original_file = re.sub(r"\.backup\d{3}$", "", backup_file)

        if not os.path.exists(backup_file):
            messagebox.showerror("Error", f"Backup file not found: {backup_file}")
            return

        try:
            # Create a temporary backup of current file if it exists
            if os.path.exists(original_file):
                os.rename(original_file, original_file + ".tmp")

            # Restore the backup
            os.rename(backup_file, original_file)

            # Remove the temporary file
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
