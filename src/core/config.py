"""
Configuration management for the Unofficial Retro Patch application.

This module handles loading, validation, and access to application configuration
including edition-specific settings and environment variables.
"""

import os
import configparser
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EditionConfig:
    """Configuration for a specific game edition."""
    name: str
    target_folder: str
    assets_folder: str
    masks_folder: str
    debug_pixelated_folder: str
    pixelate_files: List[str]
    resize_amount: float
    debug_source_folder: Optional[str] = None
    debug_unpacked_folder: Optional[str] = None
    debug_exported_alpha_masks_folder: Optional[str] = None


class ConfigManager:
    """Manages application configuration and environment variables."""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)
    
    def get_edition_config(self, edition_name: str) -> EditionConfig:
        """Get configuration for a specific edition."""
        if not self.config.has_section(edition_name):
            raise ValueError(f"Edition '{edition_name}' not found in configuration")
        
        # Get environment variable overrides
        env_prefix = edition_name.upper().replace(' ', '_')
        target_folder = os.getenv(f"{env_prefix}_TARGET_FOLDER") or \
                       self.config.get(edition_name, "target_folder", fallback=f"downloads/{edition_name}")
        
        assets_folder = self.config.get(edition_name, "assets_folder", 
                                      fallback=f"{edition_name}_Data/resources.assets")
        
        masks_folder = self.config.get(edition_name, "masks_folder", 
                                     fallback=f"assets/masks/{edition_name}")
        
        debug_pixelated_folder = self.config.get(edition_name, "debug_pixelated_folder", 
                                               fallback=f"downloads/{edition_name}/pixelated")
        
        # Parse resize amount
        resize_env = os.getenv(f"{env_prefix}_RESIZE_AMOUNT")
        if resize_env:
            resize_amount = float(resize_env)
        else:
            resize_amount = self.config.getfloat(edition_name, "resize_amount", fallback=0.5)
        
        # Parse pixelate files
        pixelate_files_env = os.getenv(f"{env_prefix}_PIXELATE_FILES")
        if pixelate_files_env:
            pixelate_files_str = pixelate_files_env
        else:
            pixelate_files_str = self.config.get(edition_name, "pixelate_files", fallback="")
        
        pixelate_files = [f.strip() for f in pixelate_files_str.split(",") if f.strip()]
        
        return EditionConfig(
            name=edition_name,
            target_folder=target_folder,
            assets_folder=assets_folder,
            masks_folder=masks_folder,
            debug_pixelated_folder=debug_pixelated_folder,
            pixelate_files=pixelate_files,
            resize_amount=resize_amount,
            debug_source_folder=self.config.get(edition_name, "debug_source_folder", fallback=None),
            debug_unpacked_folder=self.config.get(edition_name, "debug_unpacked_folder", fallback=None),
            debug_exported_alpha_masks_folder=self.config.get(edition_name, "debug_exported_alpha_masks_folder", fallback=None)
        )
    
    def get_available_editions(self) -> List[str]:
        """Get list of available editions from configuration."""
        return self.config.sections()
    
    def update_edition_path(self, edition_name: str, target_folder: str) -> None:
        """Update the target folder for a specific edition."""
        if not self.config.has_section(edition_name):
            self.config.add_section(edition_name)
        
        self.config.set(edition_name, "target_folder", target_folder)
        self.save_config()
    
    def validate_edition_paths(self, edition_config: EditionConfig) -> List[str]:
        """Validate that all required paths exist for an edition."""
        errors = []
        
        if not os.path.exists(edition_config.target_folder):
            errors.append(f"Target folder '{edition_config.target_folder}' does not exist")
        
        assets_path = os.path.join(edition_config.target_folder, edition_config.assets_folder)
        if not os.path.exists(assets_path):
            errors.append(f"Assets folder '{assets_path}' does not exist")
        
        if not os.path.exists(edition_config.masks_folder):
            errors.append(f"Masks folder '{edition_config.masks_folder}' does not exist")
        
        return errors


# Global configuration manager instance
config_manager = ConfigManager()