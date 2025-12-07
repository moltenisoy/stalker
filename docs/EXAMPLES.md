# Stalker - Examples and Use Cases

Practical examples for using Stalker's features.

---

## Basic Usage

### Opening Applications

```
chrome          → Open Google Chrome
vscode          → Open Visual Studio Code
notepad         → Open Notepad
calc            → Open Calculator
```

### Quick Calculations

```
2 + 2           → 4
sqrt(144)       → 12.0
sin(90)         → 0.894
pi * 2          → 6.283
```

### Searching Files

```
/files report.pdf           → Search for report.pdf
/files *.docx              → Search for Word documents
/files budget 2024         → Search for files containing "budget 2024"
```

---

## Clipboard Management

### View History

```
/clipboard                 → Show all clipboard entries
/clipboard meeting notes   → Search for "meeting notes" in history
```

### Restore Old Content

1. Open launcher (Ctrl+Space)
2. Type `/clipboard`
3. Navigate to desired entry
4. Press Enter to copy to clipboard
5. Press Enter again or Ctrl+V to paste

---

## Snippets

### Creating Snippets

1. Open: `/snippets`
2. Click "Create new snippet"
3. Fill in:
   - Name: "Email Signature"
   - Trigger: `@sig`
   - Body: Your signature text
   - Hotkey (optional): `ctrl+shift+s`

### Using Snippets

```
@sig            → Expand email signature
;meeting        → Expand meeting template
@addr           → Expand address
```

---

## Notes

### Creating Notes

```
/notes          → List all notes
/notes New note title    → Create note with title
```

**From Clipboard:**
1. Copy text
2. Open launcher
3. Type `/notes`
4. Select "📋 Insertar selección en nota"

### Searching Notes

```
/notes project          → Find notes containing "project"
/notes tag:work         → Find notes with "work" tag
```

---

## System Health

### Basic Monitoring

```
/syshealth              → Show system overview and top processes
/syshealth chrome       → Filter for Chrome processes
```

### Using System Tools

```
/syshealth task         → Open Task Manager
/syshealth startup      → Open Startup Apps
/syshealth defrag       → Open Disk Defragmenter
```

### Killing Processes

1. Type `/syshealth`
2. Find process in list
3. Select process
4. Press Ctrl+W to kill

### Persistent Overlay

```
/overlay                → Toggle system health overlay
```

---

## AI Assistant

### Basic Queries

```
/ai What is Python?
/ai Explain async/await
> Write a function to sort an array
> Translate "hello" to Spanish
```

### Using Responses

1. Ask question with `/ai` or `>`
2. Response appears in panel
3. Click "Insert to Note" to save
4. Or copy text directly

---

## Intent Router Examples

### Detected Intents

**Open Application:**
```
open chrome             → Detected: OPEN_APP (confidence: 0.9)
launch vscode           → Detected: OPEN_APP
```

**Search File:**
```
find report.pdf         → Detected: SEARCH_FILE
file: image.jpg         → Detected: SEARCH_FILE
```

**Text Transform:**
```
uppercase hello         → Detected: TEXT_TRANSFORM
clean format text       → Detected: TEXT_TRANSFORM
```

**Translate:**
```
translate hello         → Detected: TRANSLATE
traducir hola           → Detected: TRANSLATE
```

---

## Compound Actions

### Zip and Share

**Scenario:** You need to compress files and send the path to someone.

1. Open `/files` and find the file/folder
2. Select it
3. Choose "🗜️ Zip y Compartir"
4. ZIP is created and path copied to clipboard
5. Paste path in email/chat

### Copy Path and Open Folder

**Scenario:** You want to share a file location and open it.

1. Find file with `/files`
2. Select "📋 Copiar Ruta y Abrir Carpeta"
3. Path is copied to clipboard
4. Folder opens in Explorer

### Translate and Paste

**Scenario:** Translate text from clipboard.

1. Copy text to translate
2. Open Stalker
3. Type `/actions`
4. Select "🌐 Traducir y Pegar"
5. Translation is pasted automatically

### Clean and Paste

**Scenario:** Remove formatting from copied text.

1. Copy formatted text (from web, PDF, etc.)
2. Open Stalker
3. Type `/actions`
4. Select "✨ Limpiar y Pegar"
5. Clean text is pasted

---

## Context-Aware Actions

### In Visual Studio Code

**Scenario:** You're coding and need quick access to VSCode features.

1. Make sure VSCode is active window
2. Open Stalker (Ctrl+Space)
3. Type `/context`
4. See VSCode-specific actions:
   - ⚡ search_symbols
   - ⚡ find_file
   - ⚡ terminal
5. Select action to execute

**Using Snippets:**
```
@log            → console.log('', );
@func           → function template
@class          → class template
```

### In Web Browser

**Scenario:** Save current browser tabs for later.

1. Browser is active
2. Open Stalker
3. Type `/context`
4. Select "⚡ save_session"
5. All open tabs are saved

**Restore session:**
1. Open Stalker
2. Type `/context`
3. Select "⚡ restore_session"

**Extract links from page:**
1. Copy page content
2. Open Stalker
3. Type `/context`
4. Select "⚡ extract_links"
5. All URLs are extracted and copied

### In File Explorer

**Scenario:** You need to open a terminal in current folder.

1. Explorer is active
2. Open Stalker
3. Type `/context`
4. Select "⚡ terminal_here"
5. CMD opens in current directory

**Copy current path:**
1. Explorer active
2. Stalker → `/context`
3. Select "⚡ copy_path"
4. Path is in clipboard

---

## Flow Commands Examples

### Example 1: Custom Text Transform

**Goal:** Convert clipboard to uppercase and paste.

Create `~/.stalker/flows/to_upper.json`:

```json
{
  "name": "to_uppercase",
  "description": "Convert to uppercase and paste",
  "app_context": "any",
  "steps": [
    {
      "action": "clipboard",
      "params": {"operation": "get"}
    },
    {
      "action": "transform",
      "params": {"type": "uppercase"}
    },
    {
      "action": "paste",
      "params": {"text": "${transformed_text}"}
    }
  ]
}
```

**Usage:**
1. Copy text
2. Stalker → `/context`
3. Select "⚡ to_uppercase"

### Example 2: Quick Screenshot and Path Copy

**Goal:** Take screenshot, save to specific folder, copy path.

Create `~/.stalker/flows/screenshot.json`:

```json
{
  "name": "quick_screenshot",
  "description": "Screenshot and copy path",
  "app_context": "any",
  "steps": [
    {
      "action": "keystroke",
      "params": {"keys": "win+shift+s"}
    },
    {
      "action": "wait",
      "params": {"duration": 2}
    },
    {
      "action": "clipboard",
      "params": {"operation": "get"}
    },
    {
      "action": "copy",
      "params": {"text": "${clipboard_content}"}
    }
  ]
}
```

### Example 3: Format Code Block

**Goal:** Format clipboard content as code block.

```json
{
  "name": "format_code",
  "description": "Format as code block",
  "app_context": "any",
  "steps": [
    {
      "action": "clipboard",
      "params": {"operation": "get"}
    },
    {
      "action": "paste",
      "params": {"text": "```\n${clipboard_content}\n```"}
    }
  ]
}
```

---

## Contextual Actions Examples

### Extract URLs from Article

**Scenario:** You copied an article and want just the links.

1. Copy article text
2. Stalker → `/actions`
3. Select "🔗 Extraer Enlaces"
4. All URLs are pasted

### Clean Copy from PDF

**Scenario:** PDF text has weird line breaks and formatting.

1. Copy from PDF
2. Stalker → `/actions`
3. Select "✨ Limpiar Formato"
4. Clean text is pasted

### Convert Table to CSV

**Scenario:** You have a table in text format.

**Before:**
```
Name      Age    City
John      30     NYC
Jane      25     LA
```

1. Copy table
2. Stalker → `/actions`
3. Select "📊 Convertir a CSV"

**After:**
```
Name,Age,City
John,30,NYC
Jane,25,LA
```

### Quote Text for Reply

**Scenario:** Quoting text in email/chat.

1. Copy text to quote
2. Stalker → `/actions`
3. Select "💬 Entrecomillar"
4. Text is pasted with quotes

---

## Advanced Workflows

### Workflow 1: Research and Notes

**Goal:** Research topic, save key points.

1. Open browser
2. Search topic
3. Copy interesting passages
4. Stalker → `/notes`
5. "📋 Insertar selección en nota"
6. Repeat for multiple sources
7. Later: `/notes research` to find all

### Workflow 2: Code Documentation

**Goal:** Document code with AI help.

1. Copy code snippet
2. Stalker → `/ai Explain this code`
3. Review AI response
4. Click "Insert to Note"
5. Add to code documentation

### Workflow 3: File Organization

**Goal:** Find and organize project files.

1. Stalker → `/files project`
2. Review results
3. For each file:
   - Select file
   - Choose "📋 Copiar Ruta y Abrir Carpeta"
   - Move to appropriate folder
4. Create note with final structure

### Workflow 4: Multi-language Support

**Goal:** Translate and maintain multilingual content.

1. Write content in English
2. Copy section
3. Stalker → `/actions`
4. Select "🌐 Traducir y Pegar"
5. Paste in Spanish section
6. Repeat for each section

---

## Custom Profile Examples

### Example 1: Notion Profile

Create `~/.stalker/profiles/notion.json`:

```json
{
  "app_name": "notion",
  "display_name": "Notion",
  "window_title_pattern": "Notion",
  "actions": [
    {
      "name": "new_page",
      "description": "Create new page",
      "trigger": "ctrl+n",
      "action_type": "command",
      "action_data": {"command": "new_page"}
    }
  ],
  "snippets": {
    "@todo": "- [ ] ",
    "@heading": "## ",
    "@code": "```\n\n```"
  }
}
```

### Example 2: Slack Profile

```json
{
  "app_name": "slack",
  "display_name": "Slack",
  "window_title_pattern": "Slack",
  "snippets": {
    "@brb": "Be right back!",
    "@meeting": "In a meeting, will respond shortly",
    "@done": "Done! ✅"
  }
}
```

---

## Productivity Tips

### Tip 1: Morning Routine

**Create a flow for morning setup:**

```json
{
  "name": "morning_routine",
  "description": "Open morning apps",
  "app_context": "any",
  "steps": [
    {
      "action": "command",
      "params": {"command": "start chrome"}
    },
    {
      "action": "wait",
      "params": {"duration": 1}
    },
    {
      "action": "command",
      "params": {"command": "start code"}
    },
    {
      "action": "wait",
      "params": {"duration": 1}
    },
    {
      "action": "command",
      "params": {"command": "start slack"}
    }
  ]
}
```

### Tip 2: Quick Email Templates

**Create email snippets:**

```
@meeting → "Hi, let's schedule a meeting to discuss..."
@thanks → "Thank you for your time and assistance..."
@followup → "Following up on our previous conversation..."
```

### Tip 3: Code Review Workflow

1. Copy code block
2. `/ai Review this code for issues`
3. Copy feedback
4. Stalker → `/notes code-review-{date}`
5. Paste feedback
6. Make improvements

---

## Troubleshooting Examples

### Problem: Snippet not expanding

**Solution:**
1. Check trigger: `/snippets`
2. Verify trigger format (starts with @ or ;)
3. Ensure snippets module is enabled (>config)

### Problem: Files not found

**Solution:**
1. Check if file indexer is running
2. Verify drive is indexed (>config)
3. If in performance mode, disable it
4. Wait for indexing to complete

### Problem: Context actions not showing

**Solution:**
1. Check active window detection:
   - Type `/context`
   - Check "Ventana activa" field
2. Create custom profile if needed
3. Ensure window title/class matches pattern

---

## Integration Examples

### With Git Bash

**Flow:** Commit with formatted message

```json
{
  "name": "git_commit",
  "description": "Format commit message",
  "app_context": "terminal",
  "steps": [
    {
      "action": "paste",
      "params": {"text": "git commit -m \""}
    },
    {
      "action": "clipboard",
      "params": {"operation": "get"}
    },
    {
      "action": "paste",
      "params": {"text": "${clipboard_content}"}
    },
    {
      "action": "paste",
      "params": {"text": "\""}
    }
  ]
}
```

### With Postman

**Profile:** Quick request templates

```json
{
  "app_name": "postman",
  "display_name": "Postman",
  "window_title_pattern": "Postman",
  "snippets": {
    "@get": "GET /api/",
    "@post": "POST /api/",
    "@auth": "Bearer ${token}"
  }
}
```

---

*Examples last updated: 2025-01-07*
