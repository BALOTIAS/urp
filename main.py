"""
Main entry point for the Unofficial Retro Patch.

This module provides the main entry point and maintains backward compatibility.
"""

import os
from dotenv import load_dotenv
from core.main_processor import MainProcessor

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the application."""
    print("\n[UNOFFICIAL RETRO PATCH] Starting pixelation process...")
    
    processor = MainProcessor()
    processor.pixelate_edition("Stronghold Definitive Edition")
    
    print("\n[UNOFFICIAL RETRO PATCH] Finished pixelation process.")


if __name__ == "__main__":
    main()
