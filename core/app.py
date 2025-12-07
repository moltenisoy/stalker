from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from ui.launcher import LauncherWindow
from core.hotkey import GlobalHotkey
from core.config import ConfigManager
from services.autostart import ensure_autostart

class LauncherApp:
    def __init__(self, qt_app):
        self.qt_app = qt_app
        self.config = ConfigManager()
        self.window = LauncherWindow(config=self.config, app_ref=self)
        
        # Get hotkey from config
        hotkey = self.config.data.get("hotkey", "ctrl+space")
        self.hotkey = GlobalHotkey(self.toggle_visibility, hotkey=hotkey)

    def start(self):
        # Apply theme from config
        theme = self.config.get_ui("theme")
        self._apply_theme(dark=(theme == "dark"))
        ensure_autostart()  # silently ensure autostart at logon
        self.hotkey.register()  # register global hotkey
        self.window.hide()      # start silent/minimized

    def toggle_visibility(self):
        if self.window.isVisible() and self.window.isActiveWindow():
            self.window.hide()
        else:
            self.window.center_and_show()

    def _apply_theme(self, dark=True):
        """Apply global application theme from config."""
        palette = QPalette()
        
        # Get accent color from config
        accent_hex = self.config.get_ui("accent")
        accent = QColor(accent_hex)
        
        if dark:
            bg = QColor("#121212")
            fg = QColor("#eaeaea")
            panel = QColor("#1c1c1c")
        else:
            bg = QColor("#f5f7fb")
            fg = QColor("#0f172a")
            panel = QColor("#e2e8f0")

        palette.setColor(QPalette.Window, bg)
        palette.setColor(QPalette.WindowText, fg)
        palette.setColor(QPalette.Base, panel)
        palette.setColor(QPalette.AlternateBase, bg)
        palette.setColor(QPalette.Text, fg)
        palette.setColor(QPalette.Button, panel)
        palette.setColor(QPalette.ButtonText, fg)
        palette.setColor(QPalette.Highlight, accent)
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.qt_app.setPalette(palette)
        self.qt_app.setStyle("Fusion")