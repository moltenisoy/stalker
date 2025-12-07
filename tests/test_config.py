"""
Basic tests for ConfigManager to validate defaults and toggles.
"""
import json
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.config import ConfigManager, _validate_ui_config, _validate_hotkey, _validate_modules, _DEFAULTS


def test_defaults():
    """Test that ConfigManager initializes with correct defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Check UI defaults
        assert config.data["ui"]["font_family"] == "Segoe UI"
        assert config.data["ui"]["font_size"] == 11
        assert config.data["ui"]["theme"] == "dark"
        assert config.data["ui"]["opacity_active"] == 0.98
        assert config.data["ui"]["opacity_inactive"] == 0.6
        assert config.data["ui"]["accent"] == "#3a86ff"
        assert config.data["ui"]["effects"] is True
        
        # Check hotkey default
        assert config.data["hotkey"] == "ctrl+space"
        
        # Check modules defaults
        assert config.data["modules"]["optimizer"] is True
        assert config.data["modules"]["clipboard"] is True
        assert config.data["modules"]["ai"] is True
        
        # Check performance mode default
        assert config.data["performance_mode"] is False
        
        print("✓ test_defaults passed")


def test_toggle_performance_mode():
    """Test toggling performance mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Initially should be False
        assert config.data["performance_mode"] is False
        
        # Toggle to True
        config.toggle_performance_mode(True)
        assert config.data["performance_mode"] is True
        
        # Reload and verify persistence
        config2 = ConfigManager(path=config_path)
        assert config2.data["performance_mode"] is True
        
        # Toggle back to False
        config2.toggle_performance_mode(False)
        assert config2.data["performance_mode"] is False
        
        print("✓ test_toggle_performance_mode passed")


def test_module_toggle():
    """Test enabling/disabling modules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Toggle AI module
        assert config.data["modules"]["ai"] is True
        config.set_module_enabled("ai", False)
        assert config.data["modules"]["ai"] is False
        
        # Reload and verify persistence
        config2 = ConfigManager(path=config_path)
        assert config2.data["modules"]["ai"] is False
        
        # Toggle back
        config2.set_module_enabled("ai", True)
        assert config2.data["modules"]["ai"] is True
        
        print("✓ test_module_toggle passed")


def test_ui_config():
    """Test UI configuration updates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Update UI settings
        config.set_ui(theme="light", font_size=14, accent="#ff0000")
        
        assert config.data["ui"]["theme"] == "light"
        assert config.data["ui"]["font_size"] == 14
        assert config.data["ui"]["accent"] == "#ff0000"
        
        # Reload and verify persistence
        config2 = ConfigManager(path=config_path)
        assert config2.data["ui"]["theme"] == "light"
        assert config2.data["ui"]["font_size"] == 14
        assert config2.data["ui"]["accent"] == "#ff0000"
        
        print("✓ test_ui_config passed")


def test_hotkey_validation():
    """Test hotkey validation."""
    # Valid hotkeys
    assert _validate_hotkey("ctrl+space") == "ctrl+space"
    assert _validate_hotkey("alt+tab") == "alt+tab"
    assert _validate_hotkey("ctrl+shift+a") == "ctrl+shift+a"
    
    # Invalid hotkeys should return default
    assert _validate_hotkey("") == _DEFAULTS["hotkey"]
    assert _validate_hotkey("space") == _DEFAULTS["hotkey"]  # No modifier
    assert _validate_hotkey(123) == _DEFAULTS["hotkey"]  # Not a string
    assert _validate_hotkey(None) == _DEFAULTS["hotkey"]
    
    print("✓ test_hotkey_validation passed")


def test_ui_validation():
    """Test UI configuration validation."""
    # Valid UI config
    valid_ui = {
        "font_family": "Arial",
        "font_size": 12,
        "theme": "light",
        "opacity_active": 0.9,
        "opacity_inactive": 0.5,
        "accent": "#00ff00",
        "effects": False,
    }
    result = _validate_ui_config(valid_ui)
    assert result["font_family"] == "Arial"
    assert result["font_size"] == 12
    assert result["theme"] == "light"
    assert result["opacity_active"] == 0.9
    assert result["opacity_inactive"] == 0.5
    assert result["accent"] == "#00ff00"
    assert result["effects"] is False
    
    # Invalid values should be corrected
    invalid_ui = {
        "font_size": 100,  # Too large
        "theme": "purple",  # Invalid theme
        "opacity_active": 2.0,  # Out of range
        "accent": "red",  # Invalid format
    }
    result = _validate_ui_config(invalid_ui)
    assert result["font_size"] == 24  # Clamped to max
    assert result["theme"] == "dark"  # Reset to default
    assert result["opacity_active"] == 1.0  # Clamped to max
    assert result["accent"] == _DEFAULTS["ui"]["accent"]  # Reset to default
    
    print("✓ test_ui_validation passed")


def test_corrupt_config_handling():
    """Test handling of corrupted config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        
        # Create a corrupted JSON file
        with open(config_path, "w") as f:
            f.write("{invalid json content")
        
        # Should load defaults despite corruption
        config = ConfigManager(path=config_path)
        assert config.data["hotkey"] == _DEFAULTS["hotkey"]
        assert config.data["ui"]["theme"] == _DEFAULTS["ui"]["theme"]
        
        # Should have created a backup
        backup_path = config_path.with_suffix(".json.backup")
        assert backup_path.exists()
        
        print("✓ test_corrupt_config_handling passed")


def test_export_import():
    """Test config export and import."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        export_path = Path(tmpdir) / "export.json"
        
        config = ConfigManager(path=config_path)
        
        # Modify some settings
        config.set_ui(theme="light", font_size=15)
        config.toggle_performance_mode(True)
        
        # Export
        result = config.export(export_path)
        assert result == export_path
        assert export_path.exists()
        
        # Create new config and import
        config2_path = Path(tmpdir) / "test_config2.json"
        config2 = ConfigManager(path=config2_path)
        config2.import_file(export_path)
        
        # Verify imported settings
        assert config2.data["ui"]["theme"] == "light"
        assert config2.data["ui"]["font_size"] == 15
        assert config2.data["performance_mode"] is True
        
        print("✓ test_export_import passed")


def test_set_hotkey():
    """Test setting hotkey."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Set new hotkey
        result = config.set_hotkey("alt+f1")
        assert result == "alt+f1"
        assert config.data["hotkey"] == "alt+f1"
        
        # Verify persistence
        config2 = ConfigManager(path=config_path)
        assert config2.data["hotkey"] == "alt+f1"
        
        print("✓ test_set_hotkey passed")


if __name__ == "__main__":
    print("Running ConfigManager tests...\n")
    
    test_defaults()
    test_toggle_performance_mode()
    test_module_toggle()
    test_ui_config()
    test_hotkey_validation()
    test_ui_validation()
    test_corrupt_config_handling()
    test_export_import()
    test_set_hotkey()
    
    print("\n✅ All tests passed!")
