"""
File utilities for the Unofficial Retro Patch.
"""

import os
import time
import warnings
from typing import List, Tuple, Optional, Callable
from pathlib import Path


class FileUtils:
    """Handles file operations and validation."""
    
    @staticmethod
    def is_file_locked(filepath: str) -> bool:
        """Check if file is locked by another process."""
        try:
            with open(filepath, 'r+b'):
                return False
        except (PermissionError, OSError):
            return True
    
    @staticmethod
    def wait_for_file_unlock(filepath: str, max_wait: int = 30, logger: Optional[Callable] = None) -> bool:
        """Wait for a file to become unlocked."""
        if logger is None:
            logger = print
        
        wait_time = 0
        while FileUtils.is_file_locked(filepath) and wait_time < max_wait:
            logger(f"[UNOFFICIAL RETRO PATCH] File locked, waiting... ({wait_time}s)")
            time.sleep(2)
            wait_time += 2
        
        if FileUtils.is_file_locked(filepath):
            warnings.warn(f"File still locked after {max_wait}s: {filepath}")
            return False
        
        return True
    
    @staticmethod
    def validate_directory_exists(directory: str, description: str = "Directory") -> None:
        """Validate that a directory exists."""
        if not os.path.exists(directory):
            raise FileNotFoundError(f"{description} '{directory}' does not exist.")
    
    @staticmethod
    def validate_file_exists(filepath: str, description: str = "File") -> None:
        """Validate that a file exists."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"{description} '{filepath}' does not exist.")
    
    @staticmethod
    def create_backup(filepath: str, logger: Optional[Callable] = None) -> str:
        """Create a backup of a file and return the backup path."""
        if logger is None:
            logger = print
        
        backup_no = 1
        backup_file = f"{filepath}.backup{backup_no:03}"
        
        while os.path.exists(backup_file):
            backup_no += 1
            backup_file = f"{filepath}.backup{backup_no:03}"
        
        logger(f"[UNOFFICIAL RETRO PATCH] Creating backup: {filepath} -> {backup_file}")
        os.rename(filepath, backup_file)
        
        return backup_file
    
    @staticmethod
    def restore_latest_backup(filepath: str, logger: Optional[Callable] = None) -> Optional[str]:
        """Restore the latest backup if it exists."""
        if logger is None:
            logger = print
        
        backup_no = 1
        backup_file = f"{filepath}.backup{backup_no:03}"
        latest_backup = None
        
        while os.path.exists(backup_file):
            latest_backup = backup_file
            backup_no += 1
            backup_file = f"{filepath}.backup{backup_no:03}"
        
        if latest_backup:
            logger(f"[UNOFFICIAL RETRO PATCH] Restoring latest backup before pixelation: {latest_backup}")
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(latest_backup, filepath)
        
        return latest_backup
    
    @staticmethod
    def find_backup_files(directory: str) -> List[str]:
        """Find all backup files in a directory and subdirectories."""
        backup_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".backup001") or ".backup" in file:
                    backup_files.append(os.path.join(root, file))
        return backup_files
    
    @staticmethod
    def get_file_modified_date(file_path: str) -> str:
        """Get the modified date of a file as a formatted string."""
        try:
            mod_time = os.path.getmtime(file_path)
            from datetime import datetime
            return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return "Unknown"
    
    @staticmethod
    def group_files_by_directory(files: List[str], target_folder: str, assets_folder: str) -> dict:
        """Group files by their directory for processing."""
        grouped_files = {}
        
        for file_path in files:
            asset_dir = os.path.dirname(file_path)
            asset_file = os.path.join(target_folder, assets_folder, asset_dir)
            
            if not os.path.exists(asset_file):
                warnings.warn(
                    f"[UNOFFICIAL RETRO PATCH] Asset file directory '{asset_file}' does not exist. Skipping pixelation for {file_path}."
                )
                continue
            
            pixelate_file = os.path.basename(file_path)
            name, extension = os.path.splitext(pixelate_file)
            
            if asset_file not in grouped_files:
                grouped_files[asset_file] = []
            
            grouped_files[asset_file].append({
                "asset_dir": asset_dir,
                "asset": pixelate_file,
                "asset_name": name,
                "asset_ext": extension,
                "mask_file": os.path.join(
                    "assets/masks", f"{asset_dir}/{pixelate_file}"
                ),
            })
        
        return grouped_files
    
    @staticmethod
    def save_temp_file(env, asset_file: str, logger: Optional[Callable] = None) -> Tuple[str, str]:
        """Save a Unity environment to a temporary file."""
        if logger is None:
            logger = print
        
        modified_asset_file = asset_file + ".tmp"
        
        try:
            logger(f"[UNOFFICIAL RETRO PATCH] Saving modified asset file to: {modified_asset_file}")
            with open(modified_asset_file, "wb") as f:
                f.write(env.file.save())
            
            # Verify the temp file was created
            if os.path.exists(modified_asset_file):
                file_size = os.path.getsize(modified_asset_file)
                logger(f"[UNOFFICIAL RETRO PATCH] Temporary file created: {modified_asset_file} ({file_size} bytes)")
                return asset_file, modified_asset_file
            else:
                raise Exception("Temporary file was not created")
                
        except Exception as e:
            warnings.warn(f"Failed to save modified asset file '{asset_file}': {e}")
            raise