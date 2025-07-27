#!/usr/bin/env python3
"""
Test script for the refactored Unofficial Retro Patch application.

This script verifies that the refactored structure works correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from src.core.config import config_manager, EditionConfig
        print("✓ Core config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import core config: {e}")
        return False
    
    try:
        from src.core.unity_processor import UnityProcessor, PixelateEntry
        print("✓ Unity processor module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import unity processor: {e}")
        return False
    
    try:
        from src.core.file_utils import is_file_locked, log_memory_usage
        print("✓ File utils module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import file utils: {e}")
        return False
    
    try:
        from src.image_processing import pixelate_image, apply_black_shadows, process_image
        print("✓ Image processing module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import image processing: {e}")
        return False
    
    try:
        from src.utils.unitypy_patch import patch_unitypy
        print("✓ UnityPy patch module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import UnityPy patch: {e}")
        return False
    
    return True

def test_config_manager():
    """Test the configuration manager functionality."""
    print("\nTesting configuration manager...")
    
    try:
        # Test getting available editions
        editions = config_manager.get_available_editions()
        print(f"✓ Found {len(editions)} editions: {editions}")
        
        # Test getting a specific edition config (if available)
        if editions:
            try:
                config = config_manager.get_edition_config(editions[0])
                print(f"✓ Successfully loaded config for '{editions[0]}'")
                print(f"  - Target folder: {config.target_folder}")
                print(f"  - Assets folder: {config.assets_folder}")
                print(f"  - Resize amount: {config.resize_amount}")
                print(f"  - Files to pixelate: {len(config.pixelate_files)}")
            except Exception as e:
                print(f"⚠ Could not load config for '{editions[0]}': {e}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration manager test failed: {e}")
        return False

def test_image_processing():
    """Test the image processing functionality."""
    print("\nTesting image processing...")
    
    try:
        from PIL import Image
        import numpy as np
        
        # Create a test image
        test_image = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
        
        # Test pixelation
        pixelated = pixelate_image(test_image, 0.5)
        print("✓ Pixelation function works")
        
        # Test black shadows
        shadowed = apply_black_shadows(test_image)
        print("✓ Black shadows function works")
        
        # Test full processing
        processed = process_image(test_image, 0.5, asset_name="test")
        print("✓ Full image processing works")
        
        return True
    except Exception as e:
        print(f"✗ Image processing test failed: {e}")
        return False

def test_unity_processor():
    """Test the Unity processor functionality."""
    print("\nTesting Unity processor...")
    
    try:
        processor = UnityProcessor()
        print("✓ Unity processor created successfully")
        
        # Test file grouping (with dummy data)
        test_files = ["test1.png", "test2.png"]
        grouped = processor.group_pixelate_files(
            test_files, 
            "/dummy/path", 
            "assets", 
            "masks"
        )
        print("✓ File grouping function works")
        
        return True
    except Exception as e:
        print(f"✗ Unity processor test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Unofficial Retro Patch - Refactored Structure Test ===\n")
    
    tests = [
        test_imports,
        test_config_manager,
        test_image_processing,
        test_unity_processor,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The refactored structure is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)