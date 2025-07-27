"""
Image processing operations for pixelation effects.
"""

import os
from typing import Optional, Tuple
from ..config.settings import settings

# Try to import PIL and numpy, but don't fail if they're not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class ImageProcessor:
    """Handles image processing operations."""
    
    @staticmethod
    def pixelate_image(image: Image.Image, resize_amount: float) -> Image.Image:
        """Apply pixelation effect to an image.
        
        Args:
            image: PIL Image object to pixelate.
            resize_amount: Float between 0 and 1, smaller values mean more pixelation.
            
        Returns:
            PIL Image with pixelation effect applied.
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL (Pillow) is required for image processing")
        
        # Downscale the image
        small_image = image.resize(
            (
                round(image.width * resize_amount),
                round(image.height * resize_amount),
            ),
            Image.Resampling.NEAREST,
        )
        # Upscale back to original size
        return small_image.resize(
            (image.width, image.height),
            Image.Resampling.NEAREST,
        )
    
    @staticmethod
    def apply_black_shadows(image: Image.Image, shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> Image.Image:
        """Apply black shadows to an image by replacing semi-transparent areas with solid black.
        
        Args:
            image: PIL Image object (RGBA).
            shadow_color: Tuple of (R, G, B, A) for shadow color, defaults to black.
            
        Returns:
            PIL Image with black shadows applied.
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL (Pillow) is required for image processing")
        
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for black shadows processing")
        
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Convert to numpy array for faster pixel operations
        img_array = np.array(image)

        # Create boolean mask for pixels that should be replaced
        # Semi-transparent black pixels (shadow-like) (R=0, G=0, B=0, 64 < A < 255)
        mask = (
            (img_array[:, :, 0] == 0) &  # R = 0
            (img_array[:, :, 1] == 0) &  # G = 0
            (img_array[:, :, 2] == 0) &  # B = 0
            (img_array[:, :, 3] > 64) &  # A > 64
            (img_array[:, :, 3] < 255)  # A < 255
        )

        # Apply shadow color to masked pixels
        img_array[mask] = shadow_color

        # Convert back to PIL Image
        return Image.fromarray(img_array, 'RGBA')
    
    @staticmethod
    def apply_offset_correction(pixelated_image: Image.Image, resize_amount: float) -> Image.Image:
        """Apply pixel offset correction based on resize amount to fix spillover issues.
        
        Args:
            pixelated_image: PIL Image object that has been pixelated.
            resize_amount: Float between 0 and 1, used to calculate the offset.
            
        Returns:
            PIL Image with offset correction applied.
        """
        # Calculate required offset
        pixel_offset = round((1 / resize_amount) / 2)

        if pixel_offset <= 0:
            return pixelated_image

        width, height = pixelated_image.size
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        # Main image with offset
        result.paste(pixelated_image, (pixel_offset, pixel_offset))

        # Fix right edge
        right_strip = pixelated_image.crop((0, 0, 1, height))
        for i in range(pixel_offset):
            result.paste(right_strip, (width - 1 - i, pixel_offset))

        # Fix bottom edge
        bottom_strip = pixelated_image.crop((0, 0, width, 1))
        for i in range(pixel_offset):
            result.paste(bottom_strip, (pixel_offset, height - 1 - i))

        # Fix corner pixels
        corner_pixel = pixelated_image.crop((0, 0, 1, 1))
        for i in range(pixel_offset):
            for j in range(pixel_offset):
                result.paste(corner_pixel, (width - 1 - i, height - 1 - j))

        return result
    
    @staticmethod
    def extract_alpha_mask(image: Image.Image) -> Image.Image:
        """Extract alpha mask from an image.
        
        Args:
            image: PIL Image object.
            
        Returns:
            PIL Image containing the alpha mask.
        """
        alpha_mask = image.split()[-1].convert("L")
        return alpha_mask.point(lambda p: 255 if p > 0 else 0)
    
    @staticmethod
    def apply_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
        """Apply a mask to an image.
        
        Args:
            image: PIL Image object to mask.
            mask: PIL Image object containing the mask.
            
        Returns:
            PIL Image with mask applied.
        """
        return Image.composite(image, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask)
    
    @staticmethod
    def load_image_safely(filepath: str) -> Optional[Image.Image]:
        """Load an image file safely with error handling.
        
        Args:
            filepath: Path to the image file.
            
        Returns:
            PIL Image object if successful, None otherwise.
        """
        try:
            if not os.path.exists(filepath):
                return None
            return Image.open(filepath)
        except Exception:
            return None