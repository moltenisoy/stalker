"""
Integration test for file search and indexing.
Tests the full flow from config to storage to search.
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


def test_full_file_indexing_flow():
    """Test complete file indexing workflow with config persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test directory structure
        test_dir = Path(tmpdir) / "test_files"
        test_dir.mkdir()
        
        # Create subdirectories
        docs_dir = test_dir / "documents"
        docs_dir.mkdir()
        images_dir = test_dir / "images"
        images_dir.mkdir()
        
        # Create test files
        (docs_dir / "report.pdf").write_text("report")
        (docs_dir / "notes.txt").write_text("notes")
        (images_dir / "photo1.jpg").write_text("photo")
        (images_dir / "photo2.png").write_text("photo")
        (test_dir / "readme.md").write_text("readme")
        
        # Create storage and config
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        # Create indexer and set custom root
        indexer = FileIndexer(storage=storage, config=config)
        indexer.set_roots([str(test_dir)])
        
        # Verify root was persisted
        assert config.get_file_indexer_roots() == [str(test_dir)]
        
        # Build index
        indexer._build_index()
        
        # Verify stats
        stats = indexer.get_stats()
        assert stats["files_indexed"] >= 5
        assert stats["errors"] == 0
        
        # Test search
        results = indexer.search("photo")
        assert len(results) == 2
        names = [r["name"] for r in results]
        assert "photo1.jpg" in names
        assert "photo2.png" in names
        
        results = indexer.search("report")
        assert len(results) == 1
        assert results[0]["name"] == "report.pdf"
        
        results = indexer.search(".txt")
        assert len(results) == 1
        assert results[0]["name"] == "notes.txt"
        
        # Test that new indexer instance loads config
        indexer2 = FileIndexer(storage=storage, config=config)
        assert indexer2.roots == [str(test_dir)]
        
        print("✓ test_full_file_indexing_flow passed")


def test_multiple_roots():
    """Test indexing with multiple roots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two separate directory trees
        dir1 = Path(tmpdir) / "dir1"
        dir1.mkdir()
        (dir1 / "file1.txt").write_text("file1")
        
        dir2 = Path(tmpdir) / "dir2"
        dir2.mkdir()
        (dir2 / "file2.txt").write_text("file2")
        
        # Create storage and config
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        # Create indexer with multiple roots
        indexer = FileIndexer(storage=storage, config=config)
        indexer.set_roots([str(dir1), str(dir2)])
        
        # Build index
        indexer._build_index()
        
        # Search should find files from both roots
        results = indexer.search("file")
        assert len(results) == 2
        names = [r["name"] for r in results]
        assert "file1.txt" in names
        assert "file2.txt" in names
        
        print("✓ test_multiple_roots passed")


def test_incremental_root_management():
    """Test adding and removing roots incrementally."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test directories
        dir1 = Path(tmpdir) / "dir1"
        dir1.mkdir()
        (dir1 / "file1.txt").write_text("file1")
        
        dir2 = Path(tmpdir) / "dir2"
        dir2.mkdir()
        (dir2 / "file2.txt").write_text("file2")
        
        dir3 = Path(tmpdir) / "dir3"
        dir3.mkdir()
        (dir3 / "file3.txt").write_text("file3")
        
        # Create storage and config
        storage_path = Path(tmpdir) / "storage.db"
        config_path = Path(tmpdir) / "config.json"
        
        storage = Storage(path=storage_path, encrypt_keys=False)
        config = ConfigManager(path=config_path)
        
        # Start with one root
        indexer = FileIndexer(storage=storage, roots=[str(dir1)], config=config)
        indexer._build_index()
        
        results = indexer.search("file")
        assert len(results) == 1
        
        # Add second root
        indexer.add_root(str(dir2))
        indexer._build_index()
        
        results = indexer.search("file")
        assert len(results) == 2
        
        # Add third root
        indexer.add_root(str(dir3))
        indexer._build_index()
        
        results = indexer.search("file")
        assert len(results) == 3
        
        # Remove one root
        indexer.remove_root(str(dir2))
        indexer._build_index()
        
        results = indexer.search("file")
        assert len(results) == 2
        names = [r["name"] for r in results]
        assert "file1.txt" in names
        assert "file3.txt" in names
        assert "file2.txt" not in names
        
        print("✓ test_incremental_root_management passed")


if __name__ == "__main__":
    print("Running integration tests for file search...\n")
    
    test_full_file_indexing_flow()
    test_multiple_roots()
    test_incremental_root_management()
    
    print("\n✅ All integration tests passed!")
