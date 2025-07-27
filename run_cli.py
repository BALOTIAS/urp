#!/usr/bin/env python3
"""
Command-line entry point for the Unofficial Retro Patch application.

This script provides the command-line interface for pixelating game assets.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()