"""
Main processor for the Unofficial Retro Patch.

This module orchestrates the pixelation process using the new modular structure.
"""

import os
from typing import Optional, Callable
from .config_manager import ConfigManager
from .asset_processor import AssetProcessor
from .backup_manager import BackupManager
from utils.memory_utils import MemoryUtils
from unitypy_fixes import patch_unitypy


class MainProcessor:
    """Main processor that orchestrates the pixelation process."""
    
    def __init__(self, logger: Optional[Callable] = None):
        self.logger = logger or print
        self.config_manager = ConfigManager()
        self.backup_manager = BackupManager(logger)
        
        # Apply UnityPy patches
        patch_unitypy()
    
    def pixelate_edition(
        self, 
        edition_name: str, 
        resize_amount: Optional[float] = None,
        black_shadows: bool = False
    ) -> None:
        """Pixelate a specific edition."""
        try:
            # Get edition configuration
            config = self.config_manager.get_edition_config(edition_name)
            
            # Override resize amount from environment if available
            if resize_amount is None:
                env_resize = self.config_manager.get_edition_environment_value(edition_name, "RESIZE_AMOUNT")
                if env_resize:
                    resize_amount = float(env_resize)
                else:
                    resize_amount = config.resize_amount
            
            # Override black shadows from environment if available
            env_black_shadows = self.config_manager.get_edition_environment_value(edition_name, "BLACK_SHADOWS")
            if env_black_shadows:
                black_shadows = env_black_shadows.lower() in ("true", "1", "yes")
            
            # Create asset processor
            processor = AssetProcessor(config, self.logger)
            
            # Process all assets
            files_to_replace = processor.process_all_assets(resize_amount, black_shadows)
            
            # Replace files with backups
            if files_to_replace:
                self.backup_manager.replace_files(files_to_replace)
                MemoryUtils.force_garbage_collection()
                self.logger(f"[UNOFFICIAL RETRO PATCH] Finished pixelation process for {edition_name}.")
            else:
                self.logger(f"[UNOFFICIAL RETRO PATCH] No files were processed for {edition_name}.")
                
        except Exception as e:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Error processing {edition_name}: {str(e)}")
            raise
    
    def get_available_editions(self) -> list:
        """Get list of available editions."""
        return self.config_manager.get_editions()
    
    def validate_edition_directory(self, edition_name: str, directory: str) -> bool:
        """Validate that a directory is a valid game installation."""
        try:
            config = self.config_manager.get_edition_config(edition_name)
            
            # Check for executable
            if edition_name == "Stronghold Definitive Edition":
                exe_path = os.path.join(directory, "Stronghold 1 Definitive Edition.exe")
                data_folder = os.path.join(directory, "Stronghold 1 Definitive Edition_Data")
            elif edition_name == "Stronghold Crusader Definitive Edition":
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
            
            return ((exe_path and os.path.exists(exe_path)) or 
                   (data_folder and os.path.isdir(data_folder)))
                   
        except Exception:
            return False
    
    def set_edition_directory(self, edition_name: str, directory: str) -> None:
        """Set the directory for an edition."""
        self.config_manager.set_edition_target_folder(edition_name, directory)
    
    def get_edition_directory(self, edition_name: str) -> str:
        """Get the directory for an edition."""
        return self.config_manager.get_edition_target_folder(edition_name)
    
    def find_backups_for_edition(self, edition_name: str) -> list:
        """Find all backup files for an edition."""
        directory = self.get_edition_directory(edition_name)
        if not directory or not os.path.exists(directory):
            return []
        
        backup_files = self.backup_manager.find_backups_in_directory(directory)
        backup_info = []
        
        for backup_file in backup_files:
            relative_path, backup_date = self.backup_manager.get_backup_info(backup_file, directory)
            backup_info.append({
                'file': relative_path,
                'date': backup_date,
                'full_path': backup_file
            })
        
        return backup_info
    
    def restore_backup(self, backup_file: str, original_file: str) -> bool:
        """Restore a backup file."""
        return self.backup_manager.restore_backup(backup_file, original_file)


# Backward compatibility function
def pixelate_edition(edition_name: str, logger: Optional[Callable] = None, resize_amount: Optional[float] = None, black_shadows: bool = False):
    """Backward compatibility function for pixelate_edition."""
    processor = MainProcessor(logger)
    return processor.pixelate_edition(edition_name, resize_amount, black_shadows)


def replace_files(files_to_replace, logger: Optional[Callable] = None):
    """Backward compatibility function for replace_files."""
    backup_manager = BackupManager(logger)
    return backup_manager.replace_files(files_to_replace)