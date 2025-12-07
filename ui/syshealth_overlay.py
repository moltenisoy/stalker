"""
Simple overlay panel for system health monitoring.
Shows CPU, RAM, Disk, and Network metrics with periodic updates.
Respects performance mode for update frequency.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from typing import Optional


class SysHealthOverlay(QWidget):
    """Lightweight overlay showing system health metrics."""
    
    def __init__(self, syshealth, config=None):
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus, True)
        
        self.syshealth = syshealth
        self.config = config
        
        # Load configuration
        self._load_config()
        
        # Setup UI
        self._setup_ui()
        
        # Setup update timer
        self._setup_timer()
        
        # Position overlay
        self._position_overlay()
    
    def _load_config(self):
        """Load configuration settings."""
        if self.config:
            self._update_interval = self.config.get_syshealth_config("overlay_update_interval")
            self._position = self.config.get_syshealth_config("overlay_position")
            self._performance_mode = self.config.get_performance_mode()
        else:
            self._update_interval = 5.0
            self._position = "top-right"
            self._performance_mode = False
        
        # Adjust update interval for performance mode
        if self._performance_mode:
            self._update_interval = max(self._update_interval * 2, 10.0)
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Apply theme
        self._apply_theme()
        
        # Create labels
        self.cpu_label = QLabel("CPU: ---%")
        self.ram_label = QLabel("RAM: --- / --- GB")
        self.disk_label = QLabel("Disk: ---R/---W MB/s")
        self.net_label = QLabel("Net: ---↓/---↑ MB/s")
        
        # Set font
        font = QFont("Segoe UI", 9)
        for label in [self.cpu_label, self.ram_label, self.disk_label, self.net_label]:
            label.setFont(font)
            layout.addWidget(label)
        
        self.setFixedSize(220, 110)
    
    def _apply_theme(self):
        """Apply theme based on config."""
        if self.config:
            theme = self.config.get_ui("theme")
            accent = self.config.get_ui("accent")
        else:
            theme = "dark"
            accent = "#3a86ff"
        
        if theme == "dark":
            bg_color = "rgba(15, 23, 42, 200)"
            text_color = "#eaeaea"
            border_color = "#1f2937"
        else:
            bg_color = "rgba(245, 247, 251, 220)"
            text_color = "#0f172a"
            border_color = "#cbd5e1"
        
        stylesheet = f"""
        QWidget {{
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            color: {text_color};
        }}
        QLabel {{
            color: {text_color};
            background: transparent;
        }}
        """
        self.setStyleSheet(stylesheet)
    
    def _setup_timer(self):
        """Setup update timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_metrics)
        self.timer.start(int(self._update_interval * 1000))
        
        # Initial update
        self._update_metrics()
    
    def _update_metrics(self):
        """Update displayed metrics."""
        try:
            snap = self.syshealth.snapshot(use_sampling=True)
            
            # Update labels
            self.cpu_label.setText(f"CPU: {snap.cpu_percent:.0f}%")
            self.ram_label.setText(f"RAM: {snap.ram_used_gb:.1f} / {snap.ram_total_gb:.1f} GB")
            self.disk_label.setText(f"Disk: {snap.disk_read_mb_s:.1f}R/{snap.disk_write_mb_s:.1f}W MB/s")
            self.net_label.setText(f"Net: {snap.net_down_mb_s:.1f}↓/{snap.net_up_mb_s:.1f}↑ MB/s")
        except Exception as e:
            print(f"Error updating overlay metrics: {e}")
    
    def _position_overlay(self):
        """Position overlay based on configuration."""
        screen = self.screen().geometry()
        margin = 10
        
        if self._position == "top-left":
            x = screen.x() + margin
            y = screen.y() + margin
        elif self._position == "top-right":
            x = screen.x() + screen.width() - self.width() - margin
            y = screen.y() + margin
        elif self._position == "bottom-left":
            x = screen.x() + margin
            y = screen.y() + screen.height() - self.height() - margin
        else:  # bottom-right
            x = screen.x() + screen.width() - self.width() - margin
            y = screen.y() + screen.height() - self.height() - margin
        
        self.move(x, y)
    
    def toggle_visibility(self):
        """Toggle overlay visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
    
    def update_config(self, config):
        """Update configuration and refresh settings."""
        self.config = config
        self._load_config()
        self._apply_theme()
        self._position_overlay()
        
        # Restart timer with new interval
        self.timer.stop()
        self.timer.start(int(self._update_interval * 1000))
