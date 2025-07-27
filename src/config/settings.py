"""
Application settings and constants.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """Application settings and configuration."""
    
    # Debug settings
    DEBUG_ENABLED: bool = False
    
    # Default paths
    DEFAULT_CONFIG_FILE: str = "config.ini"
    DEFAULT_ASSETS_DIR: str = "assets"
    DEFAULT_MASKS_DIR: str = "assets/masks"
    
    # Supported game editions
    SUPPORTED_EDITIONS: tuple[str, ...] = (
        "Stronghold Definitive Edition",
        "Stronghold Crusader Definitive Edition"
    )
    
    # File extensions
    ASSET_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg")
    BACKUP_EXTENSION: str = ".backup"
    
    # Processing settings
    DEFAULT_RESIZE_AMOUNT: float = 0.5
    MIN_RESIZE_AMOUNT: float = 0.1
    MAX_RESIZE_AMOUNT: float = 1.0
    
    # Memory management
    MAX_MEMORY_USAGE_MB: int = 2048
    GARBAGE_COLLECTION_THRESHOLD: int = 100
    
    # File operations
    MAX_FILE_LOCK_WAIT_SECONDS: int = 30
    FILE_LOCK_CHECK_INTERVAL: int = 2
    
    def __post_init__(self) -> None:
        """Initialize settings from environment variables."""
        self.DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "False").lower() in ("true", "1", "yes")


# Global settings instance
settings = Settings()