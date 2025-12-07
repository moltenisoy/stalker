# Stalker - Advanced Local Productivity Launcher

Stalker (FastLauncher) is a powerful, privacy-focused productivity launcher for Windows that provides instant access to applications, files, system controls, and automation workflows - all without sending your data to the cloud.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Features

### Core Functionality
- **⚡ Quick Launcher**: Instant application and file search with fuzzy matching
- **🎯 Intent Router**: Automatic detection of user intent (open apps, search files, system actions)
- **🔗 Compound Actions**: Chain multiple actions into single workflows
- **📋 Clipboard Manager**: Enhanced clipboard with history and snippets
- **🤖 AI Integration**: Optional AI-powered responses (BYOK - Bring Your Own Key)
- **🔍 File Indexer**: Fast file search with optional real-time watching
- **💻 System Health**: CPU, memory, and process monitoring with overlay
- **🎨 Customizable UI**: Dark/light themes, custom fonts, opacity control

### Modules
- **Optimizer**: System optimization and cleanup tools
- **Clipboard**: Advanced clipboard management
- **Snippets**: Text snippet expansion
- **AI Assistant**: AI-powered queries and responses
- **Files**: Fast file search and management
- **Links**: URL and bookmark management
- **Macros**: Custom automation macros

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit) or Windows 11
- **RAM**: 4 GB
- **Disk Space**: 100 MB for application + storage for indexed files
- **Runtime**: Microsoft Visual C++ Redistributable (usually pre-installed)

### Optional Dependencies
- **Python 3.9+** (only if running from source)
- See `requirements.txt` for Python packages

## 🚀 Installation

### Option 1: Pre-built Executable (Recommended)

1. Download the latest `Stalker.exe` from the [Releases](https://github.com/moltenisoy/stalker/releases) page
2. Verify the checksum (see `Stalker.exe.checksums.txt`)
3. Run `Stalker.exe`
4. On first run, a default configuration will be created at `%USERPROFILE%\.fastlauncher\config.json`

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/moltenisoy/stalker.git
cd stalker

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## ⌨️ Hotkeys and Usage

### Global Hotkey
- **`Ctrl+Space`** (default): Open/close the launcher
  - Can be customized in settings

### Main Window Commands

#### Application Launching
```
chrome           → Open Google Chrome
vscode          → Open Visual Studio Code
notepad++       → Open Notepad++
```

#### File Search
```
file: report     → Search for files named "report"
*.pdf           → Find all PDF files
document.docx   → Open specific document
```

#### System Actions
```
lock            → Lock the computer
shutdown        → Shutdown the computer
restart         → Restart the computer
volume up       → Increase system volume
volume down     → Decrease system volume
sleep           → Put computer to sleep
```

#### Text Transformation
```
uppercase       → Convert text to UPPERCASE
lowercase       → Convert text to lowercase
titlecase       → Convert Text To Title Case
```

#### Clipboard & Snippets
```
@email          → Paste email address snippet
;signature      → Paste signature snippet
history         → View clipboard history
```

#### Calculations
```
2+2             → Calculate: 4
sqrt(16)        → Calculate: 4.0
10 * 5          → Calculate: 50
```

#### Translation
```
translate hello → Translate text
traducir texto  → Translate to Spanish
```

### Compound Actions
Pre-configured workflows that chain multiple actions:

1. **Zip and Share**: Select file(s) → Compress → Copy ZIP path
2. **Copy Path and Open Folder**: Copy file path → Open containing folder
3. **Convert and Paste**: Transform text → Paste automatically

### System Health Overlay
- **Toggle**: Enable in Settings → SysHealth
- **Position**: Configurable (top-left, top-right, bottom-left, bottom-right)
- **Displays**: CPU, RAM usage, top processes
- **Kill Process**: Click on process name (with confirmation)

## 🔧 Configuration

Configuration is stored in `%USERPROFILE%\.fastlauncher\config.json`

### UI Settings
```json
{
  "ui": {
    "font_family": "Segoe UI",
    "font_size": 11,
    "theme": "dark",
    "opacity_active": 0.98,
    "opacity_inactive": 0.6,
    "accent": "#3a86ff",
    "effects": true
  }
}
```

### Module Configuration
```json
{
  "modules": {
    "optimizer": true,
    "clipboard": true,
    "snippets": true,
    "ai": true,
    "files": true,
    "links": true,
    "macros": true
  }
}
```

### File Indexer
```json
{
  "file_indexer": {
    "roots": [],
    "watch_enabled": false
  }
}
```

### System Health
```json
{
  "syshealth": {
    "sampling_interval": 2.0,
    "process_refresh_interval": 3.0,
    "process_limit": 15,
    "confirm_kill": true,
    "overlay_enabled": false,
    "overlay_update_interval": 5.0,
    "overlay_position": "top-right"
  }
}
```

## 🔐 Privacy & Security

- **100% Local**: All processing happens on your machine
- **No Telemetry**: We don't collect any usage data
- **No Cloud**: Your data never leaves your computer
- **AI Optional**: AI features require your own API key (BYOK)
- **Open Source**: Full transparency - inspect the code yourself

## 🛠️ Building from Source

### Prerequisites
```bash
pip install pyinstaller
```

### Build Executable
```bash
# Basic build
python build_exe.py

# Build with custom icon
python build_exe.py --icon path/to/icon.ico

# Skip cleaning build directories
python build_exe.py --no-clean
```

### Build Output
The build process creates:
- `dist/Stalker.exe` - The standalone executable
- `dist/Stalker.exe.checksums.txt` - SHA-256 and MD5 checksums
- `dist/BUILD_INFO.txt` - Build information and requirements

### Verify Build
```bash
# Verify build artifacts and checksums
python verify_build.py
```

### Verifying Checksums

#### Windows PowerShell
```powershell
# SHA-256
Get-FileHash Stalker.exe -Algorithm SHA256

# MD5
Get-FileHash Stalker.exe -Algorithm MD5
```

#### Command Prompt with CertUtil
```cmd
certutil -hashfile Stalker.exe SHA256
certutil -hashfile Stalker.exe MD5
```

## 📖 Documentation

### Getting Started
- [Quick Start Guide](QUICKSTART.md) - Get up and running in 5 minutes
- [Build Guide](BUILD.md) - Detailed build instructions
- [Icon Guide](ICON_GUIDE.md) - Creating custom icons
- [Changelog](CHANGELOG.md) - Version history and changes

### Project Improvements
- [Improvements and Suggestions](IMPROVEMENTS_AND_SUGGESTIONS.md) - Code improvements and feature suggestions (English)
- [Mejoras y Sugerencias](MEJORAS_Y_SUGERENCIAS.md) - Mejoras de código y sugerencias de características (Español)

### Detailed Documentation
Available in the `docs/` directory:

- [API Reference](docs/API_REFERENCE.md)
- [Comprehensive Documentation](docs/COMPREHENSIVE_DOCUMENTATION.md)
- [Settings Panel Guide](docs/SETTINGS_PANEL.md)
- [System Health Features](docs/SYSHEALTH_FEATURES.md)
- [AI Integration](docs/AI_BYOK_AND_NOTES.md)
- [Examples](docs/EXAMPLES.md)

## 🐛 Troubleshooting

### Application Won't Start
1. Ensure you have the latest Microsoft Visual C++ Redistributable
2. Check that no other instance is running
3. Delete `%USERPROFILE%\.fastlauncher\config.json` to reset configuration

### Hotkey Not Working
1. Check if another application is using the same hotkey
2. Try changing the hotkey in Settings
3. Run as Administrator if needed

### File Search Not Finding Files
1. Configure file indexer roots in Settings
2. Enable watchdog for real-time updates
3. Rebuild file index (Settings → File Indexer → Rebuild)

### High Memory Usage
1. Disable unnecessary modules in Settings
2. Enable Performance Mode
3. Reduce file indexer roots
4. Disable system health overlay if not needed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup
```bash
git clone https://github.com/moltenisoy/stalker.git
cd stalker
pip install -r requirements.txt
python main.py
```

### Running Tests
```bash
pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- PySide6 for the Qt bindings
- PyInstaller for executable packaging
- All contributors and users

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/moltenisoy/stalker/issues)
- **Documentation**: [docs/](docs/)
- **Releases**: [GitHub Releases](https://github.com/moltenisoy/stalker/releases)

---

Made with ❤️ for productivity enthusiasts
