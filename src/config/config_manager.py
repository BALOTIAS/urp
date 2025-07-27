"""
Configuration manager for handling application configuration.
"""

import os
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Any
from .settings import settings


class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_file: Optional[str] = None) -> None:
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. Defaults to settings.DEFAULT_CONFIG_FILE.
        """
        self.config_file = config_file or settings.DEFAULT_CONFIG_FILE
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
        """Get list of available editions from configuration.
        
        Returns:
            List of edition names.
        """
        return [section for section in self.config.sections() if section in settings.SUPPORTED_EDITIONS]
    
    def get_edition_config(self, edition: str) -> Dict[str, Any]:
        """Get configuration for a specific edition.
        
        Args:
            edition: Name of the edition.
            
        Returns:
            Dictionary containing edition configuration.
        """
        if not self.config.has_section(edition):
            return {}
        
        return {
            "target_folder": self.config.get(edition, "target_folder", fallback=""),
            "assets_folder": self.config.get(edition, "assets_folder", fallback=""),
            "masks_folder": self.config.get(edition, "masks_folder", fallback=""),
            "debug_pixelated_folder": self.config.get(edition, "debug_pixelated_folder", fallback=""),
            "resize_amount": self.config.getfloat(edition, "resize_amount", fallback=settings.DEFAULT_RESIZE_AMOUNT),
            "pixelate_files": self._parse_pixelate_files(edition)
        }
    
    def _parse_pixelate_files(self, edition: str) -> List[str]:
        """Parse pixelate files string into a list.
        
        Args:
            edition: Name of the edition.
            
        Returns:
            List of files to pixelate.
        """
        pixelate_files_str = self.config.get(edition, "pixelate_files", fallback="")
        return [f.strip() for f in pixelate_files_str.split(",") if f.strip()]
    
    def set_edition_config(self, edition: str, key: str, value: Any) -> None:
        """Set a configuration value for an edition.
        
        Args:
            edition: Name of the edition.
            key: Configuration key.
            value: Configuration value.
        """
        if not self.config.has_section(edition):
            self.config.add_section(edition)
        
        self.config.set(edition, key, str(value))
        self.save_config()
    
    def validate_edition_config(self, edition: str) -> List[str]:
        """Validate configuration for an edition.
        
        Args:
            edition: Name of the edition.
            
        Returns:
            List of validation errors.
        """
        errors = []
        config = self.get_edition_config(edition)
        
        if not config.get("target_folder"):
            errors.append(f"Target folder not configured for {edition}")
        
        if not config.get("assets_folder"):
            errors.append(f"Assets folder not configured for {edition}")
        
        if not config.get("pixelate_files"):
            errors.append(f"No files configured for pixelation in {edition}")
        
        return errors