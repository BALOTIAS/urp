"""
Main application class that coordinates all components.
"""

import os
import warnings
from typing import Optional, Callable, Dict, Any, List, Tuple
from ..config.config_manager import ConfigManager
from ..config.settings import settings
from ..game.asset_manager import AssetManager
from ..utils.memory_utils import MemoryUtils
from ..utils.file_utils import FileUtils
from ..utils.validation_utils import ValidationUtils


class Application:
    """Main application class that coordinates all components."""
    
    def __init__(self, logger: Optional[Callable] = None):
        """Initialize the application.
        
        Args:
            logger: Logger function to use for output. Defaults to print.
        """
        self.logger = logger or print
        self.config_manager = ConfigManager()
        self.asset_manager = AssetManager(logger)
    
    def pixelate_edition(
        self,
        edition_name: str,
        black_shadows: bool = False
    ) -> List[Tuple[str, str]]:
        """Pixelate an edition using the configuration.
        
        Args:
            edition_name: Name of the edition to pixelate.
            black_shadows: Whether to apply black shadows.
            
        Returns:
            List of tuples containing (original_file, temp_file) for replacement.
        """
        # Get configuration for the edition
        config = self.config_manager.get_edition_config(edition_name)
        
        # Validate configuration
        validation_errors = self.config_manager.validate_edition_config(edition_name)
        if validation_errors:
            raise ValueError(f"Configuration errors for {edition_name}:\n" + "\n".join(validation_errors))
        
        # Check environment variables for overrides
        config = self._apply_environment_overrides(edition_name, config)
        
        # Validate paths
        self._validate_paths(edition_name, config)
        
        # Process the edition
        return self.asset_manager.process_edition(edition_name, config, black_shadows)
    
    def replace_files(self, files_to_replace: List[Tuple[str, str]]) -> None:
        """Replace original files with their modified versions.
        
        Args:
            files_to_replace: List of tuples containing (original_file, temp_file).
        """
        self.asset_manager.replace_files(files_to_replace)
    
    def _apply_environment_overrides(self, edition_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration.
        
        Args:
            edition_name: Name of the edition.
            config: Configuration dictionary.
            
        Returns:
            Updated configuration dictionary.
        """
        edition_env = edition_name.upper().replace(' ', '_')
        
        # Override target folder
        target_folder_env = os.getenv(f"{edition_env}_TARGET_FOLDER")
        if target_folder_env:
            config["target_folder"] = target_folder_env
        
        # Override resize amount
        resize_amount_env = os.getenv(f"{edition_env}_RESIZE_AMOUNT")
        if resize_amount_env:
            try:
                config["resize_amount"] = float(resize_amount_env)
            except ValueError:
                warnings.warn(f"Invalid resize amount in environment: {resize_amount_env}")
        
        # Override pixelate files
        pixelate_files_env = os.getenv(f"{edition_env}_PIXELATE_FILES")
        if pixelate_files_env:
            config["pixelate_files"] = [f.strip() for f in pixelate_files_env.split(",") if f.strip()]
        
        return config
    
    def _validate_paths(self, edition_name: str, config: Dict[str, Any]) -> None:
        """Validate all paths in the configuration.
        
        Args:
            edition_name: Name of the edition.
            config: Configuration dictionary.
        """
        target_folder = config["target_folder"]
        assets_folder = config["assets_folder"]
        masks_folder = config["masks_folder"]
        
        # Validate target folder
        if not os.path.exists(target_folder):
            raise FileNotFoundError(f"Target folder '{target_folder}' does not exist.")
        
        # Validate assets folder
        assets_path = os.path.join(target_folder, assets_folder)
        if not os.path.exists(assets_path):
            raise FileNotFoundError(f"Assets folder '{assets_path}' does not exist.")
        
        # Validate masks folder
        if not os.path.exists(masks_folder):
            raise FileNotFoundError(f"Masks folder '{masks_folder}' does not exist.")
    
    def get_available_editions(self) -> List[str]:
        """Get list of available editions.
        
        Returns:
            List of edition names.
        """
        return self.config_manager.get_editions()
    
    def validate_edition_config(self, edition_name: str) -> List[str]:
        """Validate configuration for an edition.
        
        Args:
            edition_name: Name of the edition.
            
        Returns:
            List of validation errors.
        """
        return self.config_manager.validate_edition_config(edition_name)
    
    def set_edition_config(self, edition_name: str, key: str, value: Any) -> None:
        """Set a configuration value for an edition.
        
        Args:
            edition_name: Name of the edition.
            key: Configuration key.
            value: Configuration value.
        """
        self.config_manager.set_edition_config(edition_name, key, value)
    
    def get_edition_config(self, edition_name: str) -> Dict[str, Any]:
        """Get configuration for an edition.
        
        Args:
            edition_name: Name of the edition.
            
        Returns:
            Configuration dictionary.
        """
        return self.config_manager.get_edition_config(edition_name)
    
    def log_memory_usage(self) -> None:
        """Log current memory usage."""
        MemoryUtils.log_memory_usage(self.logger)
    
    def cleanup_memory_if_needed(self) -> None:
        """Clean up memory if usage is above threshold."""
        MemoryUtils.cleanup_memory_if_needed()
        self.asset_manager.cleanup_memory_if_needed()