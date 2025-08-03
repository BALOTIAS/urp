"""
Configuration management for the Unofficial Retro Patch.
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
    ignore_black_shadow_files: List[str]
    resize_amount: float


class ConfigManager:
    """Manages configuration for the Unofficial Retro Patch."""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
    
    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)
    
    def get_editions(self) -> List[str]:
        """Get list of available editions."""
        return [section for section in self.config.sections()]
    
    def get_edition_config(self, edition_name: str) -> EditionConfig:
        """Get configuration for a specific edition."""
        if not self.config.has_section(edition_name):
            raise ValueError(f"Edition '{edition_name}' not found in configuration")
        
        section = self.config[edition_name]
        
        # Get pixelate files as list
        pixelate_files_str = section.get("pixelate_files", "")
        pixelate_files = [f.strip() for f in pixelate_files_str.split(",") if f.strip()]
        
        # Get ignore black shadow files as list
        ignore_black_shadow_files_str = section.get("ignore_black_shadow_files", "")
        ignore_black_shadow_files = [f.strip() for f in ignore_black_shadow_files_str.split(",") if f.strip()]
        
        return EditionConfig(
            name=edition_name,
            target_folder=section.get("target_folder", ""),
            assets_folder=section.get("assets_folder", ""),
            masks_folder=section.get("masks_folder", ""),
            debug_pixelated_folder=section.get("debug_pixelated_folder", ""),
            pixelate_files=pixelate_files,
            ignore_black_shadow_files=ignore_black_shadow_files,
            resize_amount=section.getfloat("resize_amount", 0.5)
        )
    
    def set_edition_target_folder(self, edition_name: str, target_folder: str) -> None:
        """Set the target folder for an edition."""
        if not self.config.has_section(edition_name):
            self.config.add_section(edition_name)
        
        self.config.set(edition_name, "target_folder", target_folder)
        self.save_config()
    
    def get_edition_target_folder(self, edition_name: str) -> str:
        """Get the target folder for an edition."""
        if not self.config.has_section(edition_name):
            return ""
        
        return self.config.get(edition_name, "target_folder", fallback="")
    
    def get_environment_value(self, key: str, default: Any = None) -> Any:
        """Get a value from environment variables."""
        return os.getenv(key, default)
    
    def get_edition_environment_value(self, edition_name: str, key: str, default: Any = None) -> Any:
        """Get an environment variable specific to an edition."""
        env_key = f"{edition_name.upper().replace(' ', '_')}_{key}"
        return self.get_environment_value(env_key, default)