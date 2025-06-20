#!/bin/bash
"""
Build script for Auto Mouse Move using PyInstaller
"""

set -e  # Exit on any error

echo "Building Auto Mouse Move..."

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$PROJECT_ROOT/src"
DIST_DIR="$PROJECT_ROOT/dist"
BUILD_DIR="$PROJECT_ROOT/build"
VENV_DIR="$PROJECT_ROOT/.venv"

# Function to detect Python executable
detect_python() {
    if [[ -f "$VENV_DIR/bin/python" ]]; then
        echo "$VENV_DIR/bin/python"
    elif [[ -f "$VENV_DIR/bin/python3" ]]; then
        echo "$VENV_DIR/bin/python3"
    elif command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        echo "ERROR: No Python executable found!" >&2
        exit 1
    fi
}

# Detect Python executable
PYTHON_EXEC=$(detect_python)
echo "Using Python: $PYTHON_EXEC"

# Check if virtual environment exists and activate it
if [[ -d "$VENV_DIR" ]]; then
    echo "Found virtual environment at $VENV_DIR"
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        echo "Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
        PYTHON_EXEC="python"  # Use the activated python
    fi
else
    echo "No virtual environment found, using system Python"
fi

# Verify Python and required packages
echo "Checking Python version..."
$PYTHON_EXEC --version

echo "Checking required packages..."
if ! $PYTHON_EXEC -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    $PYTHON_EXEC -m pip install PyInstaller
fi

if ! $PYTHON_EXEC -c "import PIL" 2>/dev/null; then
    echo "Pillow not found. Installing for icon creation..."
    $PYTHON_EXEC -m pip install Pillow
fi

if ! $PYTHON_EXEC -c "import setproctitle" 2>/dev/null; then
    echo "setproctitle not found. Installing for process name spoofing..."
    $PYTHON_EXEC -m pip install setproctitle
fi

# Clean previous builds
echo "Cleaning previous builds..."
if [[ -d "$DIST_DIR" ]]; then
    rm -rf "$DIST_DIR"
fi
if [[ -d "$BUILD_DIR" ]]; then
    rm -rf "$BUILD_DIR"
fi

# Create resources directory
RESOURCES_DIR="$SRC_DIR/mm/resources"
mkdir -p "$RESOURCES_DIR"

# Create icon if it doesn't exist
ICON_PATH="$RESOURCES_DIR/icon.icns"
if [[ ! -f "$ICON_PATH" ]]; then
    echo "Creating default icon..."
    create_default_icon
fi

# Function to create default icon
create_default_icon() {
    $PYTHON_EXEC << 'EOF'
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
    import subprocess
    
    # Create a simple icon
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple mouse cursor
    # Main body
    draw.ellipse([50, 50, size-50, size-200], fill=(100, 150, 255, 255), outline=(0, 0, 0, 255), width=5)
    
    # Button separator
    draw.rectangle([size//2-10, 50, size//2+10, 150], fill=(0, 0, 0, 255))
    
    # Save as PNG first
    icon_path = Path("src/mm/resources/icon.icns")
    png_path = icon_path.with_suffix('.png')
    img.save(png_path)
    
    if sys.platform == "darwin":
        # Convert to ICNS on macOS
        try:
            subprocess.run([
                'sips', '-s', 'format', 'icns', str(png_path), '--out', str(icon_path)
            ], check=True)
            png_path.unlink()  # Remove PNG file
            print(f"Created icon: {icon_path}")
        except subprocess.CalledProcessError:
            # Fallback: just use PNG
            png_path.rename(icon_path.with_suffix('.png'))
            print(f"Created PNG icon: {icon_path.with_suffix('.png')}")
    else:
        # On other platforms, use PNG
        png_path.rename(icon_path.with_suffix('.png'))
        print(f"Created PNG icon: {icon_path.with_suffix('.png')}")
        
except ImportError:
    # Create a minimal placeholder
    print("PIL not available, skipping icon creation...")
    with open("src/mm/resources/icon.txt", 'w') as f:
        f.write("Icon placeholder")
EOF
}

# Build with PyInstaller
echo "Running PyInstaller..."

# Determine icon argument
ICON_ARG=""
if [[ -f "$ICON_PATH" ]]; then
    ICON_ARG="--icon=$ICON_PATH"
elif [[ -f "$RESOURCES_DIR/icon.png" ]]; then
    ICON_ARG="--icon=$RESOURCES_DIR/icon.png"
fi

# PyInstaller command with custom spec file for better spoofing
echo "Using custom spec file for enhanced process spoofing..."
$PYTHON_EXEC -m PyInstaller \
    --clean \
    --noconfirm \
    "$PROJECT_ROOT/MouseMover.spec"

# Check if build was successful
EXECUTABLE_PATH=""
if [[ -f "$DIST_DIR/telek" ]]; then
    EXECUTABLE_PATH="$DIST_DIR/telek"
elif [[ -d "$DIST_DIR/telek.app" ]]; then
    EXECUTABLE_PATH="$DIST_DIR/telek.app"
elif [[ -f "$DIST_DIR/MouseMover" ]]; then
    EXECUTABLE_PATH="$DIST_DIR/MouseMover"
else
    echo "ERROR: Build failed - executable not found!" >&2
    echo "Contents of dist directory:"
    ls -la "$DIST_DIR" 2>/dev/null || echo "Dist directory not found"
    exit 1
fi

echo "Build completed successfully!"
echo "Executable created at: $EXECUTABLE_PATH"

# Make executable (on Unix-like systems)
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    if [[ -f "$EXECUTABLE_PATH" ]]; then
        chmod +x "$EXECUTABLE_PATH"
        echo "Made executable file executable"
    elif [[ -d "$EXECUTABLE_PATH" ]]; then
        chmod +x "$EXECUTABLE_PATH/Contents/MacOS/telek" 2>/dev/null || true
        echo "Made app bundle executable"
    fi
fi

# Show file size
if command -v ls &> /dev/null; then
    echo "File size: $(ls -lh "$EXECUTABLE_PATH" | awk '{print $5}')"
fi

echo ""
echo "Build completed! You can run the application with:"
if [[ -d "$EXECUTABLE_PATH" && "$EXECUTABLE_PATH" == *.app ]]; then
    echo "  open '$EXECUTABLE_PATH'"
    echo "  or: '$EXECUTABLE_PATH/Contents/MacOS/telek'"
else
    echo "  '$EXECUTABLE_PATH'"
fi

echo ""
echo "Note: The application uses dynamic process name spoofing at runtime."
echo "Check Activity Monitor - it will appear with a unique generated name like 'CoreDisplayAgent_12ab34cd'."