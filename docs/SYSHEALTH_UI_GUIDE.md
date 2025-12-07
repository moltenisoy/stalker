# SysHealth UI Guide

## Overview
This guide demonstrates how to use the enhanced SysHealth features through the Stalker UI.

## Accessing SysHealth

### Method 1: Direct Command
1. Press your hotkey (default: `Ctrl+Space`) to open Stalker
2. Type `/syshealth` to access the system monitor
3. Press `Enter` to see system metrics and processes

### Method 2: Search
1. Open Stalker
2. Start typing "syshealth" or "sys"
3. Select "/syshealth" from the results

## SysHealth Main View

When you type `/syshealth`, you'll see:

```
┌─────────────────────────────────────────────────────────────┐
│ CPU 45% | RAM 8.2/16.0 GB | Disk 2.3R/1.5W | Net 0.5↓/0.2↑  │
│ Monitor en tiempo real • Ctrl+W para terminar proceso        │
├─────────────────────────────────────────────────────────────┤
│ 🖥️ Task Manager                                              │
│ Administrador de tareas de Windows                          │
├─────────────────────────────────────────────────────────────┤
│ 🚀 Startup Apps                                              │
│ Aplicaciones de inicio de Windows                           │
├─────────────────────────────────────────────────────────────┤
│ 💿 Defragmentador de Disco                                  │
│ Optimizar y desfragmentar unidades                          │
├─────────────────────────────────────────────────────────────┤
│ 📊 Monitor de Recursos                                       │
│ Monitor detallado de recursos del sistema                   │
├─────────────────────────────────────────────────────────────┤
│ ℹ️ Información del Sistema                                   │
│ Información detallada del hardware y software               │
├─────────────────────────────────────────────────────────────┤
│ chrome.exe (PID 4567)                                       │
│ CPU 25.3% • RAM 512 MB • username                           │
├─────────────────────────────────────────────────────────────┤
│ Code.exe (PID 3456)                                         │
│ CPU 15.7% • RAM 1024 MB • username                          │
├─────────────────────────────────────────────────────────────┤
│ python.exe (PID 2345)                                       │
│ CPU 8.2% • RAM 256 MB • username                            │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. System Metrics Header
The top line shows real-time system metrics:
- **CPU**: Current CPU usage percentage
- **RAM**: Used GB / Total GB
- **Disk**: Read MB/s / Write MB/s
- **Net**: Download MB/s ↓ / Upload MB/s ↑

### 2. System Tool Shortcuts
Quick access to Windows system tools:

#### Task Manager
- Click to open Windows Task Manager
- Alternative to typing: `/syshealth task`
- Shows full system resource monitoring

#### Startup Apps
- Opens Windows Startup configuration
- Manage which apps start with Windows
- Alternative: `/syshealth startup`

#### Disk Defragmenter
- Opens Windows Disk Optimizer (dfrgui)
- Analyze and optimize drives
- Alternative: `/syshealth defrag`

#### Resource Monitor
- Opens detailed Windows Resource Monitor
- See real-time resource usage by process
- Alternative: `/syshealth resource`

#### System Information
- Opens Windows System Information tool
- View hardware and software details
- Alternative: `/syshealth info`

### 3. Process List
Shows top processes sorted by CPU or RAM:

#### Sort by CPU (Default)
```
Type: /syshealth
Shows: Processes sorted by CPU usage (highest first)
```

#### Sort by RAM
```
Type: /syshealth ram
Shows: Processes sorted by memory usage (highest first)
```

#### Process Information
Each process shows:
- Process name and PID
- CPU usage percentage
- RAM usage in MB
- Username running the process

### 4. Process Management

#### Kill Process with Ctrl+W
1. Navigate to a process using arrow keys
2. Press `Ctrl+W` to terminate
3. Confirm in the dialog (if enabled)

#### Confirmation Dialog
```
┌───────────────────────────────────────┐
│ Confirmar terminación de proceso      │
├───────────────────────────────────────┤
│ ¿Está seguro de que desea terminar    │
│ el proceso?                           │
│                                       │
│ Nombre: chrome.exe                    │
│ PID: 4567                             │
│                                       │
│ Esta acción no se puede deshacer.     │
├───────────────────────────────────────┤
│         [ Yes ]    [ No ]             │
└───────────────────────────────────────┘
```

#### Success/Failure Feedback
After attempting to kill a process:
- **Success**: "Proceso 'chrome.exe' (PID 4567) terminado exitosamente"
- **Failure**: "Acceso denegado para terminar proceso con PID 4567"
- **Not Found**: "Proceso con PID 4567 no existe"

## System Health Overlay

### Enabling the Overlay
1. Type `/overlay` in Stalker
2. Press Enter to toggle overlay visibility
3. Or enable permanently in settings:
   ```json
   {
     "syshealth": {
       "overlay_enabled": true
     }
   }
   ```

### Overlay Display
```
┌──────────────────────┐
│ CPU: 45%             │
│ RAM: 8.2 / 16.0 GB   │
│ Disk: 2.3R/1.5W MB/s │
│ Net: 0.5↓/0.2↑ MB/s  │
└──────────────────────┘
```

### Overlay Position
Configure in settings:
- `"top-left"`: Top left corner
- `"top-right"`: Top right corner (default)
- `"bottom-left"`: Bottom left corner
- `"bottom-right"`: Bottom right corner

### Overlay Updates
- **Normal Mode**: Updates every 5 seconds (configurable)
- **Performance Mode**: Updates every 10+ seconds (auto-adjusted)
- Always-on-top, non-intrusive
- Semi-transparent background

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Space` | Open/close Stalker |
| `↑` `↓` | Navigate process list |
| `Ctrl+W` | Kill selected process |
| `Enter` | Execute selected action |
| `Esc` | Close Stalker |
| `Ctrl+C` | Copy selected item |
| `Ctrl+O` | Open folder (files) |

## Search Filters

### Filter System Tools
```
/syshealth task       -> Show only Task Manager
/syshealth startup    -> Show only Startup Apps
/syshealth defrag     -> Show only Defragmenter
/syshealth resource   -> Show only Resource Monitor
/syshealth info       -> Show only System Info
```

### Filter Processes
```
/syshealth           -> Show processes by CPU
/syshealth ram       -> Show processes by RAM
/syshealth memoria   -> Show processes by RAM (Spanish)
```

## Configuration

### Access Settings
1. Type `>config` or `settings` in Stalker
2. Navigate to SysHealth section
3. Adjust settings as needed

### Available Settings
```json
{
  "syshealth": {
    "sampling_interval": 2.0,           // System metrics sample rate
    "process_refresh_interval": 3.0,    // Process list refresh rate
    "process_limit": 15,                // Max processes to show
    "confirm_kill": true,               // Confirm before killing
    "overlay_enabled": false,           // Show overlay by default
    "overlay_update_interval": 5.0,     // Overlay refresh rate
    "overlay_position": "top-right"     // Overlay position
  }
}
```

### Performance Mode
When performance mode is enabled:
- Sampling intervals are doubled
- Process refresh is slower
- Overlay updates less frequently
- Lower CPU overhead

Toggle performance mode:
1. Open settings (`>config`)
2. Toggle "Performance Mode"
3. All modules adjust automatically

## Best Practices

### For Normal Use
- Keep default settings (2s sampling, 3s process refresh)
- Enable confirmation for process kill
- Use overlay if you want always-visible metrics

### For Low-End Systems
- Enable Performance Mode
- Increase sampling intervals to 5s+
- Disable overlay
- Reduce process limit to 10 or less

### For Power Users
- Disable kill confirmation for faster workflow
- Enable overlay with top-right position
- Use keyboard shortcuts exclusively
- Set lower refresh intervals (1-2s)

## Troubleshooting

### "Acceso denegado" Error
- Some system processes require administrator privileges
- Try running Stalker as administrator
- Or ignore protected system processes

### Overlay Not Showing
1. Check if enabled: `/overlay` command
2. Check overlay_enabled in config
3. Check if optimizer module is enabled
4. Try repositioning: Change overlay_position

### High CPU Usage
1. Enable Performance Mode
2. Increase sampling_interval to 5.0+
3. Increase process_refresh_interval to 5.0+
4. Disable overlay
5. Reduce process_limit

### Process List Not Updating
1. Check if background refresh started
2. Restart Stalker
3. Check process_refresh_interval setting
4. Look for errors in logs

## Tips & Tricks

### Quick Task Manager
- Type `task` → Instant Task Manager shortcut appears
- Faster than `Ctrl+Shift+Esc`

### Monitor Specific Process
- Type `/syshealth` + process name to filter
- Example: `/syshealth chrome`

### Copy Process Info
- Select a process
- Press `Ctrl+C` to copy details
- Paste into notes or tickets

### Overlay as Status Bar
- Enable overlay
- Position at bottom-right
- Use as permanent status indicator
- Minimal distraction

### Safe Process Hunting
- Use RAM sort to find memory leaks
- Use CPU sort to find performance hogs
- Kill with Ctrl+W after confirmation
- Monitor impact in real-time

## Advanced Usage

### Scripting with System Tools
```python
from modules.syshealth import SysHealth

# Open multiple tools programmatically
SysHealth.open_task_manager()
SysHealth.open_resource_monitor()
```

### Custom Monitoring
```python
# Get metrics programmatically
syshealth = SysHealth(config)
snap = syshealth.snapshot()

# Alert on high CPU
if snap.cpu_percent > 90:
    print("CPU usage critical!")
```

### Process Automation
```python
# Find and kill process by name
procs = syshealth.top_procs(by="cpu", limit=100)
for proc in procs:
    if "unwanted.exe" in proc.name.lower():
        success, msg = syshealth.kill(proc.pid)
        print(msg)
```

## Future Features (Roadmap)
- Process filtering by name/user
- Historical graphs
- Alert thresholds
- Network breakdown by process
- Disk I/O by process
- Custom metrics plugins
- Export to file/database
