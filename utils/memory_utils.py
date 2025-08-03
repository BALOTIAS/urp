"""
Memory utilities for the Unofficial Retro Patch.
"""

import gc
from typing import Optional, Callable

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class MemoryUtils:
    """Handles memory monitoring and management."""
    
    @staticmethod
    def log_memory_usage(logger: Optional[Callable] = None) -> None:
        """Log current memory usage for debugging."""
        if logger is None:
            logger = print
        
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                logger(f"[UNOFFICIAL RETRO PATCH] Memory usage: {memory_mb:.1f} MB")
            except Exception:
                pass  # psutil not working properly
        else:
            logger("[UNOFFICIAL RETRO PATCH] Memory monitoring not available (psutil not installed)")
    
    @staticmethod
    def force_garbage_collection() -> None:
        """Force garbage collection to free memory."""
        gc.collect()
    
    @staticmethod
    def get_memory_usage_mb() -> Optional[float]:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                return memory_info.rss / 1024 / 1024
            except Exception:
                return None
        else:
            return None