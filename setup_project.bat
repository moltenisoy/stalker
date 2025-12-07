@echo off
setlocal
mkdir core
mkdir modules
mkdir ui
type NUL > main.py
type NUL > requirements.txt
type NUL > core\app.py
type NUL > core\search.py
type NUL > core\engine.py
type NUL > core\storage.py
type NUL > core\hotkey.py
type NUL > core\config.py
type NUL > modules\calculator.py
type NUL > modules\clipboard_manager.py
type NUL > modules\keystroke.py
type NUL > modules\snippet_manager.py
type NUL > modules\app_launcher.py
type NUL > modules\file_indexer.py
type NUL > modules\quicklinks.py
type NUL > modules\window_manager.py
type NUL > modules\grid_preview.py
type NUL > modules\macro_recorder.py
type NUL > modules\hotkeys_window.py
type NUL > modules\syshealth.py
type NUL > modules\ai_assistant.py
type NUL > modules\notes.py
type NUL > modules\plugin_shell.py
type NUL > modules\diagnostics.py
type NUL > ui\launcher.py
type NUL > ui\notes_editor.py
type NUL > ui\settings_panel.py
echo Estructura creada.
endlocal