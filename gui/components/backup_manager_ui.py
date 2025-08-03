"""
Backup manager UI component for the GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Callable, Optional
import os


class BackupManagerUI:
    """UI component for managing backups."""
    
    def __init__(
        self, 
        parent: tk.Widget, 
        on_refresh: Optional[Callable] = None,
        on_restore: Optional[Callable] = None
    ):
        self.parent = parent
        self.on_refresh = on_refresh
        self.on_restore = on_restore
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the backup manager UI widgets."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Backup Management", padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Backup list frame
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        
        # Backup list
        self.backup_list = ttk.Treeview(
            list_frame, columns=("file", "date"), show="headings"
        )
        self.backup_list.heading("file", text="Asset File")
        self.backup_list.heading("date", text="Backup Date")
        self.backup_list.column("file", width=180)
        self.backup_list.column("date", width=120)
        self.backup_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.backup_list.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.backup_list.configure(yscrollcommand=scrollbar.set)
        
        # Actions frame
        actions_frame = ttk.Frame(self.parent, padding="5")
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            actions_frame, text="Refresh Backup List", command=self._refresh_backups
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Restore button
        self.restore_btn = ttk.Button(
            actions_frame, text="Restore Selected Backup", command=self._restore_backup
        )
        self.restore_btn.pack(side=tk.LEFT)
    
    def _refresh_backups(self):
        """Refresh the backup list."""
        if self.on_refresh:
            self.on_refresh()
    
    def _restore_backup(self):
        """Restore the selected backup."""
        selected_items = self.backup_list.selection()
        if not selected_items:
            messagebox.showinfo(
                "No Selection", "Please select a backup file to restore."
            )
            return
        
        item = self.backup_list.item(selected_items[0])
        relative_path = item["values"][0]
        
        if self.on_restore:
            self.on_restore(relative_path)
    
    def clear_backups(self):
        """Clear the backup list."""
        for item in self.backup_list.get_children():
            self.backup_list.delete(item)
    
    def add_backup(self, relative_path: str, backup_date: str):
        """Add a backup to the list."""
        self.backup_list.insert("", "end", values=(relative_path, backup_date))
    
    def get_selected_backup(self) -> Optional[str]:
        """Get the selected backup path."""
        selected_items = self.backup_list.selection()
        if selected_items:
            item = self.backup_list.item(selected_items[0])
            return item["values"][0]
        return None
    
    def set_refresh_callback(self, callback: Callable):
        """Set the refresh callback."""
        self.on_refresh = callback
    
    def set_restore_callback(self, callback: Callable):
        """Set the restore callback."""
        self.on_restore = callback
    
    def update_backups(self, backups: List[Dict]):
        """Update the backup list with new data."""
        self.clear_backups()
        
        for backup in backups:
            self.add_backup(backup.get('file', ''), backup.get('date', ''))
    
    def show_message(self, message: str, message_type: str = "info"):
        """Show a message to the user."""
        if message_type == "error":
            messagebox.showerror("Error", message)
        elif message_type == "warning":
            messagebox.showwarning("Warning", message)
        else:
            messagebox.showinfo("Information", message)