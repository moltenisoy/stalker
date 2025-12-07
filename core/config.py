import json
import copy
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_PATH = Path.home() / ".fastlauncher" / "config.json"

_DEFAULTS: Dict[str, Any] = {
    "ui": {
        "font_family": "Segoe UI",
        "font_size": 11,
        "theme": "dark",  # dark|light
        "opacity_active": 0.98,
        "opacity_inactive": 0.6,
        "accent": "#3a86ff",
        "effects": True,
    },
    "hotkey": "ctrl+space",
    "modules": {
        "optimizer": True,
        "clipboard": True,
        "snippets": True,
        "ai": True,
        "files": True,
        "links": True,
        "macros": True,
    },
    "performance_mode": False,
    "plugin_shell": {"enabled": True},
    "file_indexer": {
        "roots": [],  # Empty means use home directory as default
        "watch_enabled": False,  # Optional watchdog feature
    },
}


def _validate_ui_config(ui_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize UI configuration values."""
    validated = {}
    
    # Font family - must be string
    validated["font_family"] = str(ui_config.get("font_family", _DEFAULTS["ui"]["font_family"]))
    
    # Font size - must be int between 8 and 24
    try:
        font_size = int(ui_config.get("font_size", _DEFAULTS["ui"]["font_size"]))
        validated["font_size"] = max(8, min(24, font_size))
    except (ValueError, TypeError):
        validated["font_size"] = _DEFAULTS["ui"]["font_size"]
    
    # Theme - must be "dark" or "light"
    theme = ui_config.get("theme", _DEFAULTS["ui"]["theme"])
    validated["theme"] = theme if theme in ("dark", "light") else _DEFAULTS["ui"]["theme"]
    
    # Opacity values - must be float between 0.0 and 1.0
    for key in ("opacity_active", "opacity_inactive"):
        try:
            opacity = float(ui_config.get(key, _DEFAULTS["ui"][key]))
            validated[key] = max(0.0, min(1.0, opacity))
        except (ValueError, TypeError):
            validated[key] = _DEFAULTS["ui"][key]
    
    # Accent color - must be hex color string
    accent = ui_config.get("accent", _DEFAULTS["ui"]["accent"])
    if isinstance(accent, str) and accent.startswith("#") and len(accent) in (4, 7):
        validated["accent"] = accent
    else:
        validated["accent"] = _DEFAULTS["ui"]["accent"]
    
    # Effects - must be boolean
    validated["effects"] = bool(ui_config.get("effects", _DEFAULTS["ui"]["effects"]))
    
    return validated


def _validate_hotkey(hotkey: Any) -> str:
    """Validate and sanitize hotkey string."""
    if not isinstance(hotkey, str):
        return _DEFAULTS["hotkey"]
    
    # Basic validation: must contain at least one modifier and a key
    hotkey = hotkey.strip().lower()
    if not hotkey or "+" not in hotkey:
        return _DEFAULTS["hotkey"]
    
    return hotkey


def _validate_modules(modules: Any) -> Dict[str, bool]:
    """Validate and sanitize modules configuration."""
    if not isinstance(modules, dict):
        return copy.deepcopy(_DEFAULTS["modules"])
    
    validated = {}
    for key in _DEFAULTS["modules"].keys():
        validated[key] = bool(modules.get(key, _DEFAULTS["modules"][key]))
    
    return validated


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries, with validation."""
    result = copy.deepcopy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


class ConfigManager:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = path
        self.data = copy.deepcopy(_DEFAULTS)
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create config directory: {e}")

    def load(self):
        """Load configuration from file with robust error handling."""
        if not self.path.exists():
            # No config file yet, use defaults and create one
            self.save()
            return
        
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            if not isinstance(loaded_data, dict):
                raise ValueError("Config file must contain a JSON object")
            
            # Deep merge with defaults to ensure all keys exist
            merged = _deep_merge(_DEFAULTS, loaded_data)
            
            # Validate individual sections
            merged["ui"] = _validate_ui_config(merged.get("ui", {}))
            merged["hotkey"] = _validate_hotkey(merged.get("hotkey"))
            merged["modules"] = _validate_modules(merged.get("modules"))
            merged["performance_mode"] = bool(merged.get("performance_mode", False))
            
            self.data = merged
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            print("Using default configuration")
            self.data = copy.deepcopy(_DEFAULTS)
            self._backup_and_save()
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            self.data = copy.deepcopy(_DEFAULTS)
            self._backup_and_save()

    def save(self):
        """Save configuration to file with error handling."""
        try:
            self._ensure_config_dir()
            # Validate before saving
            self.data["ui"] = _validate_ui_config(self.data.get("ui", {}))
            self.data["hotkey"] = _validate_hotkey(self.data.get("hotkey"))
            self.data["modules"] = _validate_modules(self.data.get("modules"))
            
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _backup_and_save(self):
        """Backup corrupted config and save defaults."""
        try:
            if self.path.exists():
                backup_path = self.path.with_suffix(".json.backup")
                self.path.rename(backup_path)
                print(f"Backed up corrupted config to {backup_path}")
        except Exception as e:
            print(f"Could not backup config: {e}")
        
        self.save()

    def export(self, dest: Path):
        """Export configuration to a file."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            return dest
        except Exception as e:
            print(f"Error exporting config: {e}")
            return None

    def import_file(self, src: Path):
        """Import configuration from a file."""
        try:
            if not src.exists():
                raise FileNotFoundError(f"Config file not found: {src}")
            
            with open(src, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            if not isinstance(loaded_data, dict):
                raise ValueError("Config file must contain a JSON object")
            
            # Merge with defaults and validate
            merged = _deep_merge(_DEFAULTS, loaded_data)
            merged["ui"] = _validate_ui_config(merged.get("ui", {}))
            merged["hotkey"] = _validate_hotkey(merged.get("hotkey"))
            merged["modules"] = _validate_modules(merged.get("modules"))
            
            self.data = merged
            self.save()
        except Exception as e:
            print(f"Error importing config: {e}")
            raise

    def toggle_performance_mode(self, value: bool):
        """Toggle performance mode with validation."""
        self.data["performance_mode"] = bool(value)
        self.save()

    def set_module_enabled(self, module: str, enabled: bool):
        """Enable or disable a module."""
        if "modules" not in self.data:
            self.data["modules"] = copy.deepcopy(_DEFAULTS["modules"])
        
        if module in _DEFAULTS["modules"]:
            self.data["modules"][module] = bool(enabled)
            self.save()

    def set_ui(self, **kwargs):
        """Update UI configuration with validation."""
        if "ui" not in self.data:
            self.data["ui"] = copy.deepcopy(_DEFAULTS["ui"])
        
        self.data["ui"].update(kwargs)
        self.data["ui"] = _validate_ui_config(self.data["ui"])
        self.save()

    def set_hotkey(self, hotkey: str):
        """Set global hotkey with validation."""
        validated = _validate_hotkey(hotkey)
        self.data["hotkey"] = validated
        self.save()
        return validated

    def get_ui(self, key: Optional[str] = None) -> Any:
        """Get UI configuration value(s)."""
        if key is None:
            return self.data.get("ui", copy.deepcopy(_DEFAULTS["ui"]))
        return self.data.get("ui", {}).get(key, _DEFAULTS["ui"].get(key))

    def get_performance_mode(self) -> bool:
        """Get performance mode status."""
        return bool(self.data.get("performance_mode", False))

    def get_module_enabled(self, module: str) -> bool:
        """Check if a module is enabled."""
        return bool(self.data.get("modules", {}).get(module, _DEFAULTS["modules"].get(module, False)))

    def get_file_indexer_roots(self):
        """Get file indexer roots."""
        file_indexer = self.data.get("file_indexer", _DEFAULTS.get("file_indexer", {}))
        return file_indexer.get("roots", [])

    def set_file_indexer_roots(self, roots: list):
        """Set file indexer roots."""
        if "file_indexer" not in self.data:
            self.data["file_indexer"] = copy.deepcopy(_DEFAULTS["file_indexer"])
        self.data["file_indexer"]["roots"] = roots
        self.save()

    def get_file_indexer_watch_enabled(self) -> bool:
        """Get whether watchdog is enabled for file indexer."""
        file_indexer = self.data.get("file_indexer", _DEFAULTS.get("file_indexer", {}))
        return bool(file_indexer.get("watch_enabled", False))

    def set_file_indexer_watch_enabled(self, enabled: bool):
        """Set whether watchdog is enabled for file indexer."""
        if "file_indexer" not in self.data:
            self.data["file_indexer"] = copy.deepcopy(_DEFAULTS["file_indexer"])
        self.data["file_indexer"]["watch_enabled"] = bool(enabled)
        self.save()