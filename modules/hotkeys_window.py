import keyboard
from modules import window_manager as wm
from modules.grid_preview import GridPreview
from PySide6.QtWidgets import QApplication

class WindowHotkeys:
    """Registro de atajos globales para gestión de ventanas con vista previa."""
    def __init__(self, preview: GridPreview | None = None):
        self.preview = preview
        self._registered = False

    def register(self):
        if self._registered:
            return
        self._registered = True
        keyboard.add_hotkey("windows+shift+left", lambda: self._with_preview(wm.snap_left))
        keyboard.add_hotkey("windows+shift+right", lambda: self._with_preview(wm.snap_right))
        keyboard.add_hotkey("windows+shift+up", lambda: self._with_preview(lambda: wm.snap_quadrant("top")))
        keyboard.add_hotkey("windows+shift+down", lambda: self._with_preview(lambda: wm.snap_quadrant("bottom")))
        keyboard.add_hotkey("windows+shift+enter", lambda: self._with_preview(wm.center))
        keyboard.add_hotkey("windows+shift+m", lambda: self._with_preview(wm.maximize))
        keyboard.add_hotkey("windows+shift+page_up", lambda: self._with_preview(wm.move_next_monitor))

    def _with_preview(self, action):
        if self.preview:
            self.preview.show()
            QApplication.processEvents()
        try:
            action()
        finally:
            if self.preview:
                self.preview.hide()