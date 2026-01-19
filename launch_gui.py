#!/usr/bin/env python3
"""
Citation Cross-Checker GUI Launcher

Double-click this file to launch the GUI application.
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from citation_cross_checker.gui import main

if __name__ == "__main__":
    main()
