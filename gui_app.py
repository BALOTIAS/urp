"""
GUI entry point for the Unofficial Retro Patch.
"""

import tkinter as tk
from gui.main_window import RetroPixelatorGUI


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = RetroPixelatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()