# File Indexer and Search Improvements

This document describes the enhancements made to the file indexer, app launcher, and search functionality.

## Features Implemented

### 1. File Indexer Root Configuration

File indexer roots are now persisted in the configuration file, allowing you to customize which directories are indexed.

**Configuration Format:**
```json
{
  "file_indexer": {
    "roots": ["C:\\Users\\YourName\\Documents", "D:\\Projects"],
    "watch_enabled": false
  }
}
```

**Default Behavior:**
- If no roots are specified, the user's home directory is indexed by default
- Roots are automatically saved when changed

**API Usage:**
```python
from core.config import ConfigManager

config = ConfigManager()

# Get current roots
roots = config.get_file_indexer_roots()

# Set new roots
config.set_file_indexer_roots(["C:\\MyFolder", "D:\\AnotherFolder"])

# Enable watchdog (optional)
config.set_file_indexer_watch_enabled(True)
```

### 2. Dynamic Root Management

Add or remove indexer roots dynamically without replacing the entire configuration.

```python
from modules.file_indexer import FileIndexer

indexer = FileIndexer()

# Add a new root
indexer.add_root("E:\\NewFolder")

# Remove a root
indexer.remove_root("E:\\NewFolder")

# Get current roots
print(indexer.roots)
```

### 3. File Search Actions

File search results now include additional actions accessible via keyboard shortcuts:

**Ctrl+O**: Open the containing folder and highlight the file in Windows Explorer
**Ctrl+C**: Copy the file path to clipboard (default behavior)

**Implementation Details:**
- File results include a `meta` dictionary with action callbacks
- `open_folder_action`: Opens Windows Explorer with /select parameter
- `copy_path_action`: Copies the full file path to clipboard

### 4. App Detection and Caching

The app launcher can now automatically detect installed applications.

**Scan Locations:**
- Start Menu (AppData and ProgramData)
- Program Files directories

**Usage:**
```python
from modules.app_launcher import AppLauncher

launcher = AppLauncher()

# Scan and cache all installed apps
count = launcher.scan_installed_apps()
print(f"Found {count} applications")

# Add a custom alias
launcher.add_alias("calc", "Calculator", "calc.exe")

# Ensure cache is loaded (lazy loading)
launcher.ensure_cache_loaded()
```

**Cache Behavior:**
- Apps without aliases are cleared when rescanning
- Apps with custom aliases are preserved
- Cache is automatically loaded on first search if empty

### 5. Persistent App Aliases

Create persistent shortcuts for frequently used applications.

**Storage:**
- Aliases are stored in the SQLite database
- Survive application restarts and cache refreshes

**Example:**
```python
# Add alias for quick access
launcher.add_alias("vscode", "Visual Studio Code", "C:\\Program Files\\VSCode\\code.exe")

# Now searching for "vscode" will find this app
```

### 6. Search Result Scoring

Results are automatically prioritized based on type and relevance.

**Priority Order (Highest to Lowest):**
1. Calculator (100 points)
2. Apps (90 points)
3. AI (85 points)
4. Clipboard (80 points)
5. Snippets (75 points)
6. Notes (70 points)
7. Quicklinks (65 points)
8. Files (60 points)
9. Commands (50 points)
10. Macros (45 points)
11. System Health (40 points)
12. General (30 points)

**Match Bonuses:**
- Exact match: +50 points
- Prefix match: +30 points
- Contains match: +10 points

**Example:**
```
Query: "calc"

Results (ordered by score):
1. Calculator (calculator) - 100 + 0 = 100 points (exact match on app type)
2. calc.exe (app) - 90 + 50 = 140 points (exact match)
3. calculate.py (file) - 60 + 30 = 90 points (prefix match)
4. my calculations (file) - 60 + 10 = 70 points (contains match)
```

### 7. Logging and Diagnostics

All indexing operations are logged for troubleshooting.

**Log Location:** `%USERPROFILE%\.fastlauncher\logs\app.log`

**Logged Events:**
- Indexing start/stop
- Roots scanned
- Files indexed count
- Errors (silent, don't break indexing)
- Watchdog start/stop

**Get Statistics:**
```python
stats = indexer.get_stats()
print(f"Files indexed: {stats['files_indexed']}")
print(f"Errors: {stats['errors']}")
print(f"Last run: {stats['last_run']}")
```

**Diagnostics Snapshot:**
```python
from modules.diagnostics import diag_snapshot

snapshot = diag_snapshot(file_indexer=indexer)
print(snapshot)
# Output includes:
# - timestamp
# - log_file path
# - file_indexer stats (files_indexed, errors, last_run, roots)
```

### 8. Watchdog Support (Optional)

Enable real-time file system monitoring for incremental indexing.

**Configuration:**
```python
config.set_file_indexer_watch_enabled(True)
```

**Behavior:**
- Monitors all configured roots
- Detects file creation, deletion, and modification
- Framework for incremental updates (extensible)
- Automatically starts/stops with indexer pause state

**Note:** Watchdog is optional and disabled by default. Enable it if you want real-time updates.

## Storage Schema

### File Index Table
```sql
CREATE TABLE file_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    drive TEXT,
    name TEXT,
    updated_at REAL NOT NULL
);
CREATE INDEX idx_file_name ON file_index(name);
CREATE INDEX idx_file_drive ON file_index(drive);
```

### Apps Table
```sql
CREATE TABLE apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    alias TEXT UNIQUE,
    created_at REAL NOT NULL
);
```

## API Reference

### FileIndexer

**Methods:**
- `start()`: Start indexing in background thread
- `pause(value: bool)`: Pause or resume indexing
- `set_roots(roots: List[str])`: Set roots and persist to config
- `add_root(root: str)`: Add a root incrementally
- `remove_root(root: str)`: Remove a root incrementally
- `search(q: str, limit: int = 80)`: Search indexed files
- `get_stats()`: Get indexing statistics

### AppLauncher

**Methods:**
- `scan_installed_apps()`: Scan and cache installed apps
- `add_alias(alias: str, name: str, path: str)`: Add persistent alias
- `ensure_cache_loaded()`: Lazy load cache if needed
- `resolve(text: str)`: Resolve alias to SearchResult
- `search(q: str)`: Search apps by name/path/alias
- `launch(path: str)`: Launch application

### Storage

**New Methods:**
- `replace_file_index(records: List[tuple])`: Replace entire index
- `list_files(q: str = "", limit: int = 80)`: Search files
- `get_app_by_alias(alias: str)`: Get app by alias
- `list_apps(q: str = "", limit: int = 50)`: Search apps
- `add_app(name: str, path: str, alias: str = None)`: Add/update app
- `clear_app_cache()`: Clear non-aliased apps

### ConfigManager

**New Methods:**
- `get_file_indexer_roots()`: Get configured roots
- `set_file_indexer_roots(roots: list)`: Set roots
- `get_file_indexer_watch_enabled()`: Get watchdog status
- `set_file_indexer_watch_enabled(enabled: bool)`: Set watchdog status

## Performance Considerations

1. **Initial Indexing**: First-time indexing may take time depending on the size of your roots
2. **Memory Usage**: Large directories will use more memory during indexing
3. **Watchdog**: Enabling watchdog adds a small overhead for file system monitoring
4. **Performance Mode**: When enabled, file indexer is automatically paused

## Error Handling

- Individual file errors are logged but don't stop indexing
- Invalid paths are skipped silently
- Database errors are logged to diagnostics
- All exceptions are caught and logged without breaking the user experience

## Migration Notes

If you're upgrading from a previous version:

1. Configuration file will automatically include the new `file_indexer` section
2. Existing file index will be preserved
3. Apps table will be created if it doesn't exist
4. No manual migration needed

## Testing

Comprehensive test suites are included:

- `tests/test_storage.py`: Storage layer tests
- `tests/test_file_indexer.py`: Indexer functionality tests
- `tests/test_search_scoring.py`: Scoring algorithm tests
- `tests/test_integration_file_search.py`: End-to-end integration tests

Run tests:
```bash
python tests/test_storage.py
python tests/test_file_indexer.py
python tests/test_search_scoring.py
python tests/test_integration_file_search.py
```

## Security

- CodeQL security scanning: 0 alerts
- No secrets in code
- Proper error handling prevents information leakage
- File paths are validated before use
