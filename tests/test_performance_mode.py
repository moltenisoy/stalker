"""
Test performance mode integration with engine.
"""
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import ConfigManager


def test_performance_mode_config_integration():
    """Test that performance mode settings are properly managed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Test initial state using getter methods
        assert config.get_performance_mode() is False
        assert config.get_module_enabled("ai") is True
        assert config.get_module_enabled("files") is True
        
        # Enable performance mode
        config.toggle_performance_mode(True)
        assert config.get_performance_mode() is True
        
        # Verify it persists
        config2 = ConfigManager(path=config_path)
        assert config2.get_performance_mode() is True
        
        # Disable performance mode
        config2.toggle_performance_mode(False)
        assert config2.get_performance_mode() is False
        
        print("✓ test_performance_mode_config_integration passed")


def test_effects_disabled_in_performance_mode():
    """Test that effects can be controlled via config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Effects should be enabled by default
        assert config.get_ui("effects") is True
        
        # Disable effects
        config.set_ui(effects=False)
        assert config.get_ui("effects") is False
        
        # Verify it persists
        config2 = ConfigManager(path=config_path)
        assert config2.get_ui("effects") is False
        
        print("✓ test_effects_disabled_in_performance_mode passed")


def test_theme_switching():
    """Test theme switching functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Default should be dark
        assert config.get_ui("theme") == "dark"
        
        # Switch to light
        config.set_ui(theme="light")
        assert config.get_ui("theme") == "light"
        
        # Verify persistence
        config2 = ConfigManager(path=config_path)
        assert config2.get_ui("theme") == "light"
        
        # Invalid theme should be rejected
        config2.set_ui(theme="purple")
        assert config2.get_ui("theme") == "dark"  # Reset to default
        
        print("✓ test_theme_switching passed")


if __name__ == "__main__":
    print("Running performance mode integration tests...\n")
    
    test_performance_mode_config_integration()
    test_effects_disabled_in_performance_mode()
    test_theme_switching()
    
    print("\n✅ All integration tests passed!")
