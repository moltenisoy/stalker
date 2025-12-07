from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QGuiApplication


class AIResponsePanel(QWidget):
    insert_to_note_signal = Signal(str)  # Signal to insert text into a note
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Respuesta de IA")
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Don't delete when closed
        
        self._setup_ui()
        self.resize(600, 400)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self.title_label = QLabel("Respuesta de IA", self)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        self.response_text = QTextEdit(self)
        self.response_text.setReadOnly(True)
        self.response_text.setPlaceholderText("La respuesta de IA aparecerá aquí...")
        layout.addWidget(self.response_text, 1)  # Stretch factor 1
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.copy_btn = QPushButton("📋 Copiar", self)
        self.copy_btn.setToolTip("Copiar respuesta al portapapeles")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)
        
        self.insert_note_btn = QPushButton("📝 Insertar en Nota", self)
        self.insert_note_btn.setToolTip("Crear o insertar en una nota")
        self.insert_note_btn.clicked.connect(self._insert_to_note)
        button_layout.addWidget(self.insert_note_btn)
        
        self.close_btn = QPushButton("Cerrar", self)
        self.close_btn.clicked.connect(self.hide)
        button_layout.addWidget(self.close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def show_response(self, response: str, is_error: bool = False):
        self.response_text.setPlainText(response)
        
        if is_error:
            self.response_text.setStyleSheet("QTextEdit { color: #ff6b6b; }")
            self.title_label.setText("⚠️ Error de IA")
        else:
            self.response_text.setStyleSheet("QTextEdit { color: inherit; }")
            self.title_label.setText("✅ Respuesta de IA")
        
        self.show()
        self.raise_()
        self.activateWindow()
    
    def _copy_to_clipboard(self):
        text = self.response_text.toPlainText()
        if text:
            QGuiApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copiado", "Respuesta copiada al portapapeles.")
    
    def _insert_to_note(self):
        text = self.response_text.toPlainText()
        if text:
            self.insert_to_note_signal.emit(text)
            QMessageBox.information(
                self, 
                "Insertar en Nota", 
                "El texto se insertará en una nueva nota."
            )




from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPlainTextEdit, QPushButton
from PySide6.QtCore import Qt
from modules_ai import NotesManager

class NotesEditor(QWidget):
    def __init__(self, notes: NotesManager | None = None):
        super().__init__()
        self.notes = notes or NotesManager()
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



from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from typing import Optional


class SysHealthOverlay(QWidget):
    
    def __init__(self, syshealth, config=None):
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus, True)
        
        self.syshealth = syshealth
        self.config = config
        
        self._load_config()
        
        self._setup_ui()
        
        self._setup_timer()
        
        self._position_overlay()
    
    def _load_config(self):
        if self.config:
            self._update_interval = self.config.get_syshealth_config("overlay_update_interval")
            self._position = self.config.get_syshealth_config("overlay_position")
            self._performance_mode = self.config.get_performance_mode()
        else:
            self._update_interval = 5.0
            self._position = "top-right"
            self._performance_mode = False
        
        if self._performance_mode:
            self._update_interval = max(self._update_interval * 2, 10.0)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        self._apply_theme()
        
        self.cpu_label = QLabel("CPU: ---%")
        self.ram_label = QLabel("RAM: --- / --- GB")
        self.disk_label = QLabel("Disk: ---R/---W MB/s")
        self.net_label = QLabel("Net: ---↓/---↑ MB/s")
        
        font = QFont("Segoe UI", 9)
        for label in [self.cpu_label, self.ram_label, self.disk_label, self.net_label]:
            label.setFont(font)
            layout.addWidget(label)
        
        self.setFixedSize(220, 110)
    
    def _apply_theme(self):
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



from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox,
    QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core import ConfigManager
from pathlib import Path
import traceback


class SettingsPanel(QWidget):
    
    settings_changed = Signal()
    
    def __init__(self, config: ConfigManager | None = None, app_ref=None):
        super().__init__()
        self.config = config or ConfigManager()
        self.app_ref = app_ref  # Reference to LauncherApp for service restart
        
        self.setWindowTitle("Configuración - Stalker")
        self.setMinimumSize(600, 700)
        self.setWindowFlags(Qt.Window)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        
        main_layout.addWidget(self._create_hotkey_section())
        main_layout.addWidget(self._create_appearance_section())
        main_layout.addWidget(self._create_modules_section())
        main_layout.addWidget(self._create_performance_section())
        main_layout.addWidget(self._create_config_section())
        main_layout.addWidget(self._create_services_section())
        
        main_layout.addStretch()
        
        scroll.setWidget(container)
        
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(scroll)
        
        self._apply_theme()
    
    def _create_hotkey_section(self):
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
        group = QGroupBox("Apariencia")
        layout = QVBoxLayout()
        
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
        group = QGroupBox("Módulos")
        layout = QVBoxLayout()
        
        info = QLabel("Activa o desactiva módulos específicos:")
        info.setWordWrap(True)
        layout.addWidget(info)
        
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



from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont, QCursor, QGuiApplication
from core import PredictiveSearch
from core import SearchResult
from core import ConfigManager
from modules_system import send_text_ime_safe
from modules_system import GridPreview
from modules_system import WindowHotkeys

class LauncherWindow(QWidget):
    def __init__(self, config: ConfigManager = None, app_ref=None):
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus, False)
        self.setWindowModality(Qt.NonModal)
        self.setFocusPolicy(Qt.StrongFocus)

        self.config = config or ConfigManager()
        self.app_ref = app_ref
        
        self._apply_theme()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Apps, /files, /links, /clipboard, /snippets, /macros, /syshealth…")
        
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
        if self.app_ref:
            self.search.engine._app_ref = self.app_ref

        self.resize(580, 380)
        
        self._inactive_opacity = self.config.get_ui("opacity_inactive")
        self._active_opacity = self.config.get_ui("opacity_active")
        self._set_inactive()

        effects_enabled = self.config.get_ui("effects") and not self.config.get_performance_mode()
        if effects_enabled:
            self.grid_preview = GridPreview(cols=2, rows=2)
            self.win_hotkeys = WindowHotkeys(preview=self.grid_preview)
            self.win_hotkeys.register()
        else:
            self.grid_preview = None
            self.win_hotkeys = None

    def _apply_theme(self):
        ui_config = self.config.get_ui()
        theme = ui_config.get("theme", "dark")
        accent = ui_config.get("accent", "#3a86ff")
        effects = ui_config.get("effects", True)
        performance_mode = self.config.get_performance_mode()
        
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


