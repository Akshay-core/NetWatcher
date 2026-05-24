#!/usr/bin/env python3
"""
netwatcher.py — Main entry point.

Usage:
  python netwatcher.py scan --local
  python netwatcher.py scan --target 192.168.1.0/24 --open
  python netwatcher.py history
  python netwatcher.py report
  python netwatcher.py check
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from netwatcher.cli import app

if __name__ == "__main__":
    app()
