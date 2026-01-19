#!/bin/bash
# Launch Citation Cross-Checker GUI on macOS/Linux
# Created by: Osman Sabri Kiratli

# Change to the directory where this script is located
cd "$(dirname "$0")"

# Run the GUI application
python3 src/citation_cross_checker/gui.py
