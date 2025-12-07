import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path.home() / ".fastlauncher" / "config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

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
}

class ConfigManager:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = path
        self.data = _DEFAULTS.copy()
        self.load()

    def load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = {**_DEFAULTS, **json.load(f)}
            except Exception:
                self.data = _DEFAULTS.copy()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def export(self, dest: Path):
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        return dest

    def import_file(self, src: Path):
        with open(src, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.save()

    def toggle_performance_mode(self, value: bool):
        self.data["performance_mode"] = value
        self.save()

    def set_module_enabled(self, module: str, enabled: bool):
        if module in self.data["modules"]:
            self.data["modules"][module] = enabled
            self.save()

    def set_ui(self, **kwargs):
        self.data["ui"].update(kwargs)
        self.save()