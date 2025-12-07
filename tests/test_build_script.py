"""
Tests for the build script functionality.
"""
import sys
import hashlib
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_calculate_checksum():
    """Test checksum calculation."""
    from build_exe import calculate_checksum
    
    # Create a temporary test file
    test_file = Path("/tmp/test_checksum.txt")
    test_content = b"Hello, World!"
    
    test_file.write_bytes(test_content)
    
    try:
        # Calculate checksums
        sha256 = calculate_checksum(test_file, 'sha256')
        md5 = calculate_checksum(test_file, 'md5')
        
        # Verify SHA-256
        expected_sha256 = hashlib.sha256(test_content).hexdigest()
        assert sha256 == expected_sha256
        
        # Verify MD5
        expected_md5 = hashlib.md5(test_content).hexdigest()
        assert md5 == expected_md5
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_get_version():
    """Test version extraction."""
    from build_exe import get_version
    
    version = get_version()
    
    # Version should be a string
    assert isinstance(version, str)
    
    # Version should have at least one dot (e.g., 2.0.0)
    assert '.' in version or version == "2.0.0"


def test_config_default_exists():
    """Test that default config file exists."""
    config_file = Path(__file__).parent.parent / "config.default.json"
    
    assert config_file.exists(), "config.default.json should exist"
    
    # Verify it's valid JSON
    import json
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Check for required keys
    assert "ui" in config
    assert "hotkey" in config
    assert "modules" in config


def test_hook_file_exists():
    """Test that PyInstaller hook exists."""
    hook_file = Path(__file__).parent.parent / "hooks" / "hook-stalker.py"
    
    assert hook_file.exists(), "hook-stalker.py should exist"
    
    # Verify it contains datas
    content = hook_file.read_text()
    assert "datas" in content
    assert "config.default.json" in content


def test_build_script_exists():
    """Test that build script exists and is executable."""
    build_script = Path(__file__).parent.parent / "build_exe.py"
    
    assert build_script.exists(), "build_exe.py should exist"
    
    # Verify main function exists
    content = build_script.read_text()
    assert "def main():" in content
    assert "pyinstaller" in content.lower()


def test_github_workflow_exists():
    """Test that GitHub workflow exists."""
    workflow_file = Path(__file__).parent.parent / ".github" / "workflows" / "build-release.yml"
    
    assert workflow_file.exists(), "build-release.yml should exist"
    
    # Verify it contains required steps
    content = workflow_file.read_text()
    assert "pyinstaller" in content.lower()
    assert "build_exe.py" in content
    assert "upload-artifact" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
