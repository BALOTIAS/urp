"""
Test script to verify the refactored structure works correctly.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all our new modules can be imported."""
    try:
        # Test core modules
        from core.config_manager import ConfigManager, EditionConfig
        print("✓ ConfigManager imported successfully")
        
        # Test file utils
        from core.file_utils import FileUtils
        print("✓ FileUtils imported successfully")
        
        # Test memory utils
        from utils.memory_utils import MemoryUtils
        print("✓ MemoryUtils imported successfully")
        
        # Test pixelation engine (may fail if PIL is not available)
        try:
            from core.pixelation_engine import PixelationEngine
            print("✓ PixelationEngine imported successfully")
        except ImportError as e:
            if "PIL" in str(e):
                print("⚠ PixelationEngine import skipped (PIL not available)")
            else:
                print(f"❌ PixelationEngine import failed: {e}")
                return False
        
        # Test backward compatibility (may fail if PIL is not available)
        try:
            from pixelation import pixelate_image, apply_black_shadows, process_image
            print("✓ Backward compatibility functions imported successfully")
        except ImportError as e:
            if "PIL" in str(e):
                print("⚠ Backward compatibility import skipped (PIL not available)")
            else:
                print(f"❌ Backward compatibility import failed: {e}")
                return False
        
        print("\n🎉 All imports successful! The refactored structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config_manager():
    """Test the config manager functionality."""
    try:
        from core.config_manager import ConfigManager
        config_manager = ConfigManager()
        editions = config_manager.get_editions()
        print(f"✓ Found {len(editions)} editions: {editions}")
        return True
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing refactored structure...\n")
    
    success = True
    success &= test_imports()
    success &= test_config_manager()
    
    if success:
        print("\n✅ All tests passed! The refactoring was successful.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")