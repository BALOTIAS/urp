"""
File utility functions for handling file operations, backups, and file locking.
"""

import os
import time
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from ..config.settings import settings


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def is_file_locked(filepath: str) -> bool:
        """Check if a file is locked by another process.
        
        Args:
            filepath: Path to the file to check.
            
        Returns:
            True if file is locked, False otherwise.
        """
        try:
            with open(filepath, 'r+b'):
                return False
        except (PermissionError, OSError):
            return True
    
    @staticmethod
    def wait_for_file_unlock(filepath: str, max_wait: Optional[int] = None) -> bool:
        """Wait for a file to become unlocked.
        
        Args:
            filepath: Path to the file to wait for.
            max_wait: Maximum wait time in seconds. Defaults to settings.MAX_FILE_LOCK_WAIT_SECONDS.
            
        Returns:
            True if file was unlocked, False if timeout reached.
        """
        max_wait = max_wait or settings.MAX_FILE_LOCK_WAIT_SECONDS
        wait_time = 0
        
        while FileUtils.is_file_locked(filepath) and wait_time < max_wait:
            time.sleep(settings.FILE_LOCK_CHECK_INTERVAL)
            wait_time += settings.FILE_LOCK_CHECK_INTERVAL
        
        return not FileUtils.is_file_locked(filepath)
    
    @staticmethod
    def create_backup(filepath: str) -> Optional[str]:
        """Create a backup of a file.
        
        Args:
            filepath: Path to the file to backup.
            
        Returns:
            Path to the backup file, or None if backup failed.
        """
        if not os.path.exists(filepath):
            return None
        
        backup_no = 1
        backup_file = f"{filepath}{settings.BACKUP_EXTENSION}{backup_no:03}"
        
        while os.path.exists(backup_file):
            backup_no += 1
            backup_file = f"{filepath}{settings.BACKUP_EXTENSION}{backup_no:03}"
        
        try:
            shutil.copy2(filepath, backup_file)
            return backup_file
        except Exception:
            return None
    
    @staticmethod
    def restore_backup(backup_file: str, original_file: str) -> bool:
        """Restore a file from backup.
        
        Args:
            backup_file: Path to the backup file.
            original_file: Path to the original file.
            
        Returns:
            True if restore was successful, False otherwise.
        """
        if not os.path.exists(backup_file):
            return False
        
        try:
            if os.path.exists(original_file):
                os.remove(original_file)
            shutil.copy2(backup_file, original_file)
            return True
        except Exception:
            return False
    
    @staticmethod
    def find_backup_files(directory: str) -> List[Tuple[str, str]]:
        """Find all backup files in a directory.
        
        Args:
            directory: Directory to search for backup files.
            
        Returns:
            List of tuples containing (backup_file, original_file).
        """
        backup_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if settings.BACKUP_EXTENSION in file:
                    backup_path = os.path.join(root, file)
                    # Extract original filename from backup filename
                    original_file = backup_path.replace(settings.BACKUP_EXTENSION, "")
                    backup_files.append((backup_path, original_file))
        
        return backup_files
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Path to the directory.
            
        Returns:
            True if directory exists or was created, False otherwise.
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_size_mb(filepath: str) -> float:
        """Get file size in megabytes.
        
        Args:
            filepath: Path to the file.
            
        Returns:
            File size in megabytes.
        """
        if not os.path.exists(filepath):
            return 0.0
        
        return os.path.getsize(filepath) / (1024 * 1024)
    
    @staticmethod
    def get_file_modified_date(filepath: str) -> Optional[str]:
        """Get the modified date of a file as a formatted string.
        
        Args:
            filepath: Path to the file.
            
        Returns:
            Formatted date string, or None if file doesn't exist.
        """
        if not os.path.exists(filepath):
            return None
        
        try:
            from datetime import datetime
            mod_time = os.path.getmtime(filepath)
            return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "Unknown"