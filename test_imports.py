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
    from core import LauncherApp
    from core import ConfigManager
    from core import SearchEngine
    from core import PredictiveSearch
    from core import SearchResult
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing UI modules...")
    from ui import LauncherWindow
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing module components...")
    from modules_system import Calculator
    from modules_files import AppLauncher
    from modules_system import ClipboardManager
    from modules_system import SnippetManager
    from modules_files import FileIndexer
    print("  SUCCESS")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

try:
    print("✓ Importing services...")
    from services import ensure_autostart
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
    from core import Storage
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
