"""
Tests for Storage module additions (file index and app cache).
"""
import tempfile
import time
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import Storage


def test_file_index_operations():
    """Test file index storage operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        storage = Storage(path=storage_path, encrypt_keys=False)
        
        # Test replace_file_index
        records = [
            ("/path/to/file1.txt", "C:", "file1.txt", time.time()),
            ("/path/to/file2.txt", "C:", "file2.txt", time.time()),
            ("/path/to/document.pdf", "D:", "document.pdf", time.time()),
        ]
        storage.replace_file_index(records)
        
        # Test list_files
        results = storage.list_files()
        assert len(results) == 3
        
        # Test search by name
        results = storage.list_files(q="file")
        assert len(results) == 2
        
        results = storage.list_files(q="document")
        assert len(results) == 1
        assert results[0]["name"] == "document.pdf"
        
        # Test replace clears old data
        new_records = [
            ("/new/path/file3.txt", "C:", "file3.txt", time.time()),
        ]
        storage.replace_file_index(new_records)
        results = storage.list_files()
        assert len(results) == 1
        assert results[0]["name"] == "file3.txt"
        
        print("✓ test_file_index_operations passed")


def test_app_operations():
    """Test app storage operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        storage = Storage(path=storage_path, encrypt_keys=False)
        
        # Test add_app with alias
        storage.add_app("Calculator", "calc.exe", "calc")
        
        # Test get_app_by_alias
        app = storage.get_app_by_alias("calc")
        assert app is not None
        assert app["name"] == "Calculator"
        assert app["path"] == "calc.exe"
        assert app["alias"] == "calc"
        
        # Test list_apps
        storage.add_app("Notepad", "notepad.exe", "note")
        storage.add_app("Paint", "mspaint.exe")
        
        results = storage.list_apps()
        assert len(results) >= 3
        
        # Test search
        results = storage.list_apps(q="calc")
        assert len(results) >= 1
        assert any(r["name"] == "Calculator" for r in results)
        
        print("✓ test_app_operations passed")


def test_app_alias_update():
    """Test that app aliases can be updated."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        storage = Storage(path=storage_path, encrypt_keys=False)
        
        # Add app with alias
        storage.add_app("Calculator", "calc.exe", "calc")
        app = storage.get_app_by_alias("calc")
        assert app["name"] == "Calculator"
        
        # Update the same alias with different app
        storage.add_app("New Calculator", "calc2.exe", "calc")
        app = storage.get_app_by_alias("calc")
        assert app["name"] == "New Calculator"
        assert app["path"] == "calc2.exe"
        
        print("✓ test_app_alias_update passed")


def test_clear_app_cache():
    """Test clearing app cache while preserving aliases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        storage = Storage(path=storage_path, encrypt_keys=False)
        
        # Add apps with and without aliases
        storage.add_app("Calculator", "calc.exe", "calc")
        storage.add_app("Notepad", "notepad.exe", "note")
        storage.add_app("Random App 1", "app1.exe")
        storage.add_app("Random App 2", "app2.exe")
        
        # Verify all added
        results = storage.list_apps()
        assert len(results) == 4
        
        # Clear cache (should remove non-aliased apps)
        storage.clear_app_cache()
        
        # Verify aliases preserved
        results = storage.list_apps()
        assert len(results) == 2
        assert storage.get_app_by_alias("calc") is not None
        assert storage.get_app_by_alias("note") is not None
        
        print("✓ test_clear_app_cache passed")


if __name__ == "__main__":
    print("Running Storage tests...\n")
    
    test_file_index_operations()
    test_app_operations()
    test_app_alias_update()
    test_clear_app_cache()
    
    print("\n✅ All Storage tests passed!")
