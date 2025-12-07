# Settings Panel Documentation

## Overview

The Settings Panel provides a comprehensive graphical interface for managing all aspects of the Stalker/FastLauncher application configuration. It can be accessed by typing `>config` or `settings` in the launcher.

## Features

### 1. Hotkey Configuration

- **Change Global Hotkey**: Modify the keyboard shortcut that opens the launcher
- **Input Validation**: Ensures hotkey format is valid (modifier+key)
- **Example formats**: `ctrl+space`, `alt+f1`, `ctrl+shift+a`
- **Note**: Requires service restart or application restart to take effect

### 2. Appearance Settings

#### Theme
- Switch between `dark` and `light` themes
- Changes apply to entire application
- Instant preview in settings panel

#### Font
- **Font Family**: Choose system font (e.g., "Segoe UI", "Arial")
- **Font Size**: Adjust size between 8pt and 24pt
- Affects launcher input and results display

#### Opacity
- **Active Opacity**: Window opacity when focused (0.1 - 1.0)
- **Inactive Opacity**: Window opacity when unfocused (0.1 - 1.0)
- Allows subtle visual feedback

#### Accent Color
- **Hex Color Input**: Define accent color (e.g., `#3a86ff`)
- **Validation**: Ensures valid hex color format
- Used for highlights and interactive elements

### 3. Module Management

Enable or disable individual modules:

1. **Optimizer** - System health monitor and process manager
2. **Clipboard** - Clipboard history manager
3. **Snippets** - Text snippet templates
4. **AI Assistant** - Cloud/local AI integration
5. **Files** - File indexing and search
6. **Links** - Quick links and shortcuts
7. **Macros** - Macro recorder and playback

Changes take effect after service restart.

### 4. Performance Mode

- **Toggle Performance Mode**: Reduces resource usage
- When enabled:
  - Pauses file indexer
  - Disables AI assistant
  - Reduces visual effects
  - Minimizes background processing
- Useful for laptops on battery or low-resource systems

### 5. Configuration Management

#### Export Configuration
- Opens file dialog to save current config
- Creates JSON backup of all settings
- Default location: `~/stalker_config.json`

#### Import Configuration
- Opens file dialog to load config from file
- **Validation**: Ensures imported config is valid
- **Confirmation**: Asks before overwriting current settings
- Merges with defaults to ensure all required fields exist

### 6. Service Management

**Restart Services Button**:
- Reloads configuration from disk
- Restarts file indexer (if enabled)
- Reloads AI assistant (if enabled)
- Updates all module states
- Applies theme changes
- Shows status of all services after restart

Services affected:
- File Indexer
- AI Assistant
- Clipboard Manager
- Snippet Manager
- Quicklinks
- Macro Recorder
- System Health Monitor

### 7. Error Handling

- **Message Boxes**: User-friendly error notifications
- **Validation**: Prevents invalid configuration
- **Logging**: Full error details logged to console
- **Security**: Sensitive traceback info not shown to users

## Usage

### Opening Settings Panel

From the launcher, type:
- `>config` - Direct command
- `settings` - Alternative command

### Making Changes

1. Modify desired settings in the panel
2. Click "Apply" or equivalent button for each section
3. Changes are saved immediately to `~/.fastlauncher/config.json`
4. Some changes require service restart (hotkey, modules)

### Restarting Services

After making changes that require restart:
1. Click "Reiniciar Servicios" button
2. Review service status in confirmation dialog
3. Close settings panel

### Exporting Configuration

1. Click "Exportar Configuración"
2. Choose save location in file dialog
3. Save as JSON file

### Importing Configuration

1. Click "Importar Configuración"
2. Select JSON config file
3. Confirm import action
4. Restart services if needed

## Technical Details

### Configuration File

Location: `~/.fastlauncher/config.json`

Structure:
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
  },
  "hotkey": "ctrl+space",
  "modules": {
    "optimizer": true,
    "clipboard": true,
    "snippets": true,
    "ai": true,
    "files": true,
    "links": true,
    "macros": true
  },
  "performance_mode": false
}
```

### Implementation

- **UI Framework**: PySide6 (Qt for Python)
- **Layout**: Scrollable vertical layout with grouped sections
- **Validation**: Multi-level validation (input, save, import)
- **Persistence**: Automatic save on change
- **Integration**: Connected to search engine via `>config` command

### Architecture

```
LauncherApp
    ├── LauncherWindow
    │   └── PredictiveSearch
    │       └── SearchEngine
    │           └── _open_settings_panel() -> SettingsPanel
    └── ConfigManager (shared)
```

The settings panel receives:
- `ConfigManager` instance for reading/writing settings
- `LauncherApp` reference for service restart functionality

## Testing

Tests are located in:
- `tests/test_config.py` - ConfigManager functionality
- `tests/test_settings_panel.py` - UI component tests

Run tests:
```bash
python tests/test_config.py
python tests/test_settings_panel.py
```

All tests pass without requiring display server (offscreen mode).

## Future Enhancements

Possible future additions:
- Color picker widget for accent color
- Font selection dialog
- Keyboard shortcut recorder
- Preview of theme changes
- Advanced module-specific settings
- Backup/restore configuration history
- Configuration profiles (work, gaming, etc.)

## Troubleshooting

**Settings panel doesn't open**:
- Ensure PySide6 is installed: `pip install PySide6`
- Check console for error messages
- Verify config file is valid JSON

**Changes don't take effect**:
- Click "Apply" button for the section
- Use "Restart Services" button
- Some changes (hotkey) require full app restart

**Import fails**:
- Verify JSON file is valid
- Check file permissions
- Ensure file contains required fields

**Module toggles don't work**:
- Use "Restart Services" after toggling
- Some modules may require app restart
- Check console for module loading errors

## Related Documentation

- [CONFIG_REFACTORING.md](CONFIG_REFACTORING.md) - Configuration system design
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Overall implementation details
