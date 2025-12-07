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
        """Show error message with traceback."""
        error_msg = f"{str(error)}\n\n{traceback.format_exc()}"
        print(f"Error: {error_msg}")
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
            accent = self.accent_input.text().strip()
            if not accent.startswith("#"):
                self._show_message("Error", "El color debe empezar con # (ej: #3a86ff)", QMessageBox.Warning)
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
                if self.app_ref:
                    theme = self.config.get_ui("theme")
                    self.app_ref._apply_theme(dark=(theme == "dark"))
                    message_parts.append("\n✓ Tema aplicado")
                
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