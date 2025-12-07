"""
Tests for FileIndexer module.
"""
import tempfile
import time
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.storage import Storage
from core.config import ConfigManager
from modules.file_indexer import FileIndexer


def test_file_indexer_basic():
    """Test basic file indexer functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_dir = Path(tmpdir) / "test_files"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("test1")
        (test_dir / "file2.txt").write_text("test2")
        (test_dir / "file3.log").write_text("test3")
        
        # Create storage and config in temp directory
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        # Create file indexer with test directory as root
        indexer = FileIndexer(storage=storage, roots=[str(test_dir)], config=config)
        
        # Build index
        indexer._build_index()
        
        # Search for files
        results = indexer.search("file")
        assert len(results) >= 2, "Should find at least 2 files with 'file' in name"
        
        results = indexer.search("file1")
        assert len(results) == 1, "Should find exactly 1 file named file1"
        assert "file1.txt" in results[0]["name"]
        
        print("✓ test_file_indexer_basic passed")


def test_file_indexer_config_persistence():
    """Test that file indexer roots are persisted in config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        # Create indexer and set roots
        indexer = FileIndexer(storage=storage, config=config)
        test_roots = [tmpdir, str(Path.home())]
        indexer.set_roots(test_roots)
        
        # Verify roots are saved in config
        assert config.get_file_indexer_roots() == test_roots
        
        # Create new indexer - should load roots from config
        indexer2 = FileIndexer(storage=storage, config=config)
        assert indexer2.roots == test_roots
        
        print("✓ test_file_indexer_config_persistence passed")


def test_file_indexer_add_remove_roots():
    """Test adding and removing roots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        indexer = FileIndexer(storage=storage, config=config)
        initial_roots = indexer.roots.copy()
        
        # Add a root
        new_root = tmpdir
        indexer.add_root(new_root)
        assert new_root in indexer.roots
        assert len(indexer.roots) == len(initial_roots) + 1
        
        # Remove the root
        indexer.remove_root(new_root)
        assert new_root not in indexer.roots
        assert len(indexer.roots) == len(initial_roots)
        
        print("✓ test_file_indexer_add_remove_roots passed")


def test_file_indexer_stats():
    """Test that indexer provides statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_dir = Path(tmpdir) / "test_files"
        test_dir.mkdir()
        for i in range(5):
            (test_dir / f"file{i}.txt").write_text(f"test{i}")
        
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        indexer = FileIndexer(storage=storage, roots=[str(test_dir)], config=config)
        indexer._build_index()
        
        stats = indexer.get_stats()
        assert "files_indexed" in stats
        assert "errors" in stats
        assert "last_run" in stats
        assert stats["files_indexed"] >= 5
        assert stats["last_run"] is not None
        
        print("✓ test_file_indexer_stats passed")


def test_file_indexer_pause_resume():
    """Test pausing and resuming the indexer."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        indexer = FileIndexer(storage=storage, config=config)
        
        # Test pause
        indexer.pause(True)
        assert indexer.paused is True
        
        # Search should return empty when paused
        results = indexer.search("test")
        assert len(results) == 0
        
        # Test resume
        indexer.pause(False)
        assert indexer.paused is False
        
        print("✓ test_file_indexer_pause_resume passed")


if __name__ == "__main__":
    print("Running FileIndexer tests...\n")
    
    test_file_indexer_basic()
    test_file_indexer_config_persistence()
    test_file_indexer_add_remove_roots()
    test_file_indexer_stats()
    test_file_indexer_pause_resume()
    
    print("\n✅ All FileIndexer tests passed!")
