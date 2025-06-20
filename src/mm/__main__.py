#!/usr/bin/env python3
"""
Entry point for Auto Mouse Move application when run as a module
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import mm modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mm.main import main

if __name__ == "__main__":
    sys.exit(main())