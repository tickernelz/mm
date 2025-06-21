# Auto Mouse Move

A configurable Python application that prevents your system from going idle by automatically moving the mouse cursor and scrolling when the system has been idle for a specified period.

## Features

- **Configurable idle detection**: Set custom idle thresholds
- **Multiple movement patterns**: Random, circular, or linear mouse movements
- **Scroll support**: Optional mouse wheel scrolling
- **System tray integration**: Runs in background with tray icon
- **GUI configuration**: Easy-to-use interface for all settings
- **Activity logging**: Track when activities are performed
- **macOS optimized**: Proper idle detection for macOS 15+
- **Process name spoofing**: Disguises the process name for privacy

## Requirements

- Python 3.11+
- macOS 15+ (optimized for macOS, but should work on other platforms)
- PyQt6
- PyAutoGUI
- psutil

## Installation

### Download Pre-built Executables (Recommended)

Download the latest release for your Mac from the [Releases page](../../releases/latest):

- **macOS (Intel)**: `telek-macos-x86_64.zip`
- **macOS (Apple Silicon)**: `telek-macos-arm64.zip` 

#### Installation Instructions:
1. Download the appropriate file for your Mac:
   - **Intel Macs**: Download the x86_64 version
   - **Apple Silicon Macs (M1/M2/M3)**: Download the arm64 version
2. Extract the zip file
3. Run the .app file
4. Grant accessibility permissions when prompted

### From Source

#### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mm

# Install dependencies with uv
uv sync

# Run the application
uv run python run.py
```

#### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd mm

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

## Building Executable

### Automated Builds (GitHub Actions)

This project uses GitHub Actions to automatically build executables for multiple platforms and architectures:

- **Releases**: Push a version tag (e.g., `v1.0.0`) to trigger automatic builds and release creation
- **Test Builds**: Push to main branch or create PR to test builds without creating releases

See [`.github/workflows/README.md`](.github/workflows/README.md) for detailed information about the build system.

### Manual Build

To build a standalone executable locally using PyInstaller:

```bash
# Install build dependencies
pip install PyInstaller Pillow

# Run the build script
./build.sh
```

The executable will be created in the `dist/` directory.

## Usage

### GUI Mode

1. Run the application: `python run.py`
2. Configure settings in the GUI:
   - **Idle Threshold**: Time before considering system idle (default: 5 minutes)
   - **Move Interval**: How often to perform activity when idle (default: 30 seconds)
   - **Movement Distance**: How far to move the mouse (default: 5 pixels)
   - **Movement Pattern**: Random, circular, or linear movement
   - **Scroll Settings**: Enable/disable scrolling and set scroll amount
3. Enable the "Enable Auto Mouse Move" checkbox
4. Minimize to system tray or keep window open

### System Tray

- **Double-click**: Show/hide main window
- **Middle-click**: Toggle enable/disable
- **Right-click**: Access context menu with options:
  - Show/Hide Window
  - Enable/Disable
  - Force Activity
  - Quit

## Configuration

Settings are automatically saved to `~/.config/auto-mouse-move/config.json` and include:

- `idle_threshold`: Seconds before system is considered idle (default: 300)
- `move_interval`: Seconds between activities when idle (default: 30)
- `move_distance`: Pixels to move mouse (default: 5)
- `movement_pattern`: "random", "circular", or "linear" (default: "random")
- `scroll_enabled`: Enable mouse scrolling (default: true)
- `scroll_amount`: Number of scroll clicks (default: 3)
- `mouse_move_enabled`: Enable mouse movement (default: true)
- `check_interval`: How often to check idle status in seconds (default: 5)

## macOS Permissions

On macOS, you may need to grant accessibility permissions:

1. Go to System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from the left sidebar
3. Click the lock to make changes
4. Add your terminal application or the built executable
5. Ensure it's checked/enabled

## Process Name Spoofing

The application attempts to disguise its process name as "SystemUIServer" to blend in with system processes. This requires the `setproctitle` package, which is optional.

## Troubleshooting

### Idle Detection Issues

If idle detection isn't working properly:
1. Check that you have the necessary permissions on macOS
2. Try running with administrator privileges
3. Check the activity log for error messages

### Mouse Movement Not Working

1. Ensure PyAutoGUI has the necessary permissions
2. Check that the fail-safe isn't triggered (move mouse to top-left corner)
3. Verify screen resolution detection is working

### System Tray Not Showing

1. Ensure your desktop environment supports system tray
2. Try restarting the application
3. Check if other tray applications are working

## Development

### Project Structure

```
src/mm/
├── __init__.py          # Package initialization
├── main.py              # Main entry point
├── config.py            # Configuration management
├── idle_detector.py     # macOS idle time detection
├── mouse_controller.py  # Mouse movement and scrolling
├── gui.py               # Main GUI window
└── system_tray.py       # System tray management
```

### Running in Development

```bash
# Install in development mode
uv sync --dev

# Run with debugging
uv run python -m mm.main

# Run tests (if available)
uv run pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Notes

### Antivirus False Positives
PyInstaller executables are sometimes flagged by antivirus software as suspicious. This is a common false positive with packaged Python applications. If you encounter this:
- The source code is available for review in this repository
- You can build from source using the instructions above
- Add an exception for the executable in your antivirus software

### Privacy and Process Spoofing
The application includes optional process name spoofing to disguise itself as a system process. This is purely for privacy and does not affect functionality. The spoofing can be disabled by removing the `setproctitle` dependency.

## Disclaimer

This tool is designed to prevent system idle timeouts for legitimate purposes such as preventing screen savers during presentations or long-running tasks. Please use responsibly and in accordance with your organization's policies.