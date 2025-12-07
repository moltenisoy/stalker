# Building Stalker from Source

This document provides detailed instructions for building Stalker into a standalone executable.

## Prerequisites

### System Requirements
- Windows 10 (64-bit) or Windows 11
- Python 3.9 or higher (3.11 recommended)
- Git (for cloning the repository)

### Required Software
1. **Python**: Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Microsoft Visual C++ Redistributable**: Usually pre-installed on Windows 10/11
   - If needed, download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/moltenisoy/stalker.git
cd stalker
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (cmd)
venv\Scripts\activate.bat

# On Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install build dependencies
pip install -r requirements-build.txt
```

## Building the Executable

### Basic Build
The simplest way to build the executable:

```bash
python build_exe.py
```

This will:
1. Clean previous build artifacts
2. Run PyInstaller with optimal settings
3. Generate checksums (SHA-256, MD5)
4. Create build information file
5. Output files to `dist/` directory

### Build with Custom Icon
If you have a custom icon file:

```bash
python build_exe.py --icon path/to/icon.ico
```

Icon requirements:
- Format: `.ico` file
- Recommended size: 256x256 pixels
- Multiple resolutions in one file (16x16, 32x32, 48x48, 256x256)

### Skip Cleaning Previous Builds
To keep previous build artifacts:

```bash
python build_exe.py --no-clean
```

## Build Output

After successful build, you'll find these files in the `dist/` directory:

### Stalker.exe
The standalone executable. This file includes:
- All Python code
- All dependencies
- PySide6 Qt libraries
- Default configuration template
- Runtime hooks

Size: Approximately 100-200 MB (varies based on dependencies)

### Stalker.exe.checksums.txt
Contains cryptographic checksums for verifying file integrity:
- **SHA-256**: Primary checksum (recommended)
- **MD5**: Legacy checksum for compatibility

Example content:
```
File: Stalker.exe
SHA-256: a1b2c3d4e5f6...
MD5: 1a2b3c4d...
```

### BUILD_INFO.txt
Build metadata including:
- Version number
- Build date and time
- Python version used
- Runtime requirements
- Additional notes

## Verifying Checksums

### Using PowerShell
```powershell
# SHA-256
Get-FileHash Stalker.exe -Algorithm SHA256

# MD5
Get-FileHash Stalker.exe -Algorithm MD5
```

### Using Command Prompt (CertUtil)
```cmd
# SHA-256
certutil -hashfile Stalker.exe SHA256

# MD5
certutil -hashfile Stalker.exe MD5
```

### Using Third-Party Tools
- **HashTab**: Windows Explorer extension for checksum verification
- **7-Zip**: Right-click → CRC SHA → SHA-256

Compare the output with values in `Stalker.exe.checksums.txt`

## Build Configuration

### PyInstaller Settings
The build script uses the following PyInstaller configuration:

```python
--onefile           # Single executable file
--windowed         # No console window
--name Stalker     # Output name
--clean            # Clean cache before building
--noconfirm        # Overwrite without confirmation
```

### Excluded Modules
To reduce file size, these modules are excluded:
- `tests/` - Test files
- `pytest` - Testing framework
- `unittest` - Python's testing module

### Included Data Files
- `config.default.json` - Default configuration template

### Hidden Imports
Pre-configured imports to ensure all dependencies are bundled:
- PySide6 (Qt GUI framework)
- keyboard, mouse (input handling)
- psutil (system monitoring)
- watchdog (file system monitoring)

## Troubleshooting

### Build Fails with "Module not found"
**Solution**: Install missing dependency
```bash
pip install <module-name>
```

### "PyInstaller not found"
**Solution**: Install build requirements
```bash
pip install -r requirements-build.txt
```

### Antivirus Blocking Build
**Solution**: Temporarily disable antivirus or add exception for:
- Python executable
- Project directory
- `dist/` output directory

### Large Executable Size
**Solutions**:
1. Use UPX compression (add `--upx-dir` to build script)
2. Exclude unnecessary modules
3. Use virtual environment (reduces included packages)

### Missing DLL Errors
**Solution**: Install Visual C++ Redistributable
- Download from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)

### Build Works but Exe Doesn't Run
**Debugging steps**:
1. Run from command line to see error messages:
   ```cmd
   Stalker.exe
   ```
2. Check Windows Event Viewer for application errors
3. Ensure all runtime dependencies are present

## Advanced Build Options

### Custom Build Script Modifications

#### Adding More Hidden Imports
Edit `build_exe.py` and add to the `cmd` list:
```python
'--hidden-import', 'module_name',
```

#### Excluding Additional Modules
```python
'--exclude-module', 'module_name',
```

#### Adding More Data Files
```python
'--add-data', 'source_path;destination_path',
```

### Manual PyInstaller Usage
If you prefer manual control:

```bash
pyinstaller --onefile --windowed --name Stalker ^
  --exclude-module tests ^
  --additional-hooks-dir hooks ^
  --add-data "config.default.json;." ^
  main.py
```

### Creating Custom Hooks
Create a file in `hooks/` directory named `hook-<module>.py`:

```python
"""Custom hook for <module>"""
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('module_name')
```

## Testing the Built Executable

### Basic Functionality Test
1. Run `Stalker.exe`
2. Check if GUI appears
3. Test hotkey (default: Ctrl+Space)
4. Try basic commands:
   - Type application name
   - Search for files
   - Test system commands

### Configuration Test
1. Close application
2. Check `%USERPROFILE%\.fastlauncher\config.json` exists
3. Verify default settings are present

### Clean Install Test
1. Delete `%USERPROFILE%\.fastlauncher\`
2. Run `Stalker.exe` again
3. Verify configuration is recreated

## Continuous Integration (CI)

The repository includes GitHub Actions workflow (`.github/workflows/build-release.yml`) that:
1. Automatically builds on tag push (e.g., `v2.0.0`)
2. Runs on Windows runner
3. Generates checksums
4. Creates draft release
5. Attaches artifacts

### Triggering CI Build
```bash
# Create and push a tag
git tag v2.0.0
git push origin v2.0.0
```

### Manual Workflow Dispatch
1. Go to GitHub repository
2. Click "Actions" tab
3. Select "Build and Release" workflow
4. Click "Run workflow"
5. Enter version number

## Distribution Checklist

Before distributing the executable:

- [ ] Build completed successfully
- [ ] Checksums generated
- [ ] BUILD_INFO.txt created
- [ ] Executable tested on clean Windows installation
- [ ] Configuration migration tested
- [ ] Hotkey functionality verified
- [ ] All modules load correctly
- [ ] README.md and CHANGELOG.md updated
- [ ] Version number updated in code
- [ ] Git tag created
- [ ] Release notes prepared

## Support

For build-related issues:
- Check [README.md](README.md) for general documentation
- Review [CHANGELOG.md](CHANGELOG.md) for version information
- Open an issue on [GitHub](https://github.com/moltenisoy/stalker/issues)

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Python Packaging Guide](https://packaging.python.org/)
