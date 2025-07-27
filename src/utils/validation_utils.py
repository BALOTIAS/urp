"""
Validation utility functions for validating paths, files, and game installations.
"""

import os
from typing import List, Tuple
from ..config.settings import settings


class ValidationUtils:
    """Utility class for validation operations."""
    
    @staticmethod
    def validate_game_directory(directory: str, edition: str) -> Tuple[bool, List[str]]:
        """Validate if a directory is a valid game installation.
        
        Args:
            directory: Path to the directory to validate.
            edition: Name of the game edition.
            
        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []
        
        if not os.path.exists(directory):
            errors.append(f"Directory does not exist: {directory}")
            return False, errors
        
        if not os.path.isdir(directory):
            errors.append(f"Path is not a directory: {directory}")
            return False, errors
        
        # Check for expected files based on edition
        expected_files = ValidationUtils._get_expected_files(edition)
        missing_files = []
        
        for file_path in expected_files:
            full_path = os.path.join(directory, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            errors.append(f"Missing expected files: {', '.join(missing_files)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _get_expected_files(edition: str) -> List[str]:
        """Get expected files for a game edition.
        
        Args:
            edition: Name of the game edition.
            
        Returns:
            List of expected file paths.
        """
        if edition == "Stronghold Definitive Edition":
            return [
                "Stronghold 1 Definitive Edition.exe",
                "Stronghold 1 Definitive Edition_Data"
            ]
        elif edition == "Stronghold Crusader Definitive Edition":
            return [
                "Stronghold Crusader Definitive Edition.exe",
                "Stronghold Crusader Definitive Edition_Data"
            ]
        else:
            # Generic check for any .exe and _Data folder
            return []
    
    @staticmethod
    def validate_asset_file(filepath: str) -> Tuple[bool, List[str]]:
        """Validate if a file is a valid asset file.
        
        Args:
            filepath: Path to the asset file.
            
        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []
        
        if not os.path.exists(filepath):
            errors.append(f"Asset file does not exist: {filepath}")
            return False, errors
        
        if not os.path.isfile(filepath):
            errors.append(f"Path is not a file: {filepath}")
            return False, errors
        
        # Check file extension
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in settings.ASSET_EXTENSIONS:
            errors.append(f"Invalid file extension: {ext}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_mask_file(filepath: str) -> Tuple[bool, List[str]]:
        """Validate if a file is a valid mask file.
        
        Args:
            filepath: Path to the mask file.
            
        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []
        
        if not os.path.exists(filepath):
            errors.append(f"Mask file does not exist: {filepath}")
            return False, errors
        
        if not os.path.isfile(filepath):
            errors.append(f"Path is not a file: {filepath}")
            return False, errors
        
        # Check if it's an image file
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in ['.png', '.jpg', '.jpeg']:
            errors.append(f"Invalid mask file extension: {ext}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_resize_amount(amount: float) -> Tuple[bool, List[str]]:
        """Validate if a resize amount is within acceptable range.
        
        Args:
            amount: Resize amount to validate.
            
        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []
        
        if not isinstance(amount, (int, float)):
            errors.append("Resize amount must be a number")
            return False, errors
        
        if amount < settings.MIN_RESIZE_AMOUNT:
            errors.append(f"Resize amount too small (minimum: {settings.MIN_RESIZE_AMOUNT})")
        
        if amount > settings.MAX_RESIZE_AMOUNT:
            errors.append(f"Resize amount too large (maximum: {settings.MAX_RESIZE_AMOUNT})")
        
        return len(errors) == 0, errors