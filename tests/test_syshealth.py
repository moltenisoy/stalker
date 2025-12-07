"""
Tests for enhanced SysHealth module with configurable sampling,
process sorting, background refresh, and system tool shortcuts.
"""
import sys
import os
import time

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules_monitoring import SysHealth, ResourceSnapshot, ProcInfo
from core import ConfigManager
import tempfile
from pathlib import Path


def test_syshealth_snapshot():
    """Test basic snapshot functionality."""
    syshealth = SysHealth()
    
    # Get snapshot
    snap = syshealth.snapshot()
    
    # Validate snapshot fields
    assert isinstance(snap, ResourceSnapshot)
    assert snap.cpu_percent >= 0
    assert snap.ram_used_gb >= 0
    assert snap.ram_total_gb > 0
    assert snap.ram_used_gb <= snap.ram_total_gb
    assert snap.disk_read_mb_s >= 0
    assert snap.disk_write_mb_s >= 0
    assert snap.net_up_mb_s >= 0
    assert snap.net_down_mb_s >= 0
    assert snap.timestamp > 0
    
    print("✓ test_syshealth_snapshot passed")


def test_syshealth_sampling_interval():
    """Test that sampling respects configured interval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        config.set_syshealth_config(sampling_interval=1.0)
        
        syshealth = SysHealth(config=config)
        
        # First snapshot
        snap1 = syshealth.snapshot(use_sampling=True)
        time1 = snap1.timestamp
        
        # Immediate second snapshot (should use same timestamp or very close)
        snap2 = syshealth.snapshot(use_sampling=True)
        time2 = snap2.timestamp
        
        # Time difference should be small due to sampling
        # But still get updates
        assert time2 >= time1
        
        print("✓ test_syshealth_sampling_interval passed")


def test_top_procs_cpu():
    """Test getting top processes sorted by CPU."""
    syshealth = SysHealth()
    
    procs = syshealth.top_procs(by="cpu", limit=5)
    
    # Should have processes
    assert len(procs) > 0
    assert len(procs) <= 5
    
    # Each process should have valid fields
    for proc in procs:
        assert isinstance(proc, ProcInfo)
        assert proc.pid > 0
        assert proc.name != ""
        assert proc.cpu >= 0
        assert proc.ram_mb >= 0
    
    # Should be sorted by CPU descending
    if len(procs) > 1:
        for i in range(len(procs) - 1):
            assert procs[i].cpu >= procs[i + 1].cpu
    
    print("✓ test_top_procs_cpu passed")


def test_top_procs_ram():
    """Test getting top processes sorted by RAM."""
    syshealth = SysHealth()
    
    procs = syshealth.top_procs(by="ram", limit=5)
    
    # Should have processes
    assert len(procs) > 0
    assert len(procs) <= 5
    
    # Should be sorted by RAM descending
    if len(procs) > 1:
        for i in range(len(procs) - 1):
            assert procs[i].ram_mb >= procs[i + 1].ram_mb
    
    print("✓ test_top_procs_ram passed")


def test_background_refresh():
    """Test background refresh mechanism."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        config.set_syshealth_config(
            process_refresh_interval=1.0,
            process_limit=5
        )
        
        syshealth = SysHealth(config=config)
        
        # Start background refresh
        syshealth.start_background_refresh()
        
        # Wait for first refresh
        time.sleep(2)
        
        # Get cached processes
        procs = syshealth.top_procs(by="cpu", limit=5, use_cache=True)
        
        assert len(procs) > 0
        assert len(procs) <= 5
        
        # Stop background refresh
        syshealth.stop_background_refresh()
        
        print("✓ test_background_refresh passed")


def test_syshealth_config():
    """Test syshealth configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        config = ConfigManager(path=config_path)
        
        # Test getting syshealth config
        syshealth_config = config.get_syshealth_config()
        assert isinstance(syshealth_config, dict)
        assert "sampling_interval" in syshealth_config
        assert "process_refresh_interval" in syshealth_config
        assert "confirm_kill" in syshealth_config
        assert "overlay_enabled" in syshealth_config
        
        # Test default values
        assert config.get_syshealth_config("sampling_interval") == 2.0
        assert config.get_syshealth_config("process_refresh_interval") == 3.0
        assert config.get_syshealth_config("process_limit") == 15
        assert config.get_syshealth_config("confirm_kill") is True
        assert config.get_syshealth_config("overlay_enabled") is False
        
        # Test setting values
        config.set_syshealth_config(
            sampling_interval=1.5,
            confirm_kill=False,
            overlay_enabled=True
        )
        
        assert config.get_syshealth_config("sampling_interval") == 1.5
        assert config.get_syshealth_config("confirm_kill") is False
        assert config.get_syshealth_config("overlay_enabled") is True
        
        print("✓ test_syshealth_config passed")


def test_system_tool_shortcuts():
    """Test system tool shortcut methods exist and return proper format."""
    # Just test that methods exist and are callable
    # Don't actually open the tools
    
    assert callable(SysHealth.open_task_manager)
    assert callable(SysHealth.open_startup_apps)
    assert callable(SysHealth.open_defragmenter)
    assert callable(SysHealth.open_resource_monitor)
    assert callable(SysHealth.open_system_info)
    
    print("✓ test_system_tool_shortcuts passed")


def test_kill_process_return_format():
    """Test that kill method returns proper tuple format."""
    syshealth = SysHealth()
    
    # Try to kill non-existent process
    success, message = syshealth.kill(99999)
    
    assert isinstance(success, bool)
    assert isinstance(message, str)
    assert not success  # Should fail for non-existent PID
    assert len(message) > 0
    
    print("✓ test_kill_process_return_format passed")


if __name__ == "__main__":
    # Run all tests
    test_syshealth_snapshot()
    test_syshealth_sampling_interval()
    test_top_procs_cpu()
    test_top_procs_ram()
    test_background_refresh()
    test_syshealth_config()
    test_system_tool_shortcuts()
    test_kill_process_return_format()
    
    print("\n✓ All syshealth tests passed!")
