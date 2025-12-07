"""
Tests for config migration and first-run functionality.
"""
import sys
import json
import tempfile
import shutil
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_bundled_config_path_detection():
    """Test detection of bundled config path."""
    from core.config import _get_bundled_config_path
    
    bundled_path = _get_bundled_config_path()
    
    # Should return a Path object
    assert isinstance(bundled_path, Path)
    
    # Should point to config.default.json
    assert bundled_path.name == "config.default.json"


def test_config_migration_logic():
    """Test that config migration works correctly."""
    from core.config import _copy_default_config_on_first_run, CONFIG_PATH, _get_bundled_config_path
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_config_path = Path(tmpdir) / ".fastlauncher" / "config.json"
        
        # Temporarily override CONFIG_PATH for testing
        import core.config as config_module
        original_path = config_module.CONFIG_PATH
        config_module.CONFIG_PATH = test_config_path
        
        try:
            # Ensure default config exists
            default_config = _get_bundled_config_path()
            assert default_config.exists(), "Default config should exist"
            
            # Test: Config doesn't exist yet, should be copied
            assert not test_config_path.exists()
            
            _copy_default_config_on_first_run()
            
            # Config should now exist if default exists
            if default_config.exists():
                assert test_config_path.exists(), "Config should be created on first run"
                
                # Verify it's valid JSON
                with open(test_config_path, 'r') as f:
                    config = json.load(f)
                
                # Check basic structure
                assert "ui" in config
                assert "hotkey" in config
                assert "modules" in config
            
        finally:
            # Restore original CONFIG_PATH
            config_module.CONFIG_PATH = original_path


def test_config_not_overwritten_if_exists():
    """Test that existing config is not overwritten."""
    from core.config import _copy_default_config_on_first_run
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_config_path = Path(tmpdir) / ".fastlauncher" / "config.json"
        
        # Create config directory
        test_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a custom config
        custom_config = {"custom": "value", "test": True}
        with open(test_config_path, 'w') as f:
            json.dump(custom_config, f)
        
        # Override CONFIG_PATH
        import core.config as config_module
        original_path = config_module.CONFIG_PATH
        config_module.CONFIG_PATH = test_config_path
        
        try:
            # Call migration function
            _copy_default_config_on_first_run()
            
            # Verify config was not overwritten
            with open(test_config_path, 'r') as f:
                loaded_config = json.load(f)
            
            assert loaded_config == custom_config, "Existing config should not be overwritten"
            
        finally:
            config_module.CONFIG_PATH = original_path


def test_default_config_valid_json():
    """Test that the default config is valid JSON with expected structure."""
    default_config_path = Path(__file__).parent.parent / "config.default.json"
    
    assert default_config_path.exists(), "Default config should exist"
    
    with open(default_config_path, 'r') as f:
        config = json.load(f)
    
    # Test required top-level keys
    required_keys = ["ui", "hotkey", "modules", "performance_mode", "file_indexer", "syshealth"]
    for key in required_keys:
        assert key in config, f"Config should have '{key}' key"
    
    # Test UI config structure
    ui_keys = ["font_family", "font_size", "theme", "opacity_active", "opacity_inactive", "accent", "effects"]
    for key in ui_keys:
        assert key in config["ui"], f"UI config should have '{key}' key"
    
    # Test modules structure
    module_keys = ["optimizer", "clipboard", "snippets", "ai", "files", "links", "macros"]
    for key in module_keys:
        assert key in config["modules"], f"Modules config should have '{key}' key"
    
    # Test value types
    assert isinstance(config["hotkey"], str)
    assert isinstance(config["performance_mode"], bool)
    assert isinstance(config["modules"], dict)
    assert isinstance(config["ui"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
