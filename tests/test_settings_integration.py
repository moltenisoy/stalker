"""
Tests for settings panel integration with search engine.
"""
import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set up Qt to use offscreen platform
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from core.config import ConfigManager
from core.engine import SearchEngine
from PySide6.QtWidgets import QApplication


def test_config_command_returns_result():
    """Test that >config command returns settings panel result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Create Qt application (required for widgets)
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Create search engine
        engine = SearchEngine(config=config)
        
        # Search for config command
        results = engine.search(">config")
        
        # Should return one result to open settings panel
        assert len(results) == 1
        assert "Configuración" in results[0].title or "Panel" in results[0].title
        assert results[0].action is not None
        assert results[0].group == "config"
        
        print("✓ test_config_command_returns_result passed")


def test_settings_command_returns_result():
    """Test that 'settings' command also works."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        app = QApplication.instance() or QApplication(sys.argv)
        engine = SearchEngine(config=config)
        
        # Search for settings command
        results = engine.search("settings")
        
        # Should return one result to open settings panel
        assert len(results) == 1
        assert results[0].action is not None
        
        print("✓ test_settings_command_returns_result passed")


def test_open_settings_panel_method_exists():
    """Test that _open_settings_panel method exists and is callable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        app = QApplication.instance() or QApplication(sys.argv)
        engine = SearchEngine(config=config)
        
        # Check method exists
        assert hasattr(engine, '_open_settings_panel')
        assert callable(engine._open_settings_panel)
        
        print("✓ test_open_settings_panel_method_exists passed")


def test_config_command_case_insensitive():
    """Test that config command works regardless of case."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        app = QApplication.instance() or QApplication(sys.argv)
        engine = SearchEngine(config=config)
        
        # Test various cases
        test_queries = [">config", ">CONFIG", ">Config", "settings", "SETTINGS", "Settings"]
        
        for query in test_queries:
            results = engine.search(query)
            assert len(results) == 1, f"Query '{query}' should return exactly one result"
            assert results[0].action is not None, f"Query '{query}' result should have an action"
        
        print("✓ test_config_command_case_insensitive passed")


if __name__ == "__main__":
    print("Running Settings Integration tests...\n")
    
    test_config_command_returns_result()
    test_settings_command_returns_result()
    test_open_settings_panel_method_exists()
    test_config_command_case_insensitive()
    
    print("\n✅ All Settings Integration tests passed!")
