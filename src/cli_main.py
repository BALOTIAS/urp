"""
CLI entry point for the Unofficial Retro Patch application.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from unitypy_fixes import patch_unitypy
from .core.application import Application


def main():
    """Main entry point for the CLI application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Unofficial Retro Patch - Apply pixelation to Stronghold textures")
    parser.add_argument("--edition", "-e", default="Stronghold Definitive Edition",
                       help="Game edition to process")
    parser.add_argument("--black-shadows", "-b", action="store_true",
                       help="Apply black shadows effect")
    parser.add_argument("--list-editions", "-l", action="store_true",
                       help="List available editions")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Patch UnityPy
    patch_unitypy()
    
    # Create application instance
    app = Application()
    
    # List editions if requested
    if args.list_editions:
        print("Available editions:")
        for edition in app.get_available_editions():
            print(f"  - {edition}")
        return
    
    print(f"\n[UNOFFICIAL RETRO PATCH] Starting pixelation process for {args.edition}...")
    
    try:
        # Validate edition
        if args.edition not in app.get_available_editions():
            print(f"Error: Edition '{args.edition}' is not available.")
            print("Available editions:")
            for edition in app.get_available_editions():
                print(f"  - {edition}")
            sys.exit(1)
        
        # Validate configuration
        validation_errors = app.validate_edition_config(args.edition)
        if validation_errors:
            print(f"Configuration errors for {args.edition}:")
            for error in validation_errors:
                print(f"  - {error}")
            sys.exit(1)
        
        # Process the edition
        files_to_replace = app.pixelate_edition(args.edition, args.black_shadows)
        
        if files_to_replace:
            print(f"\n[UNOFFICIAL RETRO PATCH] Replacing {len(files_to_replace)} files...")
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