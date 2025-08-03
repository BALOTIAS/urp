"""
Image utilities for the GUI components.
"""

import os
import sys
from PIL import Image, ImageTk
from typing import Optional, Tuple


class ImageUtils:
    """Handles image loading and processing for the GUI."""
    
    @staticmethod
    def load_icon_image(icon_name: str, size: Optional[Tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
        """Load an icon image for the GUI."""
        try:
            if getattr(sys, "frozen", False):
                application_path = sys._MEIPASS
                icon_path = os.path.join(
                    application_path,
                    "assets/icon",
                    f"{icon_name}.ico" if sys.platform == "win32" else f"{icon_name}.png",
                )
            else:
                icon_path = os.path.join(
                    "assets/icon", 
                    f"{icon_name}.ico" if sys.platform == "win32" else f"{icon_name}.png"
                )
            
            if os.path.exists(icon_path):
                if size:
                    img = Image.open(icon_path)
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
                else:
                    return ImageTk.PhotoImage(file=icon_path)
            
            return None
        except Exception as e:
            print(f"Could not load icon {icon_name}: {e}")
            return None
    
    @staticmethod
    def load_edition_image(edition_name: str, size: Tuple[int, int] = (96, 48)) -> Optional[ImageTk.PhotoImage]:
        """Load an edition image for the GUI."""
        try:
            # Map edition names to image files
            edition_images = {
                "Stronghold Definitive Edition": "shde.png",
                "Stronghold Crusader Definitive Edition": "shcde.png"
            }
            
            image_file = edition_images.get(edition_name, "shde.png")
            image_path = os.path.join("assets/firefly", image_file)
            
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            
            return None
        except Exception as e:
            print(f"Could not load edition image for {edition_name}: {e}")
            return None
    
    @staticmethod
    def load_placeholder_image(edition_name: str) -> Optional[Image.Image]:
        """Load a placeholder image for preview."""
        try:
            # Map edition names to screenshot files
            screenshot_files = {
                "Stronghold Definitive Edition": "shde-screenshot.jpg",
                "Stronghold Crusader Definitive Edition": "shcde-screenshot.jpg"
            }
            
            screenshot_file = screenshot_files.get(edition_name, "shde-screenshot.jpg")
            screenshot_path = os.path.join("assets/firefly", screenshot_file)
            
            if os.path.exists(screenshot_path):
                return Image.open(screenshot_path)
            
            return None
        except Exception as e:
            print(f"Could not load placeholder image for {edition_name}: {e}")
            return None
    
    @staticmethod
    def create_preview_image(
        base_image: Image.Image, 
        pixelation_amount: float, 
        black_shadows: bool = False
    ) -> Image.Image:
        """Create a preview image with pixelation applied."""
        try:
            from core.pixelation_engine import PixelationEngine
            
            # Apply pixelation
            pixelated = PixelationEngine.pixelate_image(base_image, pixelation_amount)
            
            # Apply black shadows if enabled
            if black_shadows:
                pixelated = PixelationEngine.apply_black_shadows(pixelated)
            
            # Make preview square (crop to square center)
            width, height = pixelated.size
            side = min(width, height)
            left = (width - side) // 1.8
            top = (height - side) // 2
            right = left + side
            bottom = top + side
            
            return pixelated.crop((left, top, right, bottom))
            
        except Exception as e:
            print(f"Could not create preview image: {e}")
            return base_image