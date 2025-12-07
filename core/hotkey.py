import threading
import keyboard  # global hotkeys on Windows

DEFAULT_HOTKEY = "ctrl+space"  # avoids Alt+Space conflicts with PowerToys

class GlobalHotkey:
    def __init__(self, callback, hotkey: str = DEFAULT_HOTKEY):
        self.callback = callback
        self.hotkey = hotkey
        self._listener_thread = None
        self._registered = False

    def register(self):
        if self._listener_thread and self._listener_thread.is_alive():
            return
        self._registered = True
        self._listener_thread = threading.Thread(target=self._listen, daemon=True)
        self._listener_thread.start()
    
    def unregister(self):
        """Unregister the global hotkey."""
        if self._registered:
            try:
                keyboard.remove_hotkey(self.hotkey)
                self._registered = False
            except Exception:
                pass  # Ignore errors during unregistration

    def _listen(self):
        keyboard.add_hotkey(self.hotkey, self.callback, suppress=False, trigger_on_release=True)
        keyboard.wait()  # block thread to keep listener alive