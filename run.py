#!/usr/bin/env python3
"""
Simple launcher for Auto Mouse Move
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from mm.main import main

if __name__ == "__main__":
    sys.exit(main())