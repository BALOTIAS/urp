"""
Asset management and processing coordination.
"""

import os
import warnings
from typing import Dict, List, Optional, Callable, Any, Tuple
from ..config.settings import settings
from ..utils.file_utils import FileUtils
from ..utils.validation_utils import ValidationUtils
from .unity_processor import UnityProcessor


class AssetManager:
    """Manages asset files and coordinates processing operations."""
    
    def __init__(self, logger: Optional[Callable] = None):
        """Initialize the asset manager.
        
        Args:
            logger: Logger function to use for output. Defaults to print.
        """
        self.logger = logger or print
        self.unity_processor = UnityProcessor(logger)
    
    def organize_pixelate_files(
        self,
        pixelate_files: List[str],
        target_folder: str,
        assets_folder: str,
        masks_folder: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize pixelate files by their asset file directory.
        
        Args:
            pixelate_files: List of files to pixelate.
            target_folder: Target folder path.
            assets_folder: Assets folder path.
            masks_folder: Masks folder path.
            
        Returns:
            Dictionary mapping asset files to their pixelation entries.
        """
        pixelate_asset_files = {}
        
        for pixelate_file in pixelate_files:
            asset_dir = os.path.dirname(pixelate_file)
            
            # e.g. system/Stronghold Definitive Edition/Stronghold Definitive Edition_Data/resources.assets
            asset_file = os.path.join(target_folder, assets_folder, asset_dir)
            
            if not os.path.exists(asset_file):
                warnings.warn(
                    f"[UNOFFICIAL RETRO PATCH] Asset file directory '{asset_file}' does not exist. "
                    f"Skipping pixelation for {pixelate_file}."
                )
                continue
            
            # e.g. texture_name.png
            pixelate_file_basename = os.path.basename(pixelate_file)
            name, extension = os.path.splitext(pixelate_file_basename)
            
            if asset_file not in pixelate_asset_files:
                pixelate_asset_files[asset_file] = []
            
            pixelate_asset_files[asset_file].append({
                "asset_dir": asset_dir,
                "asset": pixelate_file_basename,
                "asset_name": name,
                "asset_ext": extension,
                "mask_file": os.path.join(masks_folder, f"{asset_dir}/{pixelate_file_basename}")
            })
        
        return pixelate_asset_files
    
    def validate_asset_files(
        self,
        pixelate_asset_files: Dict[str, List[Dict[str, Any]]],
        target_folder: str,
        assets_folder: str,
        masks_folder: str
    ) -> List[str]:
        """Validate asset files and their dependencies.
        
        Args:
            pixelate_asset_files: Dictionary of asset files and their entries.
            target_folder: Target folder path.
            assets_folder: Assets folder path.
            masks_folder: Masks folder path.
            
        Returns:
            List of validation errors.
        """
        errors = []
        
        # Validate target folder
        if not os.path.exists(target_folder):
            errors.append(f"Target folder '{target_folder}' does not exist.")
        
        # Validate assets folder
        assets_path = os.path.join(target_folder, assets_folder)
        if not os.path.exists(assets_path):
            errors.append(f"Assets folder '{assets_path}' does not exist.")
        
        # Validate masks folder
        if not os.path.exists(masks_folder):
            errors.append(f"Masks folder '{masks_folder}' does not exist.")
        
        # Validate each asset file
        for asset_file in pixelate_asset_files:
            if not os.path.exists(asset_file):
                errors.append(f"Asset file '{asset_file}' does not exist.")
        
        return errors
    
    def process_edition(
        self,
        edition_name: str,
        config: Dict[str, Any],
        black_shadows: bool = False
    ) -> List[Tuple[str, str]]:
        """Process an entire edition with pixelation.
        
        Args:
            edition_name: Name of the edition to process.
            config: Configuration dictionary for the edition.
            black_shadows: Whether to apply black shadows.
            
        Returns:
            List of tuples containing (original_file, temp_file) for replacement.
        """
        self.logger(f"\n[UNOFFICIAL RETRO PATCH] Pixelating edition: {edition_name}")
        self.unity_processor.log_memory_usage()
        
        # Extract configuration values
        target_folder = config["target_folder"]
        assets_folder = config["assets_folder"]
        masks_folder = config["masks_folder"]
        debug_pixelated_folder = config["debug_pixelated_folder"]
        resize_amount = config["resize_amount"]
        pixelate_files = config["pixelate_files"]
        
        # Validate configuration
        validation_errors = self.validate_asset_files(
            {}, target_folder, assets_folder, masks_folder
        )
        if validation_errors:
            raise FileNotFoundError("\n".join(validation_errors))
        
        # Organize files by asset file
        pixelate_asset_files = self.organize_pixelate_files(
            pixelate_files, target_folder, assets_folder, masks_folder
        )
        
        if not pixelate_asset_files:
            self.logger(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {edition_name}.")
            return []
        
        # Calculate total textures for progress tracking
        total_textures = sum(len(entries) for entries in pixelate_asset_files.values())
        self.logger(f"[UNOFFICIAL RETRO PATCH] Total textures to process: {total_textures}")
        self.unity_processor.log_memory_usage()
        
        # Process each asset file
        files_to_replace = []
        processed_textures_total = 0
        
        for asset_file, pixelate_entries in pixelate_asset_files.items():
            try:
                # Restore latest backup if it exists
                self._restore_latest_backup(asset_file)
                
                # Process the asset file
                modified_objects, temp_file = self.unity_processor.process_asset_file(
                    asset_file=asset_file,
                    pixelate_entries=pixelate_entries,
                    resize_amount=resize_amount,
                    black_shadows=black_shadows,
                    debug_folder=debug_pixelated_folder if settings.DEBUG_ENABLED else None
                )
                
                if temp_file:
                    files_to_replace.append((asset_file, temp_file))
                
                processed_textures_total += len(modified_objects)
                self.logger(f"[UNOFFICIAL RETRO PATCH] Processed {len(modified_objects)} textures in {os.path.basename(asset_file)}")
                
            except Exception as e:
                warnings.warn(f"[UNOFFICIAL RETRO PATCH] Failed to process asset file '{asset_file}': {e}")
                continue
        
        self.logger(f"[UNOFFICIAL RETRO PATCH] Completed processing {processed_textures_total} textures total.")
        return files_to_replace
    
    def _restore_latest_backup(self, asset_file: str) -> None:
        """Restore the latest backup for an asset file.
        
        Args:
            asset_file: Path to the asset file.
        """
        backup_no = 1
        backup_file = f"{asset_file}{settings.BACKUP_EXTENSION}{backup_no:03}"
        latest_backup = None
        
        while os.path.exists(backup_file):
            latest_backup = backup_file
            backup_no += 1
            backup_file = f"{asset_file}{settings.BACKUP_EXTENSION}{backup_no:03}"
        
        if latest_backup:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Restoring latest backup before pixelation: {latest_backup}")
            if os.path.exists(asset_file):
                os.remove(asset_file)
            os.rename(latest_backup, asset_file)
    
    def replace_files(self, files_to_replace: List[Tuple[str, str]]) -> None:
        """Replace original files with their modified versions.
        
        Args:
            files_to_replace: List of tuples containing (original_file, temp_file).
        """
        self.logger(f"[UNOFFICIAL RETRO PATCH] Processing {len(files_to_replace)} file replacements...")
        
        for original_file, temp_file in files_to_replace:
            # Wait for file to be unlocked
            if not FileUtils.wait_for_file_unlock(original_file):
                warnings.warn(f"File still locked after timeout: {original_file}")
                continue
            
            try:
                # Create backup
                backup_file = FileUtils.create_backup(original_file)
                if not backup_file:
                    warnings.warn(f"Failed to create backup for {original_file}")
                    continue
                
                self.logger(f"[UNOFFICIAL RETRO PATCH] Creating backup: {original_file} -> {backup_file}")
                
                # Replace original with modified file
                self.logger(f"[UNOFFICIAL RETRO PATCH] Replacing original with modified file: {temp_file} -> {original_file}")
                os.rename(temp_file, original_file)
                
                self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully replaced asset file: {original_file}")
                
            except Exception as e:
                warnings.warn(f"Failed to replace asset file '{original_file}': {e}")
                
                # Try to restore original if backup was created
                if backup_file and os.path.exists(backup_file) and not os.path.exists(original_file):
                    try:
                        FileUtils.restore_backup(backup_file, original_file)
                        self.logger(f"[UNOFFICIAL RETRO PATCH] Restored original file from backup: {original_file}")
                    except Exception as restore_e:
                        warnings.warn(f"Failed to restore original file '{original_file}': {restore_e}")
    
    def cleanup_memory_if_needed(self) -> None:
        """Clean up memory if usage is above threshold."""
        self.unity_processor.cleanup_memory_if_needed()