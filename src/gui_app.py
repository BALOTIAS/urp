"""
GUI entry point for the Unofficial Retro Patch application.

This module provides the graphical user interface for the application.
"""

import tkinter as tk
from .gui.main_window import MainWindow
from .utils.unitypy_patch import patch_unitypy


def main():
    """Main entry point for GUI application."""
    # Apply UnityPy patches
    patch_unitypy()
    
    # Create and run the GUI
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()