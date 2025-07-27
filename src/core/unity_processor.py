"""
Unity asset processing functionality.

This module handles Unity asset file operations including loading, modifying,
and saving Unity asset files using UnityPy.
"""

import os
import warnings
import gc
import time
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass
import UnityPy
from .config import EditionConfig


@dataclass
class PixelateEntry:
    """Represents a file to be pixelated."""
    asset_dir: str
    asset: str
    asset_name: str
    asset_ext: str
    mask_file: str


class UnityProcessor:
    """Handles Unity asset file processing operations."""
    
    def __init__(self, logger: Optional[Callable] = None):
        self.logger = logger or print
    
    def group_pixelate_files(self, pixelate_files: List[str], target_folder: str, 
                           assets_folder: str, masks_folder: str) -> Dict[str, List[PixelateEntry]]:
        """Group pixelate files by their asset file directory."""
        pixelate_asset_files = {}
        
        for pixelate_file in pixelate_files:
            asset_dir = os.path.dirname(pixelate_file)
            asset_file = os.path.join(target_folder, assets_folder, asset_dir)
            
            if not os.path.exists(asset_file):
                warnings.warn(
                    f"[UNOFFICIAL RETRO PATCH] Asset file directory '{asset_file}' does not exist. "
                    f"Skipping pixelation for {pixelate_file}."
                )
                continue
            
            pixelate_file_basename = os.path.basename(pixelate_file)
            name, extension = os.path.splitext(pixelate_file_basename)
            
            if asset_file not in pixelate_asset_files:
                pixelate_asset_files[asset_file] = []
            
            pixelate_asset_files[asset_file].append(PixelateEntry(
                asset_dir=asset_dir,
                asset=pixelate_file_basename,
                asset_name=name,
                asset_ext=extension,
                mask_file=os.path.join(masks_folder, f"{asset_dir}/{pixelate_file_basename}")
            ))
        
        return pixelate_asset_files
    
    def restore_latest_backup(self, asset_file: str) -> Optional[str]:
        """Restore the latest backup if it exists."""
        backup_no = 1
        backup_file = f"{asset_file}.backup{backup_no:03}"
        latest_backup = None
        
        while os.path.exists(backup_file):
            latest_backup = backup_file
            backup_no += 1
            backup_file = f"{asset_file}.backup{backup_no:03}"
        
        if latest_backup:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Restoring latest backup before pixelation: {latest_backup}")
            if os.path.exists(asset_file):
                os.remove(asset_file)
            os.rename(latest_backup, asset_file)
            return latest_backup
        
        return None
    
    def process_asset_file(self, asset_file: str, pixelate_entries: List[PixelateEntry],
                         resize_amount: float, black_shadows: bool = False,
                         debug_pixelated_folder: Optional[str] = None) -> Tuple[int, str]:
        """
        Process a single asset file and return the number of processed textures
        and the path to the temporary modified file.
        """
        from ..image_processing import process_image
        
        # Restore latest backup if it exists
        self.restore_latest_backup(asset_file)
        
        # Load Unity environment
        env = UnityPy.load(asset_file)
        processed_textures = 0
        modified_objects = []
        
        # Prepare texture data for processing
        texture_data_list = []
        for obj in env.objects:
            if obj.type.name == "Texture2D":
                for pixelate_entry in pixelate_entries:
                    texture_data_list.append((obj, pixelate_entry))
        
        # Process textures
        for obj, pixelate_entry in texture_data_list:
            try:
                data = obj.read()
                
                if not hasattr(data, "m_Name") or data.m_Name != pixelate_entry.asset_name:
                    continue
                
                if hasattr(data, "image"):
                    processed_textures += 1
                    self.logger(f"[UNOFFICIAL RETRO PATCH] Pixelating texture: {pixelate_entry.asset_name}")
                    
                    data.image = process_image(
                        image=data.image,
                        resize_amount=resize_amount,
                        mask_file=pixelate_entry.mask_file,
                        asset_name=pixelate_entry.asset_name,
                        black_shadows=black_shadows,
                    )
                    data.save()
                    modified_objects.append(obj)
                    
                    self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully pixelated {pixelate_entry.asset_name}")
                    
                    # Save debug image if enabled
                    if debug_pixelated_folder:
                        debug_path = os.path.join(
                            debug_pixelated_folder, 
                            pixelate_entry.asset_dir, 
                            pixelate_entry.asset
                        )
                        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                        data.image.save(debug_path)
                        self.logger(f"[UNOFFICIAL RETRO PATCH | DEBUG] Exported pixelated {pixelate_entry.asset_name} to {debug_path}")
                else:
                    warnings.warn(f"[UNOFFICIAL RETRO PATCH] {pixelate_entry.asset_name} does not have an image attribute.")
                    
            except Exception as e:
                warnings.warn(f"Failed to pixelate {pixelate_entry.asset_name}: {e}")
        
        if processed_textures == 0:
            self.logger(f"[UNOFFICIAL RETRO PATCH] No textures to process in {asset_file}")
        else:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Modified {len(modified_objects)} objects in {asset_file}")
        
        # Save modified asset file to temporary location
        modified_asset_file = asset_file + ".tmp"
        try:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Saving modified asset file to: {modified_asset_file}")
            with open(modified_asset_file, "wb") as f:
                f.write(env.file.save())
            
            if os.path.exists(modified_asset_file):
                file_size = os.path.getsize(modified_asset_file)
                self.logger(f"[UNOFFICIAL RETRO PATCH] Temporary file created: {modified_asset_file} ({file_size} bytes)")
                return processed_textures, modified_asset_file
            else:
                raise Exception("Temporary file was not created")
                
        except Exception as e:
            warnings.warn(f"Failed to save modified asset file '{asset_file}': {e}")
            return processed_textures, None
    
    def create_backup(self, original_file: str) -> Optional[str]:
        """Create a backup of the original file."""
        backup_no = 1
        backup_file = f"{original_file}.backup{backup_no:03}"
        
        while os.path.exists(backup_file):
            backup_no += 1
            backup_file = f"{original_file}.backup{backup_no:03}"
        
        try:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Creating backup: {original_file} -> {backup_file}")
            os.rename(original_file, backup_file)
            return backup_file
        except Exception as e:
            warnings.warn(f"Failed to create backup for '{original_file}': {e}")
            return None
    
    def replace_file(self, original_file: str, temp_file: str, max_wait: int = 30) -> bool:
        """Replace the original file with the temporary file."""
        from .file_utils import is_file_locked
        
        wait_time = 0
        while is_file_locked(original_file) and wait_time < max_wait:
            self.logger(f"[UNOFFICIAL RETRO PATCH] File locked, waiting... ({wait_time}s)")
            time.sleep(2)
            wait_time += 2
        
        if is_file_locked(original_file):
            warnings.warn(f"File still locked after {max_wait}s: {original_file}")
            return False
        
        backup_file = None
        try:
            # Create backup
            backup_file = self.create_backup(original_file)
            
            # Replace with modified file
            self.logger(f"[UNOFFICIAL RETRO PATCH] Replacing original with modified file: {temp_file} -> {original_file}")
            os.rename(temp_file, original_file)
            
            self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully replaced asset file: {original_file}")
            return True
            
        except Exception as e:
            warnings.warn(f"Failed to replace asset file '{original_file}': {e}")
            
            # Try to restore original if backup was created
            if backup_file and os.path.exists(backup_file) and not os.path.exists(original_file):
                try:
                    os.rename(backup_file, original_file)
                    self.logger(f"[UNOFFICIAL RETRO PATCH] Restored original file from backup: {original_file}")
                except Exception as restore_e:
                    warnings.warn(f"Failed to restore original file '{original_file}': {restore_e}")
            
            return False