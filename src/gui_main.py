"""
GUI entry point for the Unofficial Retro Patch application.
"""

import os
import sys
import tkinter as tk
from dotenv import load_dotenv
from unitypy_fixes import patch_unitypy
from .gui.main_window import MainWindow


def main():
    """Main entry point for the GUI application."""
    # Load environment variables
    load_dotenv()
    
    # Patch UnityPy
    patch_unitypy()
    
    # Create and run GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()