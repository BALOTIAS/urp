"""
Test script for the refactored Unofficial Retro Patch application.
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from src.config.settings import settings
        print("✓ Settings imported successfully")
        
        from src.config.config_manager import ConfigManager
        print("✓ ConfigManager imported successfully")
        
        from src.utils.file_utils import FileUtils
        print("✓ FileUtils imported successfully")
        
        from src.utils.memory_utils import MemoryUtils
        print("✓ MemoryUtils imported successfully")
        
        from src.utils.validation_utils import ValidationUtils
        print("✓ ValidationUtils imported successfully")
        
        from src.processing.image_processor import ImageProcessor
        print("✓ ImageProcessor imported successfully")
        
        from src.processing.pixelation_processor import PixelationProcessor
        print("✓ PixelationProcessor imported successfully")
        
        from src.game.unity_processor import UnityProcessor
        print("✓ UnityProcessor imported successfully")
        
        from src.game.asset_manager import AssetManager
        print("✓ AssetManager imported successfully")
        
        from src.core.application import Application
        print("✓ Application imported successfully")
        
        print("\nAll imports successful! ✓")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration functionality."""
    print("\nTesting configuration...")
    
    try:
        from src.config.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        editions = config_manager.get_editions()
        print(f"✓ Found {len(editions)} editions: {editions}")
        
        if editions:
            config = config_manager.get_edition_config(editions[0])
            print(f"✓ Configuration loaded for {editions[0]}")
            print(f"  - Target folder: {config.get('target_folder', 'Not set')}")
            print(f"  - Resize amount: {config.get('resize_amount', 'Not set')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_application():
    """Test application initialization."""
    print("\nTesting application...")
    
    try:
        from src.core.application import Application
        
        app = Application()
        available_editions = app.get_available_editions()
        print(f"✓ Application initialized with {len(available_editions)} editions")
        
        return True
        
    except ImportError as e:
        print(f"✗ Application test failed (missing dependency): {e}")
        return False
    except Exception as e:
        print(f"✗ Application test failed: {e}")
        return False

def test_utilities():
    """Test utility functions."""
    print("\nTesting utilities...")
    
    try:
        from src.utils.validation_utils import ValidationUtils
        from src.utils.memory_utils import MemoryUtils
        
        # Test memory utils
        memory_mb = MemoryUtils.get_memory_usage_mb()
        print(f"✓ Memory usage: {memory_mb:.1f} MB")
        
        # Test validation utils
        is_valid, errors = ValidationUtils.validate_resize_amount(0.5)
        print(f"✓ Resize amount validation: {'Valid' if is_valid else 'Invalid'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Utilities test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing refactored Unofficial Retro Patch application...\n")
    
    tests = [
        test_imports,
        test_configuration,
        test_application,
        test_utilities
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The refactored application is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)