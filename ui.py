"""
Panel de respuesta de IA con soporte para copiar y insertar en notas.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QGuiApplication


class AIResponsePanel(QWidget):
    """
    Panel para mostrar respuestas de IA con opciones para copiar e insertar en notas.
    """
    insert_to_note_signal = Signal(str)  # Signal to insert text into a note
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Respuesta de IA")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Don't delete when closed
        
        # Setup UI
        self._setup_ui()
        self.resize(600, 400)
    
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title label
        self.title_label = QLabel("Respuesta de IA", self)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Response text area (read-only)
        self.response_text = QTextEdit(self)
        self.response_text.setReadOnly(True)
        self.response_text.setPlaceholderText("La respuesta de IA aparecerá aquí...")
        layout.addWidget(self.response_text, 1)  # Stretch factor 1
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Copy button
        self.copy_btn = QPushButton("📋 Copiar", self)
        self.copy_btn.setToolTip("Copiar respuesta al portapapeles")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)
        
        # Insert to note button
        self.insert_note_btn = QPushButton("📝 Insertar en Nota", self)
        self.insert_note_btn.setToolTip("Crear o insertar en una nota")
        self.insert_note_btn.clicked.connect(self._insert_to_note)
        button_layout.addWidget(self.insert_note_btn)
        
        # Close button
        self.close_btn = QPushButton("Cerrar", self)
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def show_response(self, response: str, is_error: bool = False):
        """
        Display AI response in the panel.
        
        Args:
            response: The response text to display
            is_error: Whether this is an error message
        """
        self.response_text.setPlainText(response)
        
        # Change styling based on error status
        if is_error:
            self.response_text.setStyleSheet("QTextEdit { color: #ff6b6b; }")
            self.title_label.setText("⚠️ Error de IA")
        else:
            self.response_text.setStyleSheet("QTextEdit { color: inherit; }")
            self.title_label.setText("✅ Respuesta de IA")
        
        # Show and raise the panel
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _copy_to_clipboard(self):
        """Copy response to clipboard."""
        text = self.response_text.toPlainText()
        if text:
            QGuiApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copiado", "Respuesta copiada al portapapeles.")
    
    def _insert_to_note(self):
        """Signal to insert the response into a note."""
        text = self.response_text.toPlainText()
        if text:
            self.insert_to_note_signal.emit(text)
            QMessageBox.information(
                self, 
                "Insertar en Nota", 
                "El texto se insertará en una nueva nota."
            )




"""
Editor minimal de notas en texto plano/Markdown.
CRÍTICO: Se desactiva el rich-text para evitar conversión de <, >, & a entidades HTML.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPlainTextEdit, QPushButton
from PySide6.QtCore import Qt
try:
    from modules_ai import NotesManager
except Exception:
    NotesManager = None

class NotesEditor(QWidget):
    def __init__(self, notes=None):
        super().__init__()
        if notes is not None:
            self.notes = notes
        else:
            if NotesManager is None:
                from modules_ai import NotesManager as _NotesManager
                self.notes = _NotesManager()
            else:
                self.notes = NotesManager()
        self.setWindowTitle("Notas")
        layout = QVBoxLayout(self)
        self.title = QLineEdit(self)
        self.body = QPlainTextEdit(self)  # plain text => no HTML escaping
        self.body.setPlaceholderText("Markdown aquí; los caracteres <, >, & se mantienen crudos.")
        self.save_btn = QPushButton("Guardar", self)
        layout.addWidget(self.title)
        layout.addWidget(self.body, 1)
        layout.addWidget(self.save_btn)
        self.save_btn.clicked.connect(self.save_note)

    def save_note(self):
        title = self.title.text().strip() or "Sin título"
        body = self.body.toPlainText()
        self.notes.create(title=title, body=body, tags="")
        self.close()



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




from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox,
    QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core.config import ConfigManager
from pathlib import Path
import traceback


class SettingsPanel(QWidget):
    """
    Comprehensive settings panel for Stalker/FastLauncher.
    Allows configuration of:
    - Global hotkey
    - UI appearance (theme, opacity, font)
    - Module toggles
    - Performance mode
    - Config import/export
    - Service restart
    """
    
    # Signal emitted when settings require a restart
    settings_changed = Signal()
    
    def __init__(self, config: ConfigManager | None = None, app_ref=None):
        super().__init__()
        self.config = config or ConfigManager()
        self.app_ref = app_ref  # Reference to LauncherApp for service restart
        
        self.setWindowTitle("Configuración - Stalker")
        self.setMinimumSize(600, 700)
        self.setWindowFlags(Qt.Window)
        
        # Create scrollable area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        
        # Add sections
        main_layout.addWidget(self._create_hotkey_section())
        main_layout.addWidget(self._create_appearance_section())
        main_layout.addWidget(self._create_modules_section())
        main_layout.addWidget(self._create_performance_section())
        main_layout.addWidget(self._create_config_section())
        main_layout.addWidget(self._create_services_section())
        
        main_layout.addStretch()
        
        scroll.setWidget(container)
        
        # Main window layout
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(scroll)
        
        # Apply current theme
        self._apply_theme()
    
    def _create_hotkey_section(self):
        """Create hotkey configuration section."""
        group = QGroupBox("Tecla de Acceso Global")
        layout = QVBoxLayout()
        
        info = QLabel("Define el atajo de teclado global para abrir el launcher.")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("Hotkey:"))
        
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setText(self.config.data.get("hotkey", "ctrl+space"))
        self.hotkey_input.setPlaceholderText("Ej: ctrl+space, alt+f1")
        hotkey_layout.addWidget(self.hotkey_input)
        
        apply_hotkey_btn = QPushButton("Aplicar")
        apply_hotkey_btn.clicked.connect(self._on_hotkey_change)
        hotkey_layout.addWidget(apply_hotkey_btn)
        
        layout.addLayout(hotkey_layout)
        
        note = QLabel("⚠ Los cambios requieren reiniciar servicios para tomar efecto.")
        note.setStyleSheet("color: #f59e0b; font-size: 10px;")
        layout.addWidget(note)
        
        group.setLayout(layout)
        return group
    
    def _create_appearance_section(self):
        """Create appearance configuration section."""
        group = QGroupBox("Apariencia")
        layout = QVBoxLayout()
        
        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        current_theme = self.config.get_ui("theme")
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self._on_theme_change)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Font
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Fuente:"))
        self.font_family_input = QLineEdit()
        self.font_family_input.setText(self.config.get_ui("font_family"))
        self.font_family_input.setPlaceholderText("Ej: Segoe UI, Arial")
        font_layout.addWidget(self.font_family_input)
        
        font_layout.addWidget(QLabel("Tamaño:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.config.get_ui("font_size"))
        font_layout.addWidget(self.font_size_spin)
        
        apply_font_btn = QPushButton("Aplicar")
        apply_font_btn.clicked.connect(self._on_font_change)
        font_layout.addWidget(apply_font_btn)
        layout.addLayout(font_layout)
        
        # Opacity
        opacity_active_layout = QHBoxLayout()
        opacity_active_layout.addWidget(QLabel("Opacidad (activo):"))
        self.opacity_active_spin = QDoubleSpinBox()
        self.opacity_active_spin.setRange(0.1, 1.0)
        self.opacity_active_spin.setSingleStep(0.05)
        self.opacity_active_spin.setValue(self.config.get_ui("opacity_active"))
        opacity_active_layout.addWidget(self.opacity_active_spin)
        opacity_active_layout.addStretch()
        layout.addLayout(opacity_active_layout)
        
        opacity_inactive_layout = QHBoxLayout()
        opacity_inactive_layout.addWidget(QLabel("Opacidad (inactivo):"))
        self.opacity_inactive_spin = QDoubleSpinBox()
        self.opacity_inactive_spin.setRange(0.1, 1.0)
        self.opacity_inactive_spin.setSingleStep(0.05)
        self.opacity_inactive_spin.setValue(self.config.get_ui("opacity_inactive"))
        opacity_inactive_layout.addWidget(self.opacity_inactive_spin)
        opacity_inactive_layout.addStretch()
        layout.addLayout(opacity_inactive_layout)
        
        apply_opacity_btn = QPushButton("Aplicar Opacidad")
        apply_opacity_btn.clicked.connect(self._on_opacity_change)
        layout.addWidget(apply_opacity_btn)
        
        # Accent color
        accent_layout = QHBoxLayout()
        accent_layout.addWidget(QLabel("Color Acento:"))
        self.accent_input = QLineEdit()
        self.accent_input.setText(self.config.get_ui("accent"))
        self.accent_input.setPlaceholderText("Ej: #3a86ff")
        accent_layout.addWidget(self.accent_input)
        
        apply_accent_btn = QPushButton("Aplicar")
        apply_accent_btn.clicked.connect(self._on_accent_change)
        accent_layout.addWidget(apply_accent_btn)
        layout.addLayout(accent_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_modules_section(self):
        """Create modules enable/disable section."""
        group = QGroupBox("Módulos")
        layout = QVBoxLayout()
        
        info = QLabel("Activa o desactiva módulos específicos:")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Create checkboxes for each module
        self.module_checkboxes = {}
        modules = [
            ("optimizer", "Optimizer - Monitor de sistema y procesos"),
            ("clipboard", "Clipboard - Historial de portapapeles"),
            ("snippets", "Snippets - Plantillas de texto"),
            ("ai", "AI Assistant - Asistente de inteligencia artificial"),
            ("files", "Files - Índice de archivos"),
            ("links", "Links - Accesos directos personalizados"),
            ("macros", "Macros - Grabador de macros"),
        ]
        
        for module_key, module_label in modules:
            checkbox = QCheckBox(module_label)
            checkbox.setChecked(self.config.get_module_enabled(module_key))
            checkbox.stateChanged.connect(
                lambda state, key=module_key: self._on_module_toggle(key, state)
            )
            self.module_checkboxes[module_key] = checkbox
            layout.addWidget(checkbox)
        
        group.setLayout(layout)
        return group
    
    def _create_performance_section(self):
        """Create performance mode section."""
        group = QGroupBox("Rendimiento")
        layout = QVBoxLayout()
        
        info = QLabel(
            "El Modo Ahorro reduce el uso de recursos desactivando efectos visuales "
            "y pausando servicios de indexación en segundo plano."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        self.performance_checkbox = QCheckBox("Activar Modo Ahorro de Rendimiento")
        self.performance_checkbox.setChecked(self.config.get_performance_mode())
        self.performance_checkbox.stateChanged.connect(self._on_performance_toggle)
        layout.addWidget(self.performance_checkbox)
        
        group.setLayout(layout)
        return group
    
    def _create_config_section(self):
        """Create config import/export section."""
        group = QGroupBox("Configuración")
        layout = QVBoxLayout()
        
        info = QLabel("Exporta o importa tu configuración completa:")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Exportar Configuración")
        export_btn.clicked.connect(self._on_export)
        buttons_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Importar Configuración")
        import_btn.clicked.connect(self._on_import)
        buttons_layout.addWidget(import_btn)
        
        layout.addLayout(buttons_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_services_section(self):
        """Create services restart section."""
        group = QGroupBox("Servicios")
        layout = QVBoxLayout()
        
        info = QLabel(
            "Reinicia los servicios de indexación, monitoreo y IA para aplicar cambios "
            "o resolver problemas."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        restart_btn = QPushButton("Reiniciar Servicios")
        restart_btn.clicked.connect(self._on_restart_services)
        layout.addWidget(restart_btn)
        
        group.setLayout(layout)
        return group
    
    def _apply_theme(self):
        """Apply theme to settings panel."""
        theme = self.config.get_ui("theme")
        accent = self.config.get_ui("accent")
        
        if theme == "dark":
            bg_color = "#1c1c1c"
            text_color = "#eaeaea"
            group_bg = "#252525"
            border_color = "#3a3a3a"
        else:
            bg_color = "#f5f7fb"
            text_color = "#0f172a"
            group_bg = "#ffffff"
            border_color = "#cbd5e1"
        
        stylesheet = f"""
        QWidget {{
            background-color: {bg_color};
            color: {text_color};
        }}
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {border_color};
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: {group_bg};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }}
        QPushButton {{
            background-color: {accent};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {accent}dd;
        }}
        QPushButton:pressed {{
            background-color: {accent}bb;
        }}
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            padding: 6px;
            border: 1px solid {border_color};
            border-radius: 4px;
            background-color: {group_bg};
        }}
        QCheckBox {{
            spacing: 8px;
        }}
        """
        self.setStyleSheet(stylesheet)
    
    def _show_message(self, title: str, message: str, icon=QMessageBox.Information):
        """Show a message dialog."""
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    def _show_error(self, title: str, error: Exception):
        """Show error message with traceback logged."""
        error_msg = f"{str(error)}\n\n{traceback.format_exc()}"
        print(f"Error: {error_msg}")  # Log full traceback
        # Only show user-friendly error message, not full traceback
        self._show_message(title, str(error), QMessageBox.Critical)
    
    # Event Handlers
    
    def _on_hotkey_change(self):
        """Handle hotkey change."""
        try:
            new_hotkey = self.hotkey_input.text().strip()
            if not new_hotkey:
                self._show_message("Error", "El hotkey no puede estar vacío.", QMessageBox.Warning)
                return
            
            validated = self.config.set_hotkey(new_hotkey)
            self.hotkey_input.setText(validated)
            self._show_message("Éxito", f"Hotkey actualizado a: {validated}\n\nReinicia servicios para aplicar.")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al cambiar hotkey", ex)
    
    def _on_theme_change(self, theme: str):
        """Handle theme change."""
        try:
            self.config.set_ui(theme=theme)
            self._apply_theme()
            self._show_message("Éxito", f"Tema cambiado a: {theme}\n\nCierra y reabre la ventana para ver todos los cambios.")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al cambiar tema", ex)
    
    def _on_font_change(self):
        """Handle font change."""
        try:
            font_family = self.font_family_input.text().strip()
            font_size = self.font_size_spin.value()
            
            if not font_family:
                self._show_message("Error", "El nombre de fuente no puede estar vacío.", QMessageBox.Warning)
                return
            
            self.config.set_ui(font_family=font_family, font_size=font_size)
            self._show_message("Éxito", f"Fuente actualizada: {font_family} {font_size}pt")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al cambiar fuente", ex)
    
    def _on_opacity_change(self):
        """Handle opacity change."""
        try:
            opacity_active = self.opacity_active_spin.value()
            opacity_inactive = self.opacity_inactive_spin.value()
            
            self.config.set_ui(opacity_active=opacity_active, opacity_inactive=opacity_inactive)
            self._show_message("Éxito", "Opacidad actualizada.")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al cambiar opacidad", ex)
    
    def _on_accent_change(self):
        """Handle accent color change."""
        try:
            from PySide6.QtGui import QColor
            import re
            
            accent = self.accent_input.text().strip()
            
            # Validate hex color format
            hex_pattern = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')
            if not hex_pattern.match(accent):
                self._show_message(
                    "Error",
                    "El color debe ser un código hex válido (ej: #3a86ff o #f00)",
                    QMessageBox.Warning
                )
                return
            
            # Additional validation using QColor
            color = QColor(accent)
            if not color.isValid():
                self._show_message(
                    "Error",
                    "El color especificado no es válido",
                    QMessageBox.Warning
                )
                return
            
            self.config.set_ui(accent=accent)
            self._apply_theme()
            self._show_message("Éxito", f"Color acento actualizado: {accent}")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al cambiar color acento", ex)
    
    def _on_module_toggle(self, module: str, state: int):
        """Handle module enable/disable toggle."""
        try:
            enabled = bool(state)
            self.config.set_module_enabled(module, enabled)
            status = "activado" if enabled else "desactivado"
            print(f"Módulo {module} {status}")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error(f"Error al cambiar módulo {module}", ex)
    
    def _on_performance_toggle(self, state: int):
        """Handle performance mode toggle."""
        try:
            enabled = bool(state)
            self.config.toggle_performance_mode(enabled)
            status = "activado" if enabled else "desactivado"
            self._show_message("Éxito", f"Modo Ahorro {status}.\n\nReinicia servicios para aplicar todos los cambios.")
            self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al cambiar modo rendimiento", ex)
    
    def _on_export(self):
        """Handle config export."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Configuración",
                str(Path.home() / "stalker_config.json"),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if not file_path:
                return
            
            result = self.config.export(Path(file_path))
            if result:
                self._show_message("Éxito", f"Configuración exportada a:\n{file_path}")
            else:
                self._show_message("Error", "No se pudo exportar la configuración.", QMessageBox.Critical)
        except Exception as ex:
            self._show_error("Error al exportar configuración", ex)
    
    def _on_import(self):
        """Handle config import."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Importar Configuración",
                str(Path.home()),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Confirm import
            reply = QMessageBox.question(
                self,
                "Confirmar Importación",
                "¿Estás seguro de que quieres importar esta configuración?\n"
                "Esto sobrescribirá tu configuración actual.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.config.import_file(Path(file_path))
                self._refresh_ui()
                self._show_message("Éxito", f"Configuración importada desde:\n{file_path}\n\nReinicia servicios para aplicar.")
                self.settings_changed.emit()
        except Exception as ex:
            self._show_error("Error al importar configuración", ex)
    
    def _on_restart_services(self):
        """Handle restart services button."""
        try:
            # Reload config first
            self.config.load()
            
            message_parts = ["Servicios reiniciados:\n"]
            
            # Check if we have app reference for full restart
            if self.app_ref and hasattr(self.app_ref, 'window') and hasattr(self.app_ref.window, 'search'):
                engine = self.app_ref.window.search.engine
                
                # Restart file indexer
                if engine.file_indexer:
                    perf = self.config.get_performance_mode()
                    if perf:
                        engine.file_indexer.pause(True)
                        message_parts.append("✓ File Indexer (pausado por modo ahorro)")
                    else:
                        engine.file_indexer.pause(False)
                        engine.file_indexer.start()
                        message_parts.append("✓ File Indexer (reiniciado)")
                else:
                    message_parts.append("○ File Indexer (desactivado)")
                
                # Check AI assistant
                if engine.ai:
                    message_parts.append("✓ AI Assistant (disponible)")
                else:
                    message_parts.append("○ AI Assistant (desactivado)")
                
                # Check other services
                services = [
                    ("clipboard", "Clipboard Manager"),
                    ("snippets", "Snippet Manager"),
                    ("links", "Quicklinks"),
                    ("macros", "Macro Recorder"),
                    ("optimizer", "System Health Monitor"),
                ]
                
                for service_key, service_name in services:
                    enabled = self.config.get_module_enabled(service_key)
                    status = "disponible" if enabled else "desactivado"
                    symbol = "✓" if enabled else "○"
                    message_parts.append(f"{symbol} {service_name} ({status})")
                
                # Apply theme changes
                if self.app_ref and hasattr(self.app_ref, '_apply_theme'):
                    theme = self.config.get_ui("theme")
                    self.app_ref._apply_theme(dark=(theme == "dark"))
                    message_parts.append("\n✓ Tema aplicado")
                else:
                    message_parts.append("\n⚠ Tema: Requiere reinicio de la aplicación")
                
                # Re-register hotkey if changed
                if self.app_ref and hasattr(self.app_ref, 'hotkey'):
                    message_parts.append("\n⚠ Hotkey: Requiere reinicio completo de la aplicación")
            else:
                message_parts.append("⚠ Referencia a app no disponible")
                message_parts.append("Reinicia la aplicación manualmente para aplicar todos los cambios.")
            
            self._show_message("Servicios", "\n".join(message_parts))
            
        except Exception as ex:
            self._show_error("Error al reiniciar servicios", ex)
    
    def _refresh_ui(self):
        """Refresh UI controls with current config values."""
        try:
            # Hotkey
            self.hotkey_input.setText(self.config.data.get("hotkey", "ctrl+space"))
            
            # Theme
            self.theme_combo.setCurrentText(self.config.get_ui("theme"))
            
            # Font
            self.font_family_input.setText(self.config.get_ui("font_family"))
            self.font_size_spin.setValue(self.config.get_ui("font_size"))
            
            # Opacity
            self.opacity_active_spin.setValue(self.config.get_ui("opacity_active"))
            self.opacity_inactive_spin.setValue(self.config.get_ui("opacity_inactive"))
            
            # Accent
            self.accent_input.setText(self.config.get_ui("accent"))
            
            # Modules
            for module_key, checkbox in self.module_checkboxes.items():
                checkbox.setChecked(self.config.get_module_enabled(module_key))
            
            # Performance
            self.performance_checkbox.setChecked(self.config.get_performance_mode())
            
            # Reapply theme
            self._apply_theme()
            
        except Exception as ex:
            print(f"Error refreshing UI: {ex}")



from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont, QCursor, QGuiApplication
from core import PredictiveSearch, SearchResult, ConfigManager
from modules_system import send_text_ime_safe


class GridPreview:
    def __init__(self, cols: int = 2, rows: int = 2):
        self.cols = cols
        self.rows = rows

    def show(self):
        return None

    def hide(self):
        return None


class WindowHotkeys:
    def __init__(self, preview: GridPreview | None = None):
        self.preview = preview

    def register(self):
        return None

    def unregister(self):
        return None

class LauncherWindow(QWidget):
    def __init__(self, config: ConfigManager = None, app_ref=None):
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus, False)
        self.setWindowModality(Qt.NonModal)
        self.setFocusPolicy(Qt.StrongFocus)

        # Load configuration
        self.config = config or ConfigManager()
        self.app_ref = app_ref
        
        # Apply theme from config
        self._apply_theme()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Apps, /files, /links, /clipboard, /snippets, /macros, /syshealth…")
        
        # Apply font from config
        font_family = self.config.get_ui("font_family")
        font_size = self.config.get_ui("font_size")
        self.input.setFont(QFont(font_family, font_size))
        self.input.textChanged.connect(self.on_text_changed)
        self.input.installEventFilter(self)

        self.list = QListWidget(self)
        self.list.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(self.input)
        layout.addWidget(self.list)

        self.search = PredictiveSearch(debounce_ms=250, config=self.config)
        self.search.results_ready.connect(self.populate_results)
        # Pass app reference to search engine
        if self.app_ref:
            self.search.engine._app_ref = self.app_ref

        self.resize(580, 380)
        
        # Apply opacity from config
        self._inactive_opacity = self.config.get_ui("opacity_inactive")
        self._active_opacity = self.config.get_ui("opacity_active")
        self._set_inactive()

        # Visual grid preview + window hotkeys (disabled if effects are off in performance mode)
        effects_enabled = self.config.get_ui("effects") and not self.config.get_performance_mode()
        if effects_enabled:
            self.grid_preview = GridPreview(cols=2, rows=2)
            self.win_hotkeys = WindowHotkeys(preview=self.grid_preview)
            self.win_hotkeys.register()
        else:
            self.grid_preview = None
            self.win_hotkeys = None

    def _apply_theme(self):
        """Apply theme colors and styles from config."""
        ui_config = self.config.get_ui()
        theme = ui_config.get("theme", "dark")
        accent = ui_config.get("accent", "#3a86ff")
        effects = ui_config.get("effects", True)
        performance_mode = self.config.get_performance_mode()
        
        # Adjust effects based on performance mode
        border_radius = "12px" if effects and not performance_mode else "8px"
        
        if theme == "dark":
            bg_color = "rgba(15, 23, 42, 215)"
            input_bg = "rgba(26, 32, 44, 230)"
            list_bg = "rgba(17, 24, 39, 230)"
            text_color = "#eaeaea"
            border_color = "#1f2937"
        else:  # light theme
            bg_color = "rgba(245, 247, 251, 235)"
            input_bg = "rgba(255, 255, 255, 240)"
            list_bg = "rgba(242, 244, 247, 240)"
            text_color = "#0f172a"
            border_color = "#cbd5e1"
        
        stylesheet = f"""
        QWidget {{ 
            background-color: {bg_color}; 
            border-radius: {border_radius}; 
            color: {text_color}; 
        }}
        QLineEdit {{ 
            padding: 10px 12px; 
            border: 1px solid {accent}; 
            border-radius: 8px; 
            background: {input_bg}; 
            color: {text_color}; 
            selection-background-color: {accent}; 
        }}
        QListWidget {{ 
            border: 1px solid {border_color}; 
            border-radius: 8px; 
            background: {list_bg}; 
            outline: none; 
        }}
        QListWidget::item {{ 
            padding: 8px 10px; 
        }}
        QListWidget::item:selected {{ 
            background: {accent}; 
            color: white; 
        }}
        """
        
        self.setStyleSheet(stylesheet)

    def center_and_show(self):
        screen = QCursor.pos()
        desktop = self.screen().geometry()
        self.move(
            desktop.x() + (desktop.width() - self.width()) // 2,
            desktop.y() + (desktop.height() - self.height()) // 3,
        )
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()
        self._set_active()

    def hideEvent(self, event):
        self._set_inactive()
        super().hideEvent(event)

    def focusOutEvent(self, event):
        self.hide()
        super().focusOutEvent(event)

    def on_text_changed(self, text: str):
        self.search.query(text)

    def populate_results(self, results):
        self.list.clear()
        for res in results:
            title = res.title
            if res.subtitle:
                title = f"{res.title} — {res.subtitle}"
            item = QListWidgetItem(title, self.list)
            item.setData(Qt.UserRole, res)
        if results:
            self.list.setCurrentRow(0)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key_Escape,):
            self.hide(); return
        if key in (Qt.Key_Down,):
            row = self.list.currentRow()
            if row < self.list.count() - 1:
                self.list.setCurrentRow(row + 1); return
        if key in (Qt.Key_Up,):
            row = self.list.currentRow()
            if row > 0:
                self.list.setCurrentRow(row - 1); return
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._activate_current(); return
        if key == Qt.Key_C and modifiers & Qt.ControlModifier:
            self._copy_current(); return
        if key == Qt.Key_O and modifiers & Qt.ControlModifier:
            self._open_folder_current(); return
        if key == Qt.Key_V and modifiers & Qt.ControlModifier and modifiers & Qt.ShiftModifier:
            self._paste_plain_current(); return
        if key == Qt.Key_W and modifiers & Qt.ControlModifier:
            self._kill_current_if_process(); return
        super().keyPressEvent(event)

    def _activate_current(self):
        current = self.list.currentItem()
        if not current:
            return
        res: SearchResult = current.data(Qt.UserRole)
        if res.action:
            try:
                res.action()
            except Exception as ex:
                print(f"Error al ejecutar acción: {ex}")
        if res.copy_text:
            self._copy_text(res.copy_text)
        self.hide()

    def _copy_current(self):
        current = self.list.currentItem()
        if not current:
            return
        res: SearchResult = current.data(Qt.UserRole)
        if res and res.copy_text:
            self._copy_text(res.copy_text)

    def _open_folder_current(self):
        """Open containing folder for the current item (Ctrl+O)."""
        current = self.list.currentItem()
        if not current:
            return
        res: SearchResult = current.data(Qt.UserRole)
        # Check if this is a file result with the open folder action
        if res and res.meta and "open_folder_action" in res.meta:
            try:
                res.meta["open_folder_action"]()
                self.hide()
            except Exception as ex:
                print(f"Error opening folder: {ex}")

    def _paste_plain_current(self):
        current = self.list.currentItem()
        if not current:
            return
        res: SearchResult = current.data(Qt.UserRole)
        if res and res.copy_text:
            send_text_ime_safe(res.copy_text)
            self.hide()

    def _kill_current_if_process(self):
        """Kill current process with optional confirmation (Ctrl+W)."""
        current = self.list.currentItem()
        if not current:
            return
        
        res: SearchResult = current.data(Qt.UserRole)
        if not res or res.group != "process" or not res.meta or "pid" not in res.meta:
            return
        
        pid = res.meta["pid"]
        name = res.meta.get("name", "Unknown")
        
        # Check if confirmation is enabled
        confirm_kill = True
        if self.config:
            confirm_kill = self.config.get_syshealth_config("confirm_kill")
        
        # Show confirmation dialog if enabled
        if confirm_kill:
            reply = QMessageBox.question(
                self,
                "Confirmar terminación de proceso",
                f"¿Está seguro de que desea terminar el proceso?\n\n"
                f"Nombre: {name}\n"
                f"PID: {pid}\n\n"
                f"Esta acción no se puede deshacer.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        
        # Get syshealth instance from search engine
        if hasattr(self.search, 'engine') and hasattr(self.search.engine, 'syshealth'):
            syshealth = self.search.engine.syshealth
            if syshealth:
                success, message = syshealth.kill(pid)
                
                # Show feedback
                if success:
                    QMessageBox.information(self, "Éxito", message)
                else:
                    QMessageBox.warning(self, "Error", message)
                
                # Hide launcher and refresh results
                self.hide()
                if success:
                    # Trigger refresh of search results
                    self.on_text_changed(self.input.text())
            else:
                QMessageBox.warning(self, "Error", "Módulo SysHealth no disponible")
        else:
            QMessageBox.warning(self, "Error", "No se puede acceder al módulo SysHealth")

    def _copy_text(self, text: str):
        QGuiApplication.clipboard().setText(text)

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == QEvent.FocusOut:
            self.hide()
        return super().eventFilter(obj, event)

    def _set_inactive(self):
        self.setWindowOpacity(self._inactive_opacity)

    def _set_active(self):
        self.setWindowOpacity(self._active_opacity)
