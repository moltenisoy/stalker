# Changelog

All notable changes to Stalker (FastLauncher) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-07

### Added

#### Core Features
- **Intent Router**: Automatic detection of user intent from natural language input
  - Open applications by name
  - Search files with natural language
  - System actions (lock, shutdown, volume control)
  - Text transformation (uppercase, lowercase, titlecase)
  - Translation support
  - Calculator functionality
  
- **Compound Actions**: Chain multiple actions into single workflows
  - Zip and Share: Compress files and copy path
  - Copy Path and Open Folder: Navigate while copying paths
  - Convert and Paste: Transform and automatically paste text
  
- **Context Profiles**: Automatic context detection and switching
  - Per-application context awareness
  - Contextual action suggestions
  - Smart defaults based on current activity

#### Modules
- **System Health Monitor**
  - Real-time CPU and memory monitoring
  - Process list with resource usage
  - Kill process functionality with confirmation
  - Optional persistent overlay (configurable position)
  - Configurable sampling and refresh intervals

- **Enhanced File Indexer**
  - Fast file search with fuzzy matching
  - Configurable search roots
  - Optional real-time file watching (watchdog)
  - Improved search scoring algorithm

- **AI Assistant** (BYOK - Bring Your Own Key)
  - AI-powered query responses
  - Clipboard integration
  - Notes management
  - Privacy-focused (all processing local except AI API calls)

- **Clipboard Manager**
  - Clipboard history
  - Snippet management and expansion
  - Quick paste functionality

#### UI/UX Improvements
- **Settings Panel**
  - Comprehensive settings interface
  - Real-time preview of UI changes
  - Module enable/disable toggles
  - File indexer configuration
  - System health settings
  - Hotkey customization

- **Enhanced Launcher UI**
  - Improved search interface
  - Better visual feedback
  - Theme customization (dark/light)
  - Font and opacity settings
  - Accent color customization
  - Optional visual effects

#### Developer Features
- **Build Pipeline**
  - PyInstaller integration for single-file executable
  - Automatic config migration on first run
  - Checksum generation (SHA-256, MD5)
  - Build information file
  - Icon support
  - Test exclusion from build

- **Configuration Management**
  - Robust JSON configuration with validation
  - Deep merge of user settings with defaults
  - Automatic backup of corrupted configs
  - Import/export functionality

### Changed
- Configuration now stored in `%USERPROFILE%\.fastlauncher\config.json`
- Improved error handling throughout application
- Better performance with optional performance mode
- Enhanced search algorithms with better scoring

### Fixed
- Configuration validation to prevent invalid settings
- Memory leaks in file indexer
- UI flickering on theme changes
- Hotkey conflicts with other applications

### Security
- Local-first architecture (no telemetry)
- No cloud data transmission (except optional AI API calls)
- Secure credential storage for AI API keys
- Input validation and sanitization

## [1.0.0] - Initial Release

### Added
- Basic launcher functionality
- Application search and launch
- File search
- System commands
- Hotkey support (Ctrl+Space)
- Basic UI with dark theme

---

## Release Notes

### v2.0.0 Key Features

#### 🎯 Intent Router
The Intent Router automatically understands what you want to do based on your input:
- Type "open chrome" to launch Chrome
- Type "file: report" to search for files
- Type "lock" to lock your computer
- Type "2+2" to calculate

#### 🔗 Compound Actions
Chain multiple actions together for powerful workflows:
- Select files, zip them, and copy the path in one action
- Copy file paths and open their containing folders
- Transform text and automatically paste it

#### 💻 System Health
Monitor your system in real-time:
- CPU and memory usage graphs
- Top processes by resource usage
- Kill runaway processes
- Optional persistent overlay

#### 🔧 Enhanced Configuration
- Comprehensive settings panel
- Real-time UI customization
- Module management
- File indexer configuration
- System health settings

#### 🔐 Privacy First
- 100% local processing (except optional AI)
- No telemetry or tracking
- Your data stays on your machine
- Open source for transparency

### System Requirements
- Windows 10 (64-bit) or Windows 11
- 4 GB RAM minimum
- 100 MB disk space
- Microsoft Visual C++ Redistributable (usually pre-installed)

### Installation
1. Download `Stalker.exe` from releases
2. Verify checksum from `Stalker.exe.checksums.txt`
3. Run the executable
4. Default configuration will be created on first run

### Building from Source
```bash
pip install pyinstaller
python build_exe.py
```

Output files:
- `dist/Stalker.exe` - The executable
- `dist/Stalker.exe.checksums.txt` - Checksums
- `dist/BUILD_INFO.txt` - Build information

### Known Issues
- Requires Windows 10/11 (not compatible with Windows 7/8)
- Some antivirus software may flag the executable (false positive)
- Hotkey may conflict with other applications using Ctrl+Space

### Upgrade Notes
When upgrading from v1.0.0:
- Backup your configuration before upgrading
- Configuration location may have changed
- New modules are enabled by default (can be disabled in settings)
- Review new hotkeys and compound actions

---

For more information, see [README.md](README.md) and documentation in the `docs/` directory.
