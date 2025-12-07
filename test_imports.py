"""
Simple test script to verify all imports work correctly.
This helps identify import errors before building the executable.
"""

import sys
print("Python version:", sys.version)
print("\nTesting imports...\n")

try:
    print("✓ Importing main...")
    import main
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing core modules...")
    from core.app import LauncherApp
    from core.config import ConfigManager
    from core.engine import SearchEngine
    from core.search import PredictiveSearch
    from core.types import SearchResult
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing UI modules...")
    from ui.launcher import LauncherWindow
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing module components...")
    from modules.calculator import Calculator
    from modules.app_launcher import AppLauncher
    from modules.clipboard_manager import ClipboardManager
    from modules.snippet_manager import SnippetManager
    from modules.file_indexer import FileIndexer
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing services...")
    from services.autostart import ensure_autostart
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Testing ConfigManager...")
    config = ConfigManager()
    print(f"  Config loaded successfully")
    print(f"  Hotkey: {config.data.get('hotkey', 'N/A')}")
    print(f"  Theme: {config.get_ui('theme')}")
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Testing Storage...")
    from core.storage import Storage
    storage = Storage()
    print("  Storage initialized successfully")
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ All imports and basic tests passed!")
print("="*50)
print("\nThe application should be ready to run.")
print("To start the application: python main.py")
