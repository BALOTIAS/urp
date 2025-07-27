#!/usr/bin/env python3
"""
GUI entry point for the Unofficial Retro Patch application.

This script launches the graphical user interface.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui_app import main

if __name__ == "__main__":
    main()