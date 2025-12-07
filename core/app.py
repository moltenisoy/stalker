from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from ui.launcher import LauncherWindow
from core.hotkey import GlobalHotkey
from core.config import ConfigManager
from services.autostart import ensure_autostart
from typing import Optional

class LauncherApp:
    def __init__(self, qt_app):
        self.qt_app = qt_app
        self.config = ConfigManager()
        self.window = LauncherWindow(config=self.config, app_ref=self)
        
        # Get hotkey from config
        hotkey = self.config.data.get("hotkey", "ctrl+space")
        self.hotkey = GlobalHotkey(self.toggle_visibility, hotkey=hotkey)
        
        # System health overlay (lazy initialization)
        self._syshealth_overlay: Optional[object] = None

    def start(self):
        # Apply theme from config
        theme = self.config.get_ui("theme")
        self._apply_theme(dark=(theme == "dark"))
        ensure_autostart()  # silently ensure autostart at logon
        self.hotkey.register()  # register global hotkey
        self.window.hide()      # start silent/minimized
        
        # Initialize overlay if enabled
        if self.config.get_syshealth_config("overlay_enabled"):
            self._init_syshealth_overlay()

    def toggle_visibility(self):
        if self.window.isVisible() and self.window.isActiveWindow():
            self.window.hide()
        else:
            self.window.center_and_show()
    
    def _init_syshealth_overlay(self):
        """Initialize system health overlay if syshealth module is enabled."""
        if not self.config.get_module_enabled("optimizer"):
            return
        
        # Get syshealth instance from search engine
        if hasattr(self.window, 'search') and hasattr(self.window.search, 'engine'):
            syshealth = self.window.search.engine.syshealth
            if syshealth:
                from ui.syshealth_overlay import SysHealthOverlay
                self._syshealth_overlay = SysHealthOverlay(syshealth, self.config)
                self._syshealth_overlay.show()
    
    def toggle_syshealth_overlay(self):
        """Toggle system health overlay visibility."""
        if not self._syshealth_overlay:
            self._init_syshealth_overlay()
        
        if self._syshealth_overlay:
            self._syshealth_overlay.toggle_visibility()

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