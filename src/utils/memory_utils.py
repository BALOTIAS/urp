"""
Memory utility functions for monitoring and managing memory usage.
"""

import gc
from typing import Optional, Callable
from ..config.settings import settings

# Try to import psutil, but don't fail if it's not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MemoryUtils:
    """Utility class for memory management."""
    
    @staticmethod
    def get_memory_usage_mb() -> float:
        """Get current memory usage in megabytes.
        
        Returns:
            Memory usage in megabytes.
        """
        if not PSUTIL_AVAILABLE:
            return 0.0
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024
        except Exception:
            return 0.0
    
    @staticmethod
    def log_memory_usage(logger: Optional[Callable] = None) -> None:
        """Log current memory usage.
        
        Args:
            logger: Logger function to use. Defaults to print.
        """
        if logger is None:
            logger = print
        
        memory_mb = MemoryUtils.get_memory_usage_mb()
        logger(f"[UNOFFICIAL RETRO PATCH] Memory usage: {memory_mb:.1f} MB")
    
    @staticmethod
    def check_memory_threshold() -> bool:
        """Check if memory usage exceeds the threshold.
        
        Returns:
            True if memory usage is above threshold, False otherwise.
        """
        memory_mb = MemoryUtils.get_memory_usage_mb()
        return memory_mb > settings.MAX_MEMORY_USAGE_MB
    
    @staticmethod
    def force_garbage_collection() -> None:
        """Force garbage collection to free memory."""
        gc.collect()
    
    @staticmethod
    def cleanup_memory_if_needed() -> None:
        """Clean up memory if usage is above threshold."""
        if MemoryUtils.check_memory_threshold():
            MemoryUtils.force_garbage_collection()
    
    @staticmethod
    def get_memory_info() -> dict:
        """Get detailed memory information.
        
        Returns:
            Dictionary containing memory information.
        """
        if not PSUTIL_AVAILABLE:
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "percent": 0.0,
                "available_mb": 0.0
            }
        
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": memory_percent,
                "available_mb": psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception:
            return {
                "rss_mb": 0.0,
                "vms_mb": 0.0,
                "percent": 0.0,
                "available_mb": 0.0
            }