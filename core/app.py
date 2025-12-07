from PySide6.QtGui import QPalette, QColor, QIcon, QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
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
        
        # System tray icon
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._init_system_tray()

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

    def _init_system_tray(self):
        """Initialize system tray icon with menu."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        # Create tray icon (use built-in icon for now)
        self._tray_icon = QSystemTrayIcon(self.qt_app)
        
        # Try to use application icon or fallback to information icon
        icon = self.qt_app.style().standardIcon(self.qt_app.style().StandardPixmap.SP_ComputerIcon)
        self._tray_icon.setIcon(icon)
        self._tray_icon.setToolTip("Stalker - Fast Launcher")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show Launcher", self.qt_app)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        
        # Settings action
        settings_action = QAction("Settings", self.qt_app)
        settings_action.triggered.connect(self._open_settings_from_tray)
        tray_menu.addAction(settings_action)
        
        # System Health Overlay toggle
        overlay_action = QAction("Toggle System Health Overlay", self.qt_app)
        overlay_action.triggered.connect(self.toggle_syshealth_overlay)
        tray_menu.addAction(overlay_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self.qt_app)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        self._tray_icon.setContextMenu(tray_menu)
        
        # Connect tray icon activation (click)
        self._tray_icon.activated.connect(self._on_tray_activated)
        
        # Show the tray icon
        self._tray_icon.show()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click - toggle window
            self.toggle_visibility()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - show window
            self.window.center_and_show()
    
    def _open_settings_from_tray(self):
        """Open settings panel from tray menu."""
        # Show launcher first
        self.window.center_and_show()
        # Then trigger settings command
        self.window.query_edit.setText(">config")
        self.window.query_edit.returnPressed.emit()
    
    def quit_application(self):
        """Quit the application gracefully."""
        # Unregister hotkey
        if self.hotkey:
            self.hotkey.unregister()
        
        # Hide tray icon
        if self._tray_icon:
            self._tray_icon.hide()
        
        # Close overlay if exists
        if self._syshealth_overlay:
            self._syshealth_overlay.close()
        
        # Quit application
        self.qt_app.quit()
    
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