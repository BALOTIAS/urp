"""
Image processing functionality for the Unofficial Retro Patch application.

This module handles image manipulation, pixelation effects, and texture processing
for game assets.
"""

from .pixelation import (
    pixelate_image,
    apply_black_shadows,
    apply_offset_correction,
    process_image
)

__all__ = [
    'pixelate_image',
    'apply_black_shadows', 
    'apply_offset_correction',
    'process_image'
]