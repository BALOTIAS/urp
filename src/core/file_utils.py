"""
File utility functions for the Unofficial Retro Patch application.

This module provides utility functions for file operations, system monitoring,
and backup management.
"""

import os
import psutil
from typing import List, Optional
from datetime import datetime


def is_file_locked(filepath: str) -> bool:
    """Check if file is locked by another process."""
    try:
        with open(filepath, 'r+b'):
            return False
    except (PermissionError, OSError):
        return True


def log_memory_usage(logger=None) -> None:
    """Log current memory usage for debugging."""
    if logger is None:
        logger = print
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger(f"[UNOFFICIAL RETRO PATCH] Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass  # psutil not available


def get_file_modified_date(file_path: str) -> str:
    """Get the modification date of a file as a formatted string."""
    try:
        mod_time = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Unknown"


def find_backup_files(game_path: str) -> List[str]:
    """Find all backup files in a game directory."""
    backup_files = []
    if not os.path.exists(game_path):
        return backup_files
    
    for root, _, files in os.walk(game_path):
        for file in files:
            if file.endswith(".backup001") or ".backup" in file:
                backup_files.append(os.path.join(root, file))
    
    return backup_files


def validate_game_directory(directory: str, edition_name: str) -> bool:
    """Validate that a directory contains a valid game installation."""
    if not os.path.exists(directory):
        return False
    
    # Check for expected files based on edition
    if edition_name == "Stronghold Definitive Edition":
        exe_path = os.path.join(directory, "Stronghold 1 Definitive Edition.exe")
        data_folder = os.path.join(directory, "Stronghold 1 Definitive Edition_Data")
    elif edition_name == "Stronghold Crusader Definitive Edition":
        exe_path = os.path.join(directory, "Stronghold Crusader Definitive Edition.exe")
        data_folder = os.path.join(directory, "Stronghold Crusader Definitive Edition_Data")
    else:
        # Fallback: just check for any .exe and _Data folder
        exe_path = None
        data_folder = None
        for file in os.listdir(directory):
            if file.endswith(".exe"):
                exe_path = os.path.join(directory, file)
            if file.endswith("_Data") and os.path.isdir(os.path.join(directory, file)):
                data_folder = os.path.join(directory, file)
    
    return ((exe_path and os.path.exists(exe_path)) or 
            (data_folder and os.path.isdir(data_folder)))


def ensure_directory_exists(path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)


def get_relative_path(full_path: str, base_path: str) -> str:
    """Get the relative path from base_path to full_path."""
    try:
        return os.path.relpath(full_path, base_path)
    except ValueError:
        return full_path