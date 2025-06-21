# GitHub Actions Workflows

This directory contains GitHub Actions workflows for building and releasing the Auto Mouse Move application.

## Workflows

### 1. Build and Release (`build-and-release.yml`)

**Trigger**: When you push a version tag (e.g., `v1.0.0`, `v2.1.3`)

**What it does**:
- Creates a GitHub release
- Builds the application for macOS on both architectures:
  - **macOS**: Intel (x86_64) and Apple Silicon (ARM64)
- Uploads both macOS executables to the release
- Updates the release notes with download links and macOS-specific instructions

**Usage**:
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### 2. Test Build (`test-build.yml`)

**Trigger**: 
- Push to main/master/develop branches
- Pull requests to main/master/develop branches
- Manual trigger from GitHub Actions tab

**What it does**:
- Tests building the application on macOS architectures
- Uploads build artifacts for debugging (retained for 7 days)
- Helps catch build issues before creating releases

## Build Matrix

| Platform | Architecture | Runner | Output |
|----------|-------------|---------|---------|
| macOS | Intel (x86_64) | `macos-13` | `telek-macos-x86_64.zip` |
| macOS | Apple Silicon (ARM64) | `macos-14` | `telek-macos-arm64.zip` |

## Features

### Multi-Architecture Support
- **ARM64**: Native support for Apple Silicon Macs (M1/M2/M3)
- **x86_64**: Traditional Intel Mac support

### Native macOS Building
- Uses native macOS runners for optimal performance
- Platform-specific optimizations and app bundle creation
- Proper ICNS icon generation using macOS tools

### Automated Release Management
- Creates GitHub releases automatically
- Generates comprehensive release notes
- Provides download links for all platforms
- Includes installation instructions

### Build Verification
- Verifies build outputs exist
- Checks file types and permissions
- Provides detailed logging for debugging

## Requirements

### Repository Secrets
No additional secrets are required. The workflows use the built-in `GITHUB_TOKEN`.

### Dependencies
The workflows automatically install:
- Python 3.11
- Project dependencies from `requirements.txt`
- PyInstaller for building executables
- Platform-specific system dependencies

### File Structure
The workflows expect:
- `requirements.txt` in the project root
- `MouseMover.spec` PyInstaller spec file
- Source code in `src/mm/` directory

## Customization

### Changing Python Version
Update the `PYTHON_VERSION` environment variable in both workflow files:
```yaml
env:
  PYTHON_VERSION: '3.11'  # Change to desired version
```

### Adding New Platforms
Add new entries to the build matrix:
```yaml
- os: new-platform
  runner: runner-name
  arch: architecture
  build_cmd: |
    # Build commands
  artifact_name: output-name
  artifact_path: path/to/output
  content_type: mime/type
```

### Modifying Build Commands
Update the `build_cmd` for each platform in the matrix to customize the build process.

## Troubleshooting

### Build Failures
1. Check the Actions tab in your GitHub repository
2. Review the build logs for specific error messages
3. Test builds locally using the same commands
4. Use the test-build workflow to debug issues

### Missing Dependencies
- Linux builds may require additional system packages
- Add them to the "Install additional dependencies" step
- macOS and Windows runners come with most required dependencies

### Icon Issues
The workflows automatically create a simple icon if none exists. To use a custom icon:
1. Place your icon file in `src/mm/resources/`
2. Update the `MouseMover.spec` file to reference it
3. Ensure the icon is in the correct format for each platform

## Security Notes

### Antivirus False Positives
PyInstaller executables are sometimes flagged by antivirus software as suspicious. This is a common false positive. Users can:
- Add exceptions for the executable
- Build from source if concerned
- Review the source code in the repository

### Code Signing
For production releases, consider adding code signing:
- **macOS**: Use Apple Developer certificates
- **Windows**: Use Authenticode certificates
- Add signing steps to the workflow after building

## Manual Triggering

Both workflows can be triggered manually:
1. Go to the Actions tab in your GitHub repository
2. Select the workflow you want to run
3. Click "Run workflow"
4. Choose the branch and click "Run workflow"

This is useful for:
- Testing changes before creating tags
- Creating releases from specific commits
- Debugging build issues