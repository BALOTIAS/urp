"""
Main pixelation processing workflow.
"""

import os
import warnings
from typing import Optional, Callable, Dict, Any, List
from PIL import Image
from ..config.settings import settings
from ..utils.memory_utils import MemoryUtils
from .image_processor import ImageProcessor


class PixelationProcessor:
    """Handles the main pixelation processing workflow."""
    
    def __init__(self, logger: Optional[Callable] = None):
        """Initialize the pixelation processor.
        
        Args:
            logger: Logger function to use for output. Defaults to print.
        """
        self.logger = logger or print
    
    def process_image(
        self,
        image: Image.Image,
        resize_amount: float,
        mask_file: Optional[str] = None,
        asset_name: Optional[str] = None,
        black_shadows: bool = False
    ) -> Image.Image:
        """Process an image with pixelation, offset correction, optional masking, and black shadows.
        
        Args:
            image: PIL Image object (RGBA).
            resize_amount: Float between 0 and 1.
            mask_file: Path to mask file or None.
            asset_name: Name of the asset (for logging).
            black_shadows: Boolean to enable black shadows feature.
            
        Returns:
            Processed PIL Image.
        """
        file_name = asset_name or os.path.basename(mask_file) if mask_file else "unknown"

        # Extract alpha mask
        alpha_mask = image.split()[-1].convert("L")
        hard_alpha_mask = alpha_mask.point(lambda p: 255 if p > 0 else 0)

        # Apply pixelation
        pixelated = ImageProcessor.pixelate_image(image, resize_amount)

        # Apply offset correction (commented out as it doesn't work well)
        # corrected = ImageProcessor.apply_offset_correction(pixelated, resize_amount)

        # Apply mask if it exists, otherwise generate from alpha
        if mask_file and os.path.exists(mask_file):
            custom_mask = ImageProcessor.load_image_safely(mask_file)
            if custom_mask:
                custom_mask = custom_mask.convert("L")
                custom_mask.paste(hard_alpha_mask, (0, 0))  # Paste the original hard alpha mask
                final_image = ImageProcessor.apply_mask(pixelated, custom_mask)
                self.logger(f"[UNOFFICIAL RETRO PATCH] Pixelated {file_name} with mask...")
            else:
                final_image = ImageProcessor.apply_mask(pixelated, hard_alpha_mask)
                warnings.warn(f"[UNOFFICIAL RETRO PATCH] Failed to load mask for {file_name}, using alpha channel.")
        else:
            # Use the alpha channel as a smooth mask for blending
            final_image = ImageProcessor.apply_mask(pixelated, hard_alpha_mask)
            if asset_name:
                warnings.warn(f"[UNOFFICIAL RETRO PATCH] Pixelated {file_name} without custom mask, using alpha channel as mask.")

        # Restore original alpha
        final_image.putalpha(alpha_mask)

        # Apply black shadows if enabled
        if black_shadows:
            final_image = ImageProcessor.apply_black_shadows(final_image)
            if asset_name:
                self.logger(f"[UNOFFICIAL RETRO PATCH] Applied black shadows to {file_name}")

        return final_image
    
    def validate_processing_params(
        self,
        resize_amount: float,
        mask_file: Optional[str] = None
    ) -> List[str]:
        """Validate processing parameters.
        
        Args:
            resize_amount: Resize amount to validate.
            mask_file: Optional mask file path to validate.
            
        Returns:
            List of validation errors.
        """
        errors = []
        
        # Validate resize amount
        if resize_amount < settings.MIN_RESIZE_AMOUNT or resize_amount > settings.MAX_RESIZE_AMOUNT:
            errors.append(f"Resize amount must be between {settings.MIN_RESIZE_AMOUNT} and {settings.MAX_RESIZE_AMOUNT}")
        
        # Validate mask file if provided
        if mask_file and not os.path.exists(mask_file):
            errors.append(f"Mask file does not exist: {mask_file}")
        
        return errors
    
    def log_memory_usage(self) -> None:
        """Log current memory usage."""
        MemoryUtils.log_memory_usage(self.logger)
    
    def cleanup_memory_if_needed(self) -> None:
        """Clean up memory if usage is above threshold."""
        MemoryUtils.cleanup_memory_if_needed()