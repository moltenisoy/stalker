# Stalker v2.0 - New Features

## What's New

This release adds powerful local automation features to Stalker, enhancing productivity while maintaining privacy.

---

## 🎯 Intent Router

**Automatic intent detection** - Stalker now understands what you want to do and suggests relevant actions.

### Detected Intents

- **Open applications**: "open chrome", "launch vscode"
- **Search files**: "find document.pdf", "file: report"
- **Paste snippets**: "@email", ";signature"
- **System actions**: "lock", "shutdown", "volume up"
- **Transform text**: "uppercase", "clean format"
- **Translate**: "translate hello", "traducir texto"
- **Calculate**: "2+2", "sqrt(16)"

### Benefits

✅ **100% Local** - No cloud processing
✅ **Privacy First** - Your data never leaves your machine
✅ **Instant** - Detection happens in <5ms
✅ **Smart** - Learns from patterns, not data

---

## 🔗 Compound Actions

**Chain multiple actions** into a single workflow.

### Built-in Actions

1. **🗜️ Zip and Share**
   - Compress file(s)
   - Copy ZIP path to clipboard
   - Ready to send

2. **📋 Copy Path and Open Folder**
   - Copy file path
   - Open containing folder
   - Perfect for navigation

3. **🔄 Convert and Paste**
   - Transform text (uppercase, lowercase, etc.)
   - Paste automatically
   - One command, two actions

4. **🌐 Translate and Paste**
   - Translate clipboard content
   - Paste translation
   - Multilingual workflow

5. **✨ Clean and Paste**
   - Remove formatting
   - Eliminate extra spaces
   - Paste clean text

### Usage

Simply use `/actions` command or select from context menu.

---

## 🎯 Context Profiles

**App-specific automation** - Different actions for different apps.

### Built-in Profiles

#### Visual Studio Code
- ⚡ Search symbols (Ctrl+T)
- ⚡ Find file (Ctrl+P)
- ⚡ Toggle terminal (Ctrl+`)
- 📝 Snippets: @log, @func, @class

#### Web Browser
- ⚡ Save tab session
- ⚡ Restore session
- ⚡ Extract links from page

#### Figma
- ⚡ Export selection

#### File Explorer
- ⚡ Copy full path
- ⚡ Open terminal here

### Custom Profiles

Create your own profiles in JSON:

```json
{
  "app_name": "myapp",
  "display_name": "My App",
  "actions": [...],
  "snippets": {
    "@trigger": "expansion"
  }
}
```

Saved in `~/.stalker/profiles/`

---

## ⚡ Flow Commands

**Declarative automation DSL** - Create workflows without coding.

### Action Types

- `keystroke` - Send keyboard input
- `clipboard` - Read/write clipboard
- `command` - Execute system command
- `wait` - Delay execution
- `paste` - Paste text (IME-safe)
- `copy` - Copy to clipboard
- `open` - Open file/folder
- `save` - Save file (Ctrl+S)
- `transform` - Transform text

### Built-in Flows

1. **copy_current_path** - Get path from Explorer
2. **open_terminal_here** - Open CMD in folder
3. **extract_links** - Extract URLs from text
4. **clean_and_paste** - Clean format and paste

### Custom Flows

Create flows in JSON:

```json
{
  "name": "my_flow",
  "description": "My custom flow",
  "steps": [
    {"action": "clipboard", "params": {"operation": "get"}},
    {"action": "transform", "params": {"type": "uppercase"}},
    {"action": "paste", "params": {"text": "${transformed_text}"}}
  ]
}
```

Saved in `~/.stalker/flows/`

---

## 🚀 Contextual Actions

**One-tap actions** on text and files.

### Paste Actions
- **Paste Plain** - No formatting, IME-safe
- **Paste and Go** - Paste URL + Enter

### Transform Actions
- **UPPERCASE** - Convert and paste
- **lowercase** - Convert and paste
- **Title Case** - Convert and paste

### Format Actions
- **Clean Format** - Remove extra spaces
- **Join Lines** - Remove line breaks
- **Quote Text** - Add quotes

### Extraction Actions
- **Extract URLs** - All links
- **Extract Emails** - Email addresses
- **Extract Numbers** - Numeric values
- **Table to CSV** - Convert tables

### Usage

1. Copy text
2. Open Stalker (Ctrl+Space)
3. Type `/actions`
4. Select action

---

## 🪟 Active Window Detection

**Smart context awareness** - Stalker knows which app you're using.

### Detected Apps

- Visual Studio Code
- Chrome, Firefox, Edge
- File Explorer
- Figma
- Terminal (CMD, PowerShell, Windows Terminal)
- Word, Excel, PowerPoint

### Usage

Type `/context` to see:
- Current app
- Available actions
- App-specific snippets
- Relevant flows

---

## New Commands

| Command | Description |
|---------|-------------|
| `/context` | Show context-aware actions for active app |
| `/actions` | Show quick actions on clipboard content |

---

## Performance

### Benchmarks

- **Intent Detection**: < 5ms
- **Context Detection**: < 10ms
- **Action Execution**: < 50ms
- **Memory Overhead**: ~10MB

### Resource Usage

- **CPU (Idle)**: < 1%
- **CPU (Active)**: 2-5%
- **Privacy**: 100% local processing

---

## Documentation

Comprehensive documentation available:

1. **COMPREHENSIVE_DOCUMENTATION.md** - Complete user guide
2. **API_REFERENCE.md** - Developer reference
3. **EXAMPLES.md** - Practical examples
4. **IMPLEMENTATION_INTENT_ROUTER_AND_CONTEXT.md** - Technical details

---

## Use Cases

### Developer Workflow
- VSCode: Quick symbol search, terminal access
- Code snippets with @triggers
- Extract links from docs
- Clean copied code formatting

### Content Creation
- Clean web text formatting
- Extract URLs from articles
- Quote text for replies
- Convert tables to CSV

### File Management
- Zip and share files
- Copy paths quickly
- Open terminal in folder
- Navigate efficiently

### Multilingual Work
- Translate and paste
- Context-aware snippets
- Language-specific profiles

---

## Privacy & Security

✅ **Local Processing** - All intent detection runs on your device
✅ **No Telemetry** - We don't track or collect data
✅ **Offline Capable** - Works without internet
✅ **Open Architecture** - Inspect profiles and flows
✅ **Security Scanned** - CodeQL verification passed

---

## Extensibility

### Easy Customization

- **JSON Profiles** - No coding required
- **Flow DSL** - Declarative automation
- **Shared Patterns** - Reusable utilities
- **Open Source** - Modify as needed

### Community

Share your:
- Custom profiles
- Flow commands
- Automation recipes
- Use cases

---

## Backwards Compatibility

✅ All existing features still work
✅ No breaking changes
✅ Optional new features
✅ Smooth upgrade

---

## Getting Started

### Try It Now

1. Press **Ctrl+Space** (or your hotkey)
2. Type `/context` to see context actions
3. Type `/actions` to see clipboard actions
4. Try compound actions on files

### Create Custom Profile

1. Find app with `/context`
2. Create JSON in `~/.stalker/profiles/myapp.json`
3. Add actions and snippets
4. Restart Stalker

### Create Custom Flow

1. Plan your workflow steps
2. Create JSON in `~/.stalker/flows/myflow.json`
3. Use action types from docs
4. Test with `/context`

---

## What's Next

### Planned Features

- Machine learning for intent detection
- More built-in profiles
- Flow debugger
- Shared flows repository
- Advanced variables
- Conditional flows

---

## Feedback

Found a bug? Have a suggestion?
- Open an issue on GitHub
- Check documentation
- Share your profiles and flows

---

**Stalker v2.0** - Smarter automation, complete privacy.

*Released: 2025-01-07*
