"""
Main entry point for the Unofficial Retro Patch application.

This module provides the command-line interface for the application.
"""

import os
import warnings
import gc
import time
from dotenv import load_dotenv

from .utils.unitypy_patch import patch_unitypy
from .core.config import config_manager
from .core.unity_processor import UnityProcessor
from .core.file_utils import log_memory_usage


# Load environment variables
load_dotenv()
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "False").lower() in ("true", "1", "yes")


def pixelate_edition(edition_name: str, logger=None, black_shadows=False):
    """
    Pixelate a specific game edition.
    
    Args:
        edition_name: Name of the edition to pixelate
        logger: Optional logger function
        black_shadows: Whether to apply black shadows effect
        
    Returns:
        List of (original_file, temp_file) tuples for file replacement
    """
    if logger is None:
        logger = print
    
    logger(f"\n[UNOFFICIAL RETRO PATCH] Pixelating edition: {edition_name}")
    log_memory_usage(logger)
    
    try:
        # Get configuration for the edition
        config = config_manager.get_edition_config(edition_name)
        
        # Validate paths
        errors = config_manager.validate_edition_paths(config)
        if errors:
            raise FileNotFoundError(f"Configuration errors: {'; '.join(errors)}")
        
        if len(config.pixelate_files) == 0:
            logger(f"[UNOFFICIAL RETRO PATCH] No files to pixelate for {edition_name}.")
            return []
        
        # Create processor
        processor = UnityProcessor(logger=logger)
        
        # Group files by asset file
        pixelate_asset_files = processor.group_pixelate_files(
            config.pixelate_files, 
            config.target_folder, 
            config.assets_folder, 
            config.masks_folder
        )
        
        # Calculate total textures for progress tracking
        total_textures_across_files = sum(len(entries) for entries in pixelate_asset_files.values())
        logger(f"[UNOFFICIAL RETRO PATCH] Total textures to process: {total_textures_across_files}")
        log_memory_usage(logger)
        
        files_to_replace = []
        processed_textures_total = 0
        
        # Process each asset file
        for asset_file, pixelate_entries in pixelate_asset_files.items():
            try:
                processed_count, temp_file = processor.process_asset_file(
                    asset_file, 
                    pixelate_entries, 
                    config.resize_amount, 
                    black_shadows, 
                    config.debug_pixelated_folder
                )
                
                if temp_file:
                    files_to_replace.append((asset_file, temp_file))
                
                processed_textures_total += processed_count
                
            except Exception as e:
                logger(f"[UNOFFICIAL RETRO PATCH] Failed to process asset file '{asset_file}': {e}")
                continue
        
        return files_to_replace
        
    except Exception as e:
        logger(f"[UNOFFICIAL RETRO PATCH] Failed to pixelate edition '{edition_name}': {e}")
        return []


def replace_files(files_to_replace, logger=None):
    """
    Replace original files with their modified versions.
    
    Args:
        files_to_replace: List of (original_file, temp_file) tuples
        logger: Optional logger function
    """
    if logger is None:
        logger = print
    
    logger(f"[UNOFFICIAL RETRO PATCH] Processing {len(files_to_replace)} file replacements...")
    
    processor = UnityProcessor(logger=logger)
    
    for original_file, temp_file in files_to_replace:
        success = processor.replace_file(original_file, temp_file)
        if not success:
            logger(f"[UNOFFICIAL RETRO PATCH] Failed to replace {original_file}")


def main():
    """Main entry point for command-line usage."""
    print("\n[UNOFFICIAL RETRO PATCH] Starting pixelation process...")
    
    # Apply UnityPy patches
    patch_unitypy()
    
    # Pixelate the default edition
    files_to_replace = pixelate_edition("Stronghold Definitive Edition")
    
    if files_to_replace:
        replace_files(files_to_replace)
    
    print("\n[UNOFFICIAL RETRO PATCH] Finished pixelation process.")


if __name__ == "__main__":
    main()