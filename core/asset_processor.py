"""
Asset processing for Unity assets in the Unofficial Retro Patch.
"""

import os
import warnings
import UnityPy
from typing import List, Dict, Tuple, Optional, Callable
from .config_manager import EditionConfig
from .pixelation_engine import PixelationEngine
from .file_utils import FileUtils
from utils.memory_utils import MemoryUtils


class AssetProcessor:
    """Handles processing of Unity assets."""
    
    def __init__(self, config: EditionConfig, logger: Optional[Callable] = None):
        self.config = config
        self.logger = logger or print
    
    def validate_paths(self) -> None:
        """Validate all required paths exist."""
        FileUtils.validate_directory_exists(
            self.config.target_folder, 
            f"Target folder for {self.config.name}"
        )
        
        assets_path = os.path.join(self.config.target_folder, self.config.assets_folder)
        FileUtils.validate_directory_exists(
            assets_path, 
            f"Assets folder for {self.config.name}"
        )
        
        FileUtils.validate_directory_exists(
            self.config.masks_folder, 
            f"Masks folder for {self.config.name}"
        )
    
    def group_assets_for_processing(self) -> Dict[str, List[Dict]]:
        """Group assets by their directory for efficient processing."""
        if not self.config.pixelate_files:
            self.logger(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {self.config.name}.")
            return {}
        
        return FileUtils.group_files_by_directory(
            self.config.pixelate_files,
            self.config.target_folder,
            self.config.assets_folder
        )
    
    def process_asset_file(
        self, 
        asset_file: str, 
        pixelate_entries: List[Dict],
        resize_amount: float,
        black_shadows: bool,
        debug_pixelated_folder: str,
        total_textures_across_files: int,
        processed_textures_total: int
    ) -> Tuple[int, List[Tuple[str, str]]]:
        """Process a single asset file."""
        files_to_replace = []
        processed_textures = 0
        
        try:
            # Restore latest backup if it exists
            FileUtils.restore_latest_backup(asset_file, self.logger)
            
            env = UnityPy.load(asset_file)
            total_textures = sum(1 for obj in env.objects if obj.type.name == "Texture2D")
            
            # Get total number of textures to process across all asset files
            total_asset_files = len(pixelate_entries)
            current_asset_file_index = list(pixelate_entries.keys()).index(asset_file) + 1
            
            self.logger(f"[UNOFFICIAL RETRO PATCH] Processing asset file {current_asset_file_index}/{total_asset_files}: {os.path.basename(asset_file)}")
            
            # Prepare data for processing
            texture_data_list = []
            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    for pixelate_entry in pixelate_entries:
                        texture_data_list.append((obj, pixelate_entry, asset_file))
            
            # Process textures sequentially
            modified_objects = []
            
            for obj, pixelate_entry, asset_file in texture_data_list:
                asset_dir, asset, asset_name, asset_ext, mask_file = pixelate_entry.values()
                
                try:
                    data = obj.read()
                    
                    if not hasattr(data, "m_Name") or not data.m_Name == asset_name:
                        continue
                    
                    if hasattr(data, "image"):
                        processed_textures_total += 1
                        processed_textures += 1
                        self.logger(f"[UNOFFICIAL RETRO PATCH] Pixelating texture {processed_textures_total}/{total_textures_across_files}: {asset_name}")
                        
                        data.image = PixelationEngine.process_image(
                            image=data.image,
                            resize_amount=resize_amount,
                            mask_file=mask_file,
                            asset_name=asset_name,
                            black_shadows=(black_shadows and f"{asset_dir}/{asset}" not in self.config.ignore_black_shadow_files),
                        )
                        data.save()
                        modified_objects.append(obj)
                        
                        self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully pixelated {asset_name} in {asset_file}")
                        
                        # Debug export if enabled
                        if os.getenv("DEBUG_ENABLED", "False").lower() in ("true", "1", "yes"):
                            debug_path = os.path.join(debug_pixelated_folder, asset_dir, asset)
                            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                            data.image.save(debug_path)
                            self.logger(f"[UNOFFICIAL RETRO PATCH | DEBUG] Successfully exported pixelated {asset_name} in {debug_path}")
                    else:
                        warnings.warn(f"[UNOFFICIAL RETRO PATCH] {asset_name} in {asset_file} does not have an image attribute.")
                except Exception as e:
                    warnings.warn(f"Failed to pixelate {asset_name} in {asset_file}: {e}")
            
            if processed_textures == 0:
                self.logger(f"[UNOFFICIAL RETRO PATCH] No textures to process in {asset_file}")
            else:
                self.logger(f"[UNOFFICIAL RETRO PATCH] Modified {len(modified_objects)} objects in {asset_file}")
            
            # Save the modified asset file to temp location
            try:
                original_file, temp_file = FileUtils.save_temp_file(env, asset_file, self.logger)
                files_to_replace.append((original_file, temp_file))
                self.logger(f"[UNOFFICIAL RETRO PATCH] Prepared modified asset file for replacement: {asset_file}")
                MemoryUtils.log_memory_usage(self.logger)
            except Exception as e:
                warnings.warn(f"Failed to save modified asset file '{asset_file}': {e}")
                
        except Exception as e:
            warnings.warn(f"[UNOFFICIAL RETRO PATCH] Failed to load asset file '{asset_file}': {e}")
        
        return processed_textures, files_to_replace
    
    def process_all_assets(
        self, 
        resize_amount: Optional[float] = None,
        black_shadows: bool = False
    ) -> List[Tuple[str, str]]:
        """Process all assets for the configured edition."""
        self.logger(f"\n[UNOFFICIAL RETRO PATCH] Pixelating edition: {self.config.name}")
        MemoryUtils.log_memory_usage(self.logger)
        
        # Validate paths
        self.validate_paths()
        
        # Get resize amount
        if resize_amount is None:
            resize_amount = self.config.resize_amount
        
        # Get pixelate files
        pixelate_files = self.config.pixelate_files
        if len(pixelate_files) == 0:
            self.logger(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {self.config.name}.")
            return []
        
        # Group files by directory
        pixelate_asset_files = self.group_assets_for_processing()
        
        # Calculate total textures across all asset files for overall progress
        total_textures_across_files = sum(len(entries) for entries in pixelate_asset_files.values())
        processed_textures_total = 0
        self.logger(f"[UNOFFICIAL RETRO PATCH] Total textures to process: {total_textures_across_files}")
        MemoryUtils.log_memory_usage(self.logger)
        
        # Store pairs of (original_file, temp_file) to process after the loop
        all_files_to_replace = []
        
        for asset_file, pixelate_entries in pixelate_asset_files.items():
            processed_textures, files_to_replace = self.process_asset_file(
                asset_file,
                pixelate_entries,
                resize_amount,
                black_shadows,
                self.config.debug_pixelated_folder,
                total_textures_across_files,
                processed_textures_total
            )
            processed_textures_total += processed_textures
            all_files_to_replace.extend(files_to_replace)
        
        return all_files_to_replace