"""
Main entry point for the Unofficial Retro Patch application.
"""

import os
import sys
from dotenv import load_dotenv
from unitypy_fixes import patch_unitypy
from .core.application import Application


def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Patch UnityPy
    patch_unitypy()
    
    # Create application instance
    app = Application()
    
    print("\n[UNOFFICIAL RETRO PATCH] Starting pixelation process...")
    
    try:
        # Process the default edition
        files_to_replace = app.pixelate_edition("Stronghold Definitive Edition")
        
        if files_to_replace:
            print("\n[UNOFFICIAL RETRO PATCH] Replacing files...")
            app.replace_files(files_to_replace)
            print("\n[UNOFFICIAL RETRO PATCH] Files replaced successfully!")
        else:
            print("\n[UNOFFICIAL RETRO PATCH] No files to replace.")
            
    except Exception as e:
        print(f"\n[UNOFFICIAL RETRO PATCH] Error during pixelation process: {e}")
        sys.exit(1)
    
    print("\n[UNOFFICIAL RETRO PATCH] Finished pixelation process.")


if __name__ == "__main__":
    main()