"""
Pixelation module for the Unofficial Retro Patch.

This module provides backward compatibility for the pixelation functions.
"""

from core.pixelation_engine import PixelationEngine, pixelate_image, apply_black_shadows, process_image

# Re-export the functions for backward compatibility
__all__ = ['pixelate_image', 'apply_black_shadows', 'process_image', 'PixelationEngine']
