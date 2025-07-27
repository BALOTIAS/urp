"""
Unity asset file processing operations.
"""

import os
import warnings
from typing import Dict, List, Optional, Callable, Any, Tuple
from ..config.settings import settings
from ..utils.memory_utils import MemoryUtils
from ..processing.pixelation_processor import PixelationProcessor

# Try to import UnityPy, but don't fail if it's not available
try:
    import UnityPy
    UNITYPY_AVAILABLE = True
except ImportError:
    UNITYPY_AVAILABLE = False


class UnityProcessor:
    """Handles Unity asset file processing operations."""
    
    def __init__(self, logger: Optional[Callable] = None):
        """Initialize the Unity processor.
        
        Args:
            logger: Logger function to use for output. Defaults to print.
        """
        self.logger = logger or print
        self.pixelation_processor = PixelationProcessor(logger)
    
    def load_asset_file(self, asset_file: str) -> Optional[Any]:
        """Load a Unity asset file.
        
        Args:
            asset_file: Path to the asset file.
            
        Returns:
            UnityPy environment object if successful, None otherwise.
        """
        if not UNITYPY_AVAILABLE:
            self.logger("[UNOFFICIAL RETRO PATCH] UnityPy not available")
            return None
        
        try:
            return UnityPy.load(asset_file)
        except Exception as e:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Failed to load asset file '{asset_file}': {e}")
            return None
    
    def get_texture_objects(self, env: Any) -> List[Any]:
        """Get all texture objects from a Unity environment.
        
        Args:
            env: UnityPy environment object.
            
        Returns:
            List of texture objects.
        """
        return [obj for obj in env.objects if obj.type.name == "Texture2D"]
    
    def process_asset_file(
        self,
        asset_file: str,
        pixelate_entries: List[Dict[str, Any]],
        resize_amount: float,
        black_shadows: bool = False,
        debug_folder: Optional[str] = None
    ) -> Tuple[List[Any], Optional[str]]:
        """Process an asset file and pixelate specified textures.
        
        Args:
            asset_file: Path to the asset file.
            pixelate_entries: List of dictionaries containing pixelation information.
            resize_amount: Resize amount for pixelation.
            black_shadows: Whether to apply black shadows.
            debug_folder: Optional debug folder for saving processed images.
            
        Returns:
            Tuple of (modified_objects, temp_file_path).
        """
        self.logger(f"[UNOFFICIAL RETRO PATCH] Processing asset file: {os.path.basename(asset_file)}")
        
        # Load the asset file
        env = self.load_asset_file(asset_file)
        if not env:
            return [], None
        
        modified_objects = []
        processed_count = 0
        
        # Process each texture object
        for obj in env.objects:
            if obj.type.name != "Texture2D":
                continue
            
            # Check if this object matches any of the textures we need to process
            for pixelate_entry in pixelate_entries:
                asset_name = pixelate_entry["asset_name"]
                
                try:
                    data = obj.read()
                    
                    if not hasattr(data, "m_Name") or data.m_Name != asset_name:
                        continue
                    
                    if not hasattr(data, "image"):
                        warnings.warn(f"[UNOFFICIAL RETRO PATCH] {asset_name} in {asset_file} does not have an image attribute.")
                        continue
                    
                    processed_count += 1
                    self.logger(f"[UNOFFICIAL RETRO PATCH] Pixelating texture: {asset_name}")
                    
                    # Process the image
                    mask_file = pixelate_entry.get("mask_file")
                    data.image = self.pixelation_processor.process_image(
                        image=data.image,
                        resize_amount=resize_amount,
                        mask_file=mask_file,
                        asset_name=asset_name,
                        black_shadows=black_shadows
                    )
                    
                    data.save()
                    modified_objects.append(obj)
                    
                    # Save debug image if debug folder is specified
                    if debug_folder and settings.DEBUG_ENABLED:
                        self._save_debug_image(data.image, asset_name, debug_folder, pixelate_entry)
                    
                    self.logger(f"[UNOFFICIAL RETRO PATCH] Successfully pixelated {asset_name}")
                    
                except Exception as e:
                    warnings.warn(f"Failed to pixelate {asset_name} in {asset_file}: {e}")
        
        if processed_count == 0:
            self.logger(f"[UNOFFICIAL RETRO PATCH] No textures to process in {asset_file}")
        else:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Modified {len(modified_objects)} objects in {asset_file}")
        
        # Save the modified asset file to temp location
        temp_file = self._save_temp_asset_file(env, asset_file)
        
        return modified_objects, temp_file
    
    def _save_debug_image(
        self,
        image: Any,
        asset_name: str,
        debug_folder: str,
        pixelate_entry: Dict[str, Any]
    ) -> None:
        """Save a debug image to the debug folder.
        
        Args:
            image: PIL Image object to save.
            asset_name: Name of the asset.
            debug_folder: Debug folder path.
            pixelate_entry: Pixelation entry containing asset information.
        """
        try:
            asset_dir = pixelate_entry.get("asset_dir", "")
            asset = pixelate_entry.get("asset", "")
            
            debug_path = os.path.join(debug_folder, asset_dir, asset)
            os.makedirs(os.path.dirname(debug_path), exist_ok=True)
            image.save(debug_path)
            
            self.logger(f"[UNOFFICIAL RETRO PATCH | DEBUG] Successfully exported pixelated {asset_name} in {debug_path}")
        except Exception as e:
            warnings.warn(f"Failed to save debug image for {asset_name}: {e}")
    
    def _save_temp_asset_file(self, env: Any, asset_file: str) -> Optional[str]:
        """Save the modified asset file to a temporary location.
        
        Args:
            env: UnityPy environment object.
            asset_file: Original asset file path.
            
        Returns:
            Path to the temporary file, or None if save failed.
        """
        temp_file = asset_file + ".tmp"
        
        try:
            self.logger(f"[UNOFFICIAL RETRO PATCH] Saving modified asset file to: {temp_file}")
            
            with open(temp_file, "wb") as f:
                f.write(env.file.save())
            
            # Verify the temp file was created
            if os.path.exists(temp_file):
                file_size = os.path.getsize(temp_file)
                self.logger(f"[UNOFFICIAL RETRO PATCH] Temporary file created: {temp_file} ({file_size} bytes)")
                return temp_file
            else:
                raise Exception("Temporary file was not created")
                
        except Exception as e:
            warnings.warn(f"Failed to save modified asset file '{asset_file}': {e}")
            return None
    
    def log_memory_usage(self) -> None:
        """Log current memory usage."""
        MemoryUtils.log_memory_usage(self.logger)
    
    def cleanup_memory_if_needed(self) -> None:
        """Clean up memory if usage is above threshold."""
        MemoryUtils.cleanup_memory_if_needed()