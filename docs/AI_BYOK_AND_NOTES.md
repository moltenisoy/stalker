# AI BYOK and Notes Features Documentation

## Overview

This document describes the professional enhancements made to the AI assistant and notes modules, including:

1. **Encrypted API Key Storage** - Secure storage of API keys using Fernet encryption
2. **Enhanced AI Error Handling** - Improved timeouts, retries, and error messages
3. **AI Response Panel** - Dedicated UI for viewing and managing AI responses
4. **Character Preservation in Notes** - Ensures special characters are preserved without HTML escaping
5. **Insert to Note Actions** - Quick actions to save content to notes

## API Key Encryption

### Overview
API keys are now encrypted using Fernet (symmetric encryption) before being stored in the database. The encryption key is stored in `%LOCALAPPDATA%/.fastlauncher/encryption.key` on Windows or `~/.fastlauncher/encryption.key` on Unix-like systems.

### Features
- **Automatic encryption**: API keys are automatically encrypted when stored
- **Transparent decryption**: Keys are decrypted automatically when retrieved
- **Multiple provider support**: Each provider (OpenAI, Anthropic, local) can have its own key
- **Backward compatibility**: Falls back gracefully for unencrypted legacy data
- **Optional**: Can be disabled by setting `encrypt_keys=False` in Storage initialization

### Usage Example
```python
from core.storage import Storage
from modules.ai_assistant import AIAssistant

# Storage with encryption (default)
storage = Storage(encrypt_keys=True)
ai = AIAssistant(storage=storage)

# Store API key (automatically encrypted)
ai.set_api_key("openai", "sk-your-api-key-here")

# Retrieve API key (automatically decrypted)
key = ai._get_api_key("openai")
```

### Security Considerations
- The encryption key file should be kept secure
- On Unix-like systems, permissions are set to 0600 (user read/write only)
- The key file is created once and reused across sessions
- Losing the key file means losing access to encrypted API keys

## Enhanced AI Error Handling

### Features
- **Configurable timeouts**: Default 30 seconds, can be customized
- **Automatic retries**: Default 2 retries with exponential backoff
- **Clear error messages**: User-friendly error messages in Spanish with ❌ icon
- **Specific error handling**: Different messages for different error types:
  - Invalid API key (401)
  - Rate limit exceeded (429)
  - Server errors (500+)
  - Connection errors
  - Timeout errors

### Error Message Examples
```
❌ Error: Falta API key para el proveedor. Configure su clave en ajustes.
❌ Error: API key inválida. Verifique su clave de OpenAI.
❌ Error: Límite de tasa excedido. Espere un momento e intente nuevamente.
❌ Error: Tiempo de espera agotado después de 3 intentos. Verifique su conexión.
❌ Error: No se pudo conectar a OpenAI. Verifique su conexión a Internet.
```

### Configuration
```python
from modules.ai_assistant import AIAssistant

# Custom timeout and retry configuration
ai = AIAssistant(
    timeout=60,      # 60 seconds timeout
    max_retries=3    # 3 retry attempts
)
```

### Response Format
All AI methods now return a tuple: `(response: str, success: bool)`
- `response`: The AI response text or error message
- `success`: `True` if successful, `False` if an error occurred

## AI Response Panel

### Overview
A new dedicated UI panel (`ui/ai_response_panel.py`) displays AI responses with options to copy or insert into notes.

### Features
- **Read-only text area**: Displays AI responses
- **Copy button**: Copy response to clipboard
- **Insert to Note button**: Create a new note with the response
- **Error indication**: Visual distinction between success and error responses
- **Always on top**: Panel stays visible for easy access

### Integration
The panel is automatically created and managed by the SearchEngine:
- Activated when using `/ai <prompt>` or `> <prompt>` commands
- Shows response in dedicated window instead of just logging
- Connected to notes system for easy saving

### Usage
1. Type `/ai <your question>` or `> <your question>` in the launcher
2. Press Enter to execute
3. AI response appears in the dedicated panel
4. Click "Copiar" to copy or "Insertar en Nota" to save

## Character Preservation in Notes

### Overview
Notes now correctly preserve special characters (`<`, `>`, `&`) without HTML escaping. This is critical for:
- Code snippets with comparison operators
- HTML/XML content
- Template syntax (e.g., C++ templates)
- Markdown content

### Implementation
- Uses `QPlainTextEdit` instead of rich text editors
- Stores raw text without entity conversion
- Database stores plain UTF-8 text without transformation

### Examples of Preserved Content
```python
# Before (escaped - incorrect)
"&lt;html&gt;&lt;body&gt;Content&lt;/body&gt;&lt;/html&gt;"

# After (preserved - correct)
"<html><body>Content</body></html>"
```

### Verified Content Types
✓ HTML tags: `<html><body><h1>Title</h1></body></html>`  
✓ Comparison operators: `if (x > 5 && y < 10)`  
✓ Templates: `template<typename T>`  
✓ Ampersands: `Rock & Roll & Blues`  
✓ Code blocks: ` ```cpp\ntemplate<class T>\n``` `

## Insert to Note Actions

### From AI Response
1. Get an AI response in the AI Response Panel
2. Click "Insertar en Nota" button
3. Note is automatically created with:
   - Title: First line or first 50 characters of response
   - Body: Full AI response
   - Tags: "ia" (for filtering)

### From Clipboard/Selection
1. Select and copy text to clipboard
2. Open launcher and type `/notes`
3. Click "📋 Insertar selección en nota"
4. Note is automatically created with:
   - Title: First line or first 50 characters
   - Body: Full clipboard content
   - Tags: "clipboard" (for filtering)

### Programmatic Usage
```python
from core.engine import SearchEngine

engine = SearchEngine()

# Create note from AI response
engine._create_note_from_text("AI response text here")

# Create note from clipboard
engine._insert_clipboard_to_note()
```

## Testing

### Test Files
- `tests/test_encryption.py` - Tests for API key encryption
- `tests/test_notes_preservation.py` - Tests for character preservation
- `tests/test_ai_assistant.py` - Tests for AI error handling

### Running Tests
```bash
# Run all tests
python tests/test_encryption.py
python tests/test_notes_preservation.py
python tests/test_ai_assistant.py

# Or run the config tests
python tests/test_config.py
```

### Test Coverage
- ✓ Encryption with multiple providers
- ✓ Encryption key persistence
- ✓ Backward compatibility with unencrypted data
- ✓ Special character preservation in notes
- ✓ Update operations preserve characters
- ✓ Search with special characters
- ✓ AI error handling for missing keys
- ✓ AI timeout and retry configuration
- ✓ Clear error messages
- ✓ Response format validation

## Migration Notes

### For Existing Users
- **API Keys**: Existing unencrypted keys will still work. New keys are encrypted.
- **Notes**: Existing notes are not affected. Character preservation applies to all notes.
- **No Action Required**: All changes are backward compatible.

### For Developers
- **API Change**: AI methods now return `(str, bool)` instead of just `str`
- **Update calls**: Change `response = ai.ask(...)` to `response, success = ai.ask(...)`
- **Error Handling**: Check the `success` flag to determine if the call succeeded

## Configuration

### Storage Configuration
```python
# With encryption (default)
storage = Storage(encrypt_keys=True)

# Without encryption
storage = Storage(encrypt_keys=False)

# Custom database path
storage = Storage(path=Path("/custom/path/storage.db"))
```

### AI Assistant Configuration
```python
# Default configuration
ai = AIAssistant()

# Custom configuration
ai = AIAssistant(
    storage=custom_storage,
    timeout=60,        # Custom timeout in seconds
    max_retries=3      # Custom retry count
)
```

## Troubleshooting

### Issue: API key not found
**Solution**: Store the API key using `ai.set_api_key(provider, key)`

### Issue: Encryption key file missing
**Solution**: File is automatically created on first use. Check `~/.fastlauncher/encryption.key`

### Issue: Cannot decrypt old keys
**Solution**: If encryption key is lost, you'll need to re-enter API keys

### Issue: Special characters appear escaped in old notes
**Solution**: This affects display only. Re-save the note to fix storage.

### Issue: AI Response Panel doesn't show
**Solution**: Ensure AI module is enabled in config and performance mode is off

## Future Enhancements

Potential improvements for future versions:
- [ ] Async AI requests for better responsiveness
- [ ] Streaming responses for long AI outputs
- [ ] Key backup/export functionality
- [ ] Master password for encryption key
- [ ] Note templates with AI integration
- [ ] Batch AI operations on multiple notes
