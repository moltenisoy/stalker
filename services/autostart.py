import sys
import os
import winreg

APP_NAME = "FastLauncher"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def ensure_autostart():
    """Registers the app to start on logon silently."""
    exe = sys.executable
    script = os.path.abspath(sys.argv[0])
    if script.lower().endswith(".exe"):
        target = script
    else:
        target = f'"{exe}" "{script}"'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, target)
    except FileNotFoundError:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, target)
    except Exception:
        # Fail silently per “inicio silencioso”
        pass