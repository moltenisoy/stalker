# SysHealth Module Enhancements

## Overview
This document describes the enhancements made to the SysHealth module for system monitoring and process management with low overhead and configurable sampling.

## Features

### 1. Configurable Sampling
The module now supports configurable sampling intervals to reduce system overhead while still providing accurate metrics.

**Configuration Options (in config.json):**
```json
{
  "syshealth": {
    "sampling_interval": 2.0,           // Seconds between system metric samples
    "process_refresh_interval": 3.0,    // Seconds between process list updates
    "process_limit": 15,                // Max processes to display
    "confirm_kill": true,               // Ask for confirmation before killing
    "overlay_enabled": false,           // Show persistent overlay
    "overlay_update_interval": 5.0,     // Overlay update frequency
    "overlay_position": "top-right"     // Position: top-left, top-right, bottom-left, bottom-right
  }
}
```

**Benefits:**
- Reduced CPU usage when monitoring system resources
- Configurable based on user needs and system capabilities
- Respects performance mode (doubles update intervals)

### 2. Background Process Refresh
Process lists are now refreshed in a background thread, preventing UI blocking.

**Features:**
- Automatic refresh at configurable intervals
- Cached results for instant display
- Sort order detection (CPU or RAM)
- Thread-safe with lock protection

**Usage:**
```python
syshealth = SysHealth(config=config)
syshealth.start_background_refresh()

# Get cached processes (instant)
procs = syshealth.top_procs(by="cpu", limit=15, use_cache=True)

# Stop when done
syshealth.stop_background_refresh()
```

### 3. Process Sorting
Processes can be sorted by CPU usage or RAM consumption.

**In UI:**
- Type `/syshealth` to see processes sorted by CPU
- Type `/syshealth ram` to see processes sorted by RAM
- Press `Ctrl+W` on a process to terminate it with confirmation

**Process Display Format:**
```
ProcessName.exe (PID 1234)
CPU 25.3% • RAM 512 MB • username
```

### 4. Safe Process Kill with Confirmation
Enhanced process termination with optional confirmation dialog.

**Features:**
- Optional confirmation dialog (configurable)
- Graceful termination (SIGTERM) with fallback to force kill
- Detailed error messages
- Success/failure feedback

**Keyboard Shortcut:**
- Select a process in `/syshealth` view
- Press `Ctrl+W` to kill the process
- Confirm in the dialog (if enabled)

**Return Format:**
```python
success, message = syshealth.kill(pid, force=False)
# Returns: (True, "Process 'chrome.exe' (PID 1234) terminated successfully")
# Or: (False, "Access denied for process with PID 1234")
```

### 5. System Tool Shortcuts
Quick access to Windows system management tools.

**Available Tools:**
- **Task Manager** (`taskmgr.exe`) - Full system task manager
- **Startup Apps** - Windows startup configuration
- **Disk Defragmenter** (`dfrgui.exe`) - Disk optimization
- **Resource Monitor** (`resmon.exe`) - Detailed resource monitoring
- **System Information** (`msinfo32.exe`) - Hardware/software details

**Usage:**
- Type `/syshealth` and select a tool from the list
- Each tool provides success/failure feedback
- Tools open in separate windows

**Examples in Search:**
```
/syshealth task    -> Shows Task Manager
/syshealth startup -> Shows Startup Apps
/syshealth defrag  -> Shows Disk Defragmenter
```

### 6. System Health Overlay
Persistent, non-intrusive overlay showing real-time system metrics.

**Features:**
- Lightweight, always-on-top widget
- Shows CPU, RAM, Disk I/O, and Network traffic
- Configurable position (corners of screen)
- Respects performance mode (reduces update frequency)
- Toggleable with `/overlay` command

**Display Format:**
```
CPU: 45%
RAM: 8.2 / 16.0 GB
Disk: 2.3R/1.5W MB/s
Net: 0.5↓/0.2↑ MB/s
```

**Toggle Overlay:**
- Type `/overlay` in the launcher
- Or call `app.toggle_syshealth_overlay()` programmatically

**Configuration:**
```python
config.set_syshealth_config(
    overlay_enabled=True,
    overlay_update_interval=5.0,
    overlay_position="top-right"
)
```

## Performance Mode Integration

The SysHealth module respects the global performance mode:
- **Normal Mode:** Full-speed updates, all features enabled
- **Performance Mode:** 
  - Doubled sampling intervals
  - Reduced process refresh rate
  - Overlay updates less frequently
  - Lower CPU overhead

## Architecture

### Background Refresh Thread
```
main thread                  background thread
    |                               |
    |-- start_background_refresh() |
    |                               |-- while running:
    |                               |     wait for interval
    |                               |     fetch processes
    |                               |     update cache (locked)
    |                               |
    |-- top_procs(use_cache=True)  |
    |   returns cached data         |
    |                               |
    |-- stop_background_refresh()   |
    |                               |-- exit thread
```

### Sampling Flow
```
snapshot(use_sampling=True)
    |
    +-- Check time since last sample
    |   |
    |   +-- Within interval? Return quick update
    |   |
    |   +-- Past interval? Full refresh
    |
    +-- Update disk/net counters
    |
    +-- Return ResourceSnapshot
```

## API Reference

### SysHealth Class

#### Constructor
```python
SysHealth(config: Optional[ConfigManager] = None)
```

#### Methods
- `snapshot(use_sampling: bool = True) -> ResourceSnapshot`
  - Get current system metrics
  - `use_sampling`: Respect sampling interval for low overhead

- `top_procs(by: Literal["cpu", "ram"] = "cpu", limit: int = 8, use_cache: bool = True) -> List[ProcInfo]`
  - Get top processes sorted by CPU or RAM
  - `use_cache`: Use cached results from background thread

- `kill(pid: int, force: bool = False) -> tuple[bool, str]`
  - Terminate a process
  - `force`: Use kill() instead of terminate()
  - Returns: (success, message)

- `start_background_refresh()`
  - Start background thread for process list updates

- `stop_background_refresh()`
  - Stop background refresh thread

#### Static Methods
- `open_task_manager() -> tuple[bool, str]`
- `open_startup_apps() -> tuple[bool, str]`
- `open_defragmenter() -> tuple[bool, str]`
- `open_resource_monitor() -> tuple[bool, str]`
- `open_system_info() -> tuple[bool, str]`

### SysHealthOverlay Class

#### Constructor
```python
SysHealthOverlay(syshealth: SysHealth, config: Optional[ConfigManager] = None)
```

#### Methods
- `toggle_visibility()`
  - Show/hide the overlay

- `update_config(config: ConfigManager)`
  - Update configuration and refresh settings

## Usage Examples

### Basic System Monitoring
```python
from modules.syshealth import SysHealth

# Create instance with config
syshealth = SysHealth(config=config)

# Get system snapshot
snap = syshealth.snapshot()
print(f"CPU: {snap.cpu_percent}%")
print(f"RAM: {snap.ram_used_gb:.1f}/{snap.ram_total_gb:.1f} GB")
```

### Process Management
```python
# Start background refresh
syshealth.start_background_refresh()

# Get top CPU processes
cpu_procs = syshealth.top_procs(by="cpu", limit=10)
for proc in cpu_procs:
    print(f"{proc.name} - CPU: {proc.cpu}%, RAM: {proc.ram_mb} MB")

# Kill a process
success, msg = syshealth.kill(1234)
print(msg)

# Stop refresh
syshealth.stop_background_refresh()
```

### System Tools
```python
# Open Task Manager
success, msg = SysHealth.open_task_manager()
if success:
    print("Task Manager opened")
else:
    print(f"Error: {msg}")
```

### Overlay
```python
from ui.syshealth_overlay import SysHealthOverlay

# Create overlay
overlay = SysHealthOverlay(syshealth, config)
overlay.show()

# Toggle visibility
overlay.toggle_visibility()
```

## Testing

Run the comprehensive test suite:
```bash
python tests/test_syshealth.py
```

Tests cover:
- Snapshot accuracy
- Sampling intervals
- Process sorting
- Background refresh
- Configuration management
- System tool methods
- Kill process functionality

## Future Enhancements

Potential improvements:
1. Process filtering by name or user
2. Historical resource tracking with graphs
3. Alert thresholds for high CPU/RAM usage
4. Network traffic breakdown by process
5. Disk I/O breakdown by process
6. Custom metrics and plugins
7. Export metrics to file/database

## Security Considerations

- Process termination requires appropriate permissions
- Access denied errors are handled gracefully
- No elevation of privileges attempted
- System tools launched with current user context
- Background thread is daemon (auto-cleanup on exit)

## Compatibility

- **OS:** Windows 10/11 (uses Windows-specific tools)
- **Python:** 3.7+
- **Dependencies:** psutil >= 5.9.8
- **GUI:** PySide6 for overlay and dialogs
