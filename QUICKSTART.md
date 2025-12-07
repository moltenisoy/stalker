# Quick Start Guide

Get Stalker up and running in 5 minutes!

## For Users

### Download and Run
1. Go to [Releases](https://github.com/moltenisoy/stalker/releases)
2. Download `Stalker.exe`
3. Double-click to run
4. Press `Ctrl+Space` to open the launcher

That's it! 🎉

### First Steps
1. **Search for apps**: Type application name (e.g., "chrome", "notepad")
2. **Find files**: Type `file: document` or `*.pdf`
3. **System actions**: Type `lock`, `shutdown`, `volume up`
4. **Open settings**: Click the gear icon or type `settings`

## For Developers

### Clone and Run
```bash
# Clone the repository
git clone https://github.com/moltenisoy/stalker.git
cd stalker

# Install dependencies (Windows only)
pip install -r requirements.txt

# Run the application
python main.py
```

### Building Executable
```bash
# Install build tools
pip install -r requirements-build.txt

# Build
python build_exe.py

# Verify
python verify_build.py

# Find your executable
# → dist/Stalker.exe
```

### Running Tests
```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config.py -v
```

## Common Commands

Once the launcher is open (Ctrl+Space):

| Command | Action |
|---------|--------|
| `chrome` | Open Google Chrome |
| `file: report` | Search for files |
| `*.pdf` | Find all PDF files |
| `lock` | Lock computer |
| `volume up` | Increase volume |
| `2+2` | Calculate |
| `settings` | Open settings |

## Hotkeys

| Key | Action |
|-----|--------|
| `Ctrl+Space` | Open/close launcher |
| `Esc` | Close launcher |
| `↑` `↓` | Navigate results |
| `Enter` | Execute selected action |

## Configuration

Config file location:
```
%USERPROFILE%\.fastlauncher\config.json
```

Edit to customize:
- Hotkey
- Theme (dark/light)
- Enabled modules
- UI appearance
- System health settings

## Need Help?

- **Documentation**: See [README.md](README.md)
- **Build Guide**: See [BUILD.md](BUILD.md)
- **Issues**: [GitHub Issues](https://github.com/moltenisoy/stalker/issues)
- **Features**: See [FEATURES_v2.0.md](FEATURES_v2.0.md)

## Next Steps

1. Explore [CHANGELOG.md](CHANGELOG.md) for what's new
2. Read [docs/COMPREHENSIVE_DOCUMENTATION.md](docs/COMPREHENSIVE_DOCUMENTATION.md)
3. Check out [docs/EXAMPLES.md](docs/EXAMPLES.md) for usage examples
4. Customize in Settings panel

Enjoy Stalker! 🚀
