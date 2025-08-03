"""
Backup management for the Unofficial Retro Patch.
"""

import os
import warnings
from typing import List, Tuple, Optional, Callable
from .file_utils import FileUtils


class BackupManager:
    """Handles backup and restore operations."""
    
    def __init__(self, logger: Optional[Callable] = None):
        self.logger = logger or print
    
    def replace_files(self, files_to_replace: List[Tuple[str, str]]) -> None:
        """Replace original files with modified temporary files."""
        self.logger(f"[UNOFFICIAL RETRO PATCH] Processing {len(files_to_replace)} file replacements...")
        
        for original_file, temp_file in files_to_replace:
            # Wait for file to be unlocked
            if not FileUtils.wait_for_file_unlock(original_file, logger=self.logger):
                continue
            
            try:
                # Create backup
                backup_file = FileUtils.create_backup(original_file, self.logger)
                
                # Replace original with modified file
                self.logger(f"[UNOFFICIAL RETRO PATCH] Replacing original with modified file: {temp_file} -> {original_file}")
                os.rename(temp_file, original_file)
                
                self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully replaced asset file: {original_file}")
                
            except Exception as e:
                warnings.warn(f"Failed to replace asset file '{original_file}': {e}")
                # Try to restore original if backup was created
                if os.path.exists(backup_file) and not os.path.exists(original_file):
                    try:
                        os.rename(backup_file, original_file)
                        self.logger(f"[UNOFFICIAL RETRO PATCH] Restored original file from backup: {original_file}")
                    except Exception as restore_e:
                        warnings.warn(f"Failed to restore original file '{original_file}': {restore_e}")
    
    def find_backups_in_directory(self, directory: str) -> List[str]:
        """Find all backup files in a directory."""
        return FileUtils.find_backup_files(directory)
    
    def get_backup_info(self, backup_file: str, base_directory: str) -> Tuple[str, str]:
        """Get backup file information."""
        relative_path = os.path.relpath(backup_file, base_directory)
        backup_date = FileUtils.get_file_modified_date(backup_file)
        return relative_path, backup_date
    
    def restore_backup(self, backup_file: str, original_file: str) -> bool:
        """Restore a backup file to its original location."""
        try:
            if os.path.exists(original_file):
                os.rename(original_file, original_file + ".tmp")
            
            os.rename(backup_file, original_file)
            
            if os.path.exists(original_file + ".tmp"):
                os.remove(original_file + ".tmp")
            
            self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully restored: {os.path.basename(backup_file)}")
            return True
            
        except Exception as e:
            warnings.warn(f"Failed to restore backup: {str(e)}")
            return False