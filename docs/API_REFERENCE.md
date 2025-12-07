# Stalker API Reference

Complete technical reference for all modules, classes, and functions in Stalker.

---

## Table of Contents

1. [Core Modules](#core-modules)
2. [Feature Modules](#feature-modules)
3. [UI Components](#ui-components)
4. [Utilities](#utilities)

---

## Core Modules

### core/app.py

#### `LauncherApp`

Main application class that manages the lifecycle and global state.

**Constructor:**
```python
LauncherApp(qt_app: QApplication)
```

**Methods:**

- `start()`: Initialize and start the application
  - Applies theme from config
  - Ensures autostart
  - Registers global hotkey
  - Initializes overlay if enabled

- `toggle_visibility()`: Toggle launcher window visibility
  - Hides if visible and active
  - Shows and centers if hidden

- `toggle_syshealth_overlay()`: Toggle system health overlay
  - Initializes overlay if not created
  - Shows/hides overlay window

**Attributes:**
- `qt_app`: QApplication instance
- `config`: ConfigManager instance
- `window`: LauncherWindow instance
- `hotkey`: GlobalHotkey instance

---

### core/engine.py

#### `SearchEngine`

Main search and action routing engine.

**Constructor:**
```python
SearchEngine(config: Optional[ConfigManager] = None)
```

**Modules Initialized:**
- Calculator
- ClipboardManager
- SnippetManager
- AppLauncher
- FileIndexer
- Quicklinks
- MacroRecorder
- SysHealth
- AIAssistant
- NotesManager
- PluginShell
- **NEW:** IntentRouter
- **NEW:** CompoundActionManager
- **NEW:** ContextProfileManager
- **NEW:** FlowCommandManager
- **NEW:** ContextualActionsManager

**Methods:**

- `search(query: str) -> List[SearchResult]`: Main search method
  - Detects command flags (`/files`, `/clipboard`, etc.)
  - Routes to appropriate module
  - Detects intent for smart suggestions
  - Returns scored and sorted results

- `_config_results() -> List[SearchResult]`: Returns settings panel result

- `_show_ai_response(prompt: str)`: Execute AI query and show response

- `_clipboard_results(q: str) -> List[SearchResult]`: Search clipboard history

- `_file_results(q: str) -> List[SearchResult]`: Search file index

- `_syshealth_results(q: str) -> List[SearchResult]`: System health info and processes

- `_context_results() -> List[SearchResult]`: **NEW** Context-aware actions based on active window

- `_intent_suggestions(intent: Intent) -> List[SearchResult]`: **NEW** Suggest actions based on detected intent

- `_apply_scoring(results: List[SearchResult], query: str) -> List[SearchResult]`: Apply scoring and sort results

#### `SearchResult` (dataclass)

Represents a search result item.

**Fields:**
```python
title: str
subtitle: str = ""
action: Optional[Callable] = None
copy_text: Optional[str] = None
group: str = "general"
meta: dict = None
score: float = 0.0
```

---

### core/config.py

#### `ConfigManager`

Manages application configuration with persistence.

**Methods:**

- `get_ui(key: str = None)`: Get UI settings
- `get_module_enabled(key: str) -> bool`: Check if module is enabled
- `set_module_enabled(key: str, val: bool)`: Enable/disable module
- `get_performance_mode() -> bool`: Check performance mode
- `toggle_performance_mode(val: bool)`: Toggle performance mode
- `get_syshealth_config(key: str)`: Get syshealth configuration
- `save()`: Persist configuration to disk
- `export(path: Path)`: Export config to file
- `import_file(path: Path)`: Import config from file

**Configuration Structure:**
```json
{
  "hotkey": "ctrl+space",
  "ui": {
    "theme": "dark",
    "accent": "#3a86ff",
    "font_family": "Segoe UI",
    "font_size": 10,
    "opacity_active": 0.98,
    "opacity_inactive": 0.85,
    "effects": true
  },
  "modules": {
    "clipboard": true,
    "snippets": true,
    "files": true,
    "links": true,
    "macros": true,
    "ai": true,
    "optimizer": true
  },
  "performance_mode": false,
  "syshealth": {
    "refresh_interval": 2,
    "overlay_enabled": true,
    "overlay_position": "top-right",
    "overlay_opacity": 0.9
  }
}
```

---

### core/storage.py

#### `Storage`

SQLite database wrapper for persistent storage.

**Tables:**
- `clips`: Clipboard history
- `snippets`: Text snippets
- `notes`: Markdown notes
- `quicklinks`: Quick links
- `macros`: Recorded macros

**Methods:**

- `add_clip(kind: str, content: bytes, metadata: dict)`: Add clipboard entry
- `list_clips(q: str = "", limit: int = 50) -> List[dict]`: Search clipboard
- `add_snippet(name: str, trigger: str, body: str, hotkey: str)`: Add snippet
- `list_snippets(q: str = "", limit: int = 30) -> List[dict]`: Search snippets
- `get_snippet_by_trigger(trigger: str) -> Optional[dict]`: Get snippet by trigger

---

### core/intent_router.py

#### `IntentType` (Enum)

Types of intents that can be detected:
- `OPEN_APP`
- `SEARCH_FILE`
- `PASTE_SNIPPET`
- `SYSTEM_ACTION`
- `CLIPBOARD_ACTION`
- `FILE_ACTION`
- `TEXT_TRANSFORM`
- `CALCULATE`
- `TRANSLATE`
- `WEB_SEARCH`
- `UNKNOWN`

#### `Intent`

Represents a detected user intent.

**Constructor:**
```python
Intent(intent_type: IntentType, confidence: float, params: Dict = None)
```

**Attributes:**
- `type`: IntentType
- `confidence`: float (0.0 to 1.0)
- `params`: dict of extracted parameters

#### `IntentRouter`

Local intent detection and routing.

**Methods:**

- `detect_intent(query: str) -> Intent`: Detect primary intent from query
  - Returns Intent with type, confidence, and extracted parameters
  - All processing happens locally

- `detect_all_intents(query: str) -> List[Intent]`: Detect multiple possible intents

**Pattern Matching:**
- Uses regex patterns for each intent type
- Confidence scoring based on pattern match quality
- Extracts relevant parameters (app name, file name, etc.)

---

### core/compound_actions.py

#### `ActionStep` (dataclass)

Single step in a compound action.

**Fields:**
```python
name: str
description: str
action: Callable
params: Dict[str, Any] = None
requires_confirmation: bool = False
```

#### `CompoundAction`

Multi-step compound action.

**Constructor:**
```python
CompoundAction(name: str, description: str, steps: List[ActionStep])
```

**Methods:**

- `execute_next() -> bool`: Execute next step, returns True if more steps remain
- `reset()`: Reset to first step
- `get_current_step() -> Optional[ActionStep]`: Get current step

#### `CompoundActionManager`

Manages compound actions and workflows.

**Built-in Actions:**
- `zip_and_share`: Compress files and copy path
- `copy_and_open`: Copy path and open folder
- `convert_and_paste`: Convert text and paste
- `translate_and_paste`: Translate and paste
- `clean_and_paste`: Clean format and paste

**Methods:**

- `register_action(action_id: str, name: str, description: str, steps: List[ActionStep])`: Register new action

- `get_action(action_id: str) -> Optional[CompoundAction]`: Get action by ID

- `suggest_actions_for_context(context: str, selected_item: Optional[Dict]) -> List[SearchResult]`: Suggest actions based on context
  - Context types: "file_selected", "text_copied"

**Action Implementations:**
- `_zip_files(filepath: str)`: Create zip archive
- `_copy_path_to_clipboard(path: str)`: Copy path to clipboard
- `_open_folder(path: str)`: Open folder in explorer
- `_convert_text(text: str, target_format: str)`: Convert text format
- `_translate_text(text: str, target_lang: str)`: Translate text
- `_paste_text(text: str)`: Paste using keystroke
- `_clean_format(text: str)`: Clean text formatting

---

### core/context_profiles.py

#### `ContextAction` (dataclass)

Action available in a specific context.

**Fields:**
```python
name: str
description: str
trigger: str  # Hotkey or command trigger
action_type: str  # "snippet", "command", "flow"
action_data: Dict
```

#### `AppProfile` (dataclass)

Profile for a specific application.

**Fields:**
```python
app_name: str
display_name: str
window_class: str = ""
window_title_pattern: str = ""
actions: List[ContextAction] = []
snippets: Dict[str, str] = {}
shortcuts: Dict[str, str] = {}
```

#### `ContextProfileManager`

Manages contextual profiles per application.

**Built-in Profiles:**
- VSCode
- Browser (Chrome/Firefox/Edge)
- Figma
- File Explorer

**Methods:**

- `get_profile(app_name: str) -> Optional[AppProfile]`: Get profile by name

- `get_profile_for_window(window_title: str, window_class: str) -> Optional[AppProfile]`: Match profile by window info

- `get_actions_for_profile(profile: AppProfile) -> List[SearchResult]`: Get actions as search results

- `get_snippets_for_profile(profile: AppProfile, query: str) -> List[SearchResult]`: Get snippets as search results

- `create_profile(app_name: str, display_name: str) -> AppProfile`: Create new profile

- `add_action_to_profile(app_name: str, action: ContextAction)`: Add action to profile

- `save_profile(profile: AppProfile)`: Save profile to disk

**Storage:**
- Profiles saved as JSON in `~/.stalker/profiles/`

---

### core/flow_commands.py

#### `FlowStep` (dataclass)

Single step in a flow.

**Fields:**
```python
action: str  # Action type
params: Dict[str, Any]
condition: Optional[str] = None
```

#### `FlowCommand` (dataclass)

Complete flow command/recipe.

**Fields:**
```python
name: str
description: str
app_context: str
steps: List[FlowStep]
variables: Dict[str, Any]
```

#### `FlowCommandExecutor`

Executes flow commands defined in DSL.

**Action Handlers:**
- `keystroke`: Send keyboard input
- `clipboard`: Read/write clipboard
- `command`: Execute system command
- `wait`: Delay execution
- `paste`: Paste text with IME safety
- `copy`: Copy to clipboard
- `open`: Open file/folder
- `save`: Trigger save (Ctrl+S)
- `transform`: Transform text

**Methods:**

- `execute(flow: FlowCommand, context: Dict[str, Any]) -> bool`: Execute flow with context

**Variable Substitution:**
- `${variable_name}` in strings replaced with values
- Built-in variables: `clipboard_content`, `transformed_text`

#### `FlowCommandManager`

Manages flow commands - loading, saving, executing.

**Built-in Flows:**
- `copy_current_path`: Copy path from explorer
- `open_terminal_here`: Open CMD in current folder
- `extract_links`: Extract URLs from clipboard
- `clean_and_paste`: Clean format and paste

**Methods:**

- `get_flow(name: str) -> Optional[FlowCommand]`: Get flow by name

- `execute_flow(name: str, context: Dict) -> bool`: Execute flow by name

- `create_flow(name: str, description: str, app_context: str) -> FlowCommand`: Create new flow

- `add_step_to_flow(flow_name: str, step: FlowStep)`: Add step to flow

- `save_flow(flow: FlowCommand)`: Save flow to disk

**Storage:**
- Flows saved as JSON in `~/.stalker/flows/`

---

## Feature Modules

### modules/calculator.py

#### `Calculator`

Math expression evaluator.

**Methods:**

- `try_calculate(expr: str) -> Optional[SearchResult]`: Evaluate expression
  - Supports: +, -, *, /, ^, sqrt, sin, cos, tan, log, ln, pi, e
  - Returns SearchResult with answer if valid

---

### modules/clipboard_manager.py

#### `ClipboardManager(QObject)`

Monitors clipboard and persists entries.

**Constructor:**
```python
ClipboardManager(poll_ms: int = 500)
```

**Methods:**

- `search(q: str, limit: int) -> List[dict]`: Search clipboard history

**Clipboard Types:**
- `text`: Regular text
- `image`: PNG images
- `url`: URLs
- `file`: File paths

---

### modules/snippet_manager.py

#### `SnippetManager`

Manages text snippets with triggers and hotkeys.

**Methods:**

- `expand_snippet(snippet_row: dict)`: Expand snippet via keystroke

- `resolve_trigger(trigger: str) -> Optional[SearchResult]`: Get snippet by trigger

- `search(q: str, limit: int) -> List[SearchResult]`: Search snippets

**Features:**
- Global hotkey support
- IME-safe expansion
- Trigger prefixes: `@` or `;`

---

### modules/file_indexer.py

#### `FileIndexer`

Indexes local files for fast search.

**Constructor:**
```python
FileIndexer(config: ConfigManager)
```

**Methods:**

- `start()`: Start indexing thread
- `pause(state: bool)`: Pause/resume indexing
- `search(q: str, limit: int) -> List[dict]`: Search indexed files

**Features:**
- Background indexing
- Watches for file changes (watchdog)
- Respects performance mode

---

### modules/window_manager.py

#### Functions

- `get_active_window_info() -> Dict[str, str]`: Get info about active window
  - Returns: hwnd, title, class, process, pid

- `detect_app_context() -> Optional[str]`: Detect current app context
  - Returns: app identifier (vscode, browser, explorer, etc.)
  - Uses window title, class, and process name

**Window Management:**
- `snap_left()`, `snap_right()`: Snap window to left/right half
- `snap_top()`, `snap_bottom()`: Snap window to top/bottom half
- `snap_quadrant(position: str)`: Snap to corner quadrant
- `maximize()`: Maximize window
- `center()`: Center window
- `move_next_monitor()`: Move window to next monitor

---

### modules/contextual_actions.py

#### `ContextualActionsManager`

One-tap actions based on active window and clipboard.

**Methods:**

- `update_active_window()`: Update active window info

- `get_clipboard_content() -> str`: Get current clipboard

- `set_clipboard_content(text: str)`: Set clipboard

- `get_available_actions(query: str) -> List[SearchResult]`: Get contextual actions
  - Returns actions based on clipboard content and context

**Action Categories:**

**Paste Actions:**
- `_paste_plain()`: Paste plain text (IME-safe)
- `_paste_and_go()`: Paste and press Enter

**Transform Actions:**
- `_transform_and_paste(text, transform_type)`: Transform and paste
  - Types: uppercase, lowercase, title

**Format Actions:**
- `_clean_and_paste(text)`: Clean formatting and paste
- `_remove_linebreaks_and_paste(text)`: Remove line breaks
- `_quote_and_paste(text)`: Add quotes

**Extraction Actions:**
- `_extract_and_paste(text, extract_type)`: Extract and paste
  - Types: urls, emails, numbers
- `_table_to_csv_and_paste(text)`: Convert table to CSV

**Helper Methods:**
- `_is_url(text) -> bool`: Check if text is URL
- `_extract_urls(text) -> List[str]`: Extract URLs
- `_extract_emails(text) -> List[str]`: Extract emails
- `_extract_numbers(text) -> List[str]`: Extract numbers
- `_looks_like_table(text) -> bool`: Detect table structure

---

### modules/syshealth.py

#### `SysHealth`

System monitoring and process management.

**Methods:**

- `start_background_refresh()`: Start background monitoring thread

- `snapshot() -> SystemSnapshot`: Get current system metrics
  - Returns: CPU%, RAM usage, disk I/O, network I/O

- `get_top_processes(limit: int) -> List[dict]`: Get top processes by resource usage

- `kill_process(pid: int) -> bool`: Terminate process

**System Tools:**
- `open_task_manager()`
- `open_startup_apps()`
- `open_defragmenter()`
- `open_resource_monitor()`
- `open_disk_cleanup()`
- `open_system_info()`

---

### modules/ai_assistant.py

#### `AIAssistant`

Integration with AI services (OpenAI/Azure/Gemini).

**Methods:**

- `ask(prompt: str) -> Tuple[str, bool]`: Send prompt to AI
  - Returns: (response, success)

**Configuration:**
- Provider: openai, azure, gemini
- API key (encrypted storage)
- Model selection
- Temperature, max_tokens

---

### modules/notes.py

#### `NotesManager`

Markdown notes with encryption.

**Methods:**

- `create(title: str, body: str, tags: str) -> int`: Create note

- `search(q: str, limit: int) -> List[Note]`: Search notes

- `get(note_id: int) -> Optional[Note]`: Get note by ID

- `update(note_id: int, title: str, body: str, tags: str)`: Update note

- `delete(note_id: int)`: Delete note

**Features:**
- AES-256 encryption
- Full-text search
- Tag support
- Markdown formatting

---

## UI Components

### ui/launcher.py

#### `LauncherWindow(QWidget)`

Main launcher window.

**Features:**
- Frameless, translucent window
- Always on top
- Debounced search (250ms)
- Adaptive opacity

**Methods:**

- `center_and_show()`: Center on current monitor and show

- `on_text_changed(text: str)`: Handle input changes

- `populate_results(results: List[SearchResult])`: Display search results

**Keyboard Handling:**
- Up/Down: Navigate results
- Enter: Execute selected result
- Ctrl+C: Copy result text
- Escape: Hide launcher

---

### ui/settings_panel.py

#### `SettingsPanel(QWidget)`

Configuration panel UI.

**Sections:**
- General settings
- UI customization
- Module toggles
- Performance mode
- AI configuration
- SysHealth settings

**Methods:**

- `save_settings()`: Persist configuration

- `load_settings()`: Load from config

---

### ui/ai_response_panel.py

#### `AIResponsePanel(QWidget)`

Display AI responses.

**Methods:**

- `show_response(response: str, is_error: bool)`: Show AI response

**Signals:**
- `insert_to_note_signal`: Emit to create note from response

---

### ui/syshealth_overlay.py

#### `SysHealthOverlay(QWidget)`

Persistent system health overlay.

**Features:**
- Always on top
- Configurable position
- Adjustable transparency
- Real-time updates

**Methods:**

- `toggle_visibility()`: Show/hide overlay

- `update_metrics()`: Refresh displayed metrics

---

## Utilities

### modules/keystroke.py

#### Functions

- `send_text_ime_safe(text: str)`: Paste text safely
  - Uses clipboard to avoid IME issues
  - Simulates Ctrl+V

---

### modules/diagnostics.py

#### Functions

- `log(message: str)`: Log message to console and file

---

## Extension Points

### Adding a New Module

1. Create class in `/modules/`
2. Implement search method if applicable
3. Register in `SearchEngine.__init__()`
4. Add command flag in `search()` method
5. Add to `internal_commands` list

### Adding a New Intent Type

1. Add to `IntentType` enum
2. Define patterns in `IntentRouter`
3. Add detection logic in `detect_intent()`
4. Implement suggestions in `_intent_suggestions()`

### Creating Custom Flow Action

1. Add action handler to `FlowCommandExecutor.action_handlers`
2. Implement handler method
3. Document parameters and return values

---

## Performance Considerations

### Optimization Strategies

- **Debouncing**: Search delayed 250ms to reduce unnecessary calls
- **Lazy Loading**: Heavy modules loaded on first use
- **Background Threads**: File indexing, system monitoring
- **Caching**: Frequent results cached
- **Performance Mode**: Disables heavy features

### Resource Usage

**Typical Memory:**
- Base: ~50MB
- With file indexer: +30MB
- With AI: +50MB

**CPU Usage:**
- Idle: <1%
- Active search: 2-5%
- File indexing: 5-10%

---

## Error Handling

### Exception Patterns

Most functions use try-except blocks with logging:

```python
try:
    # operation
except Exception as e:
    log(f"Error: {e}")
    return default_value
```

### Graceful Degradation

- Missing modules don't crash app
- Failed actions logged but don't block UI
- Network errors handled for AI

---

## Testing

### Test Structure

- Unit tests in `/tests/`
- Test coverage for core modules
- Integration tests for search flows

### Running Tests

```bash
pytest tests/
```

---

## API Versioning

**Current Version:** 2.0

**Breaking Changes from 1.x:**
- Intent Router added (backwards compatible)
- Context Profiles added (backwards compatible)
- Flow Commands added (backwards compatible)

---

*API Reference Last Updated: 2025-01-07*
