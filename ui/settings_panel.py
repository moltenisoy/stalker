from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QPushButton
from core.config import ConfigManager

class SettingsPanel(QWidget):
    def __init__(self, config: ConfigManager | None = None):
        super().__init__()
        self.config = config or ConfigManager()
        self.setWindowTitle("Configuración profunda")
        layout = QVBoxLayout(self)

        self.performance = QCheckBox("Modo Ahorro de Rendimiento")
        self.performance.setChecked(self.config.data["performance_mode"])
        self.performance.stateChanged.connect(self.on_perf)

        self.btn_export = QPushButton("Exportar configuración")
        self.btn_import = QPushButton("Importar configuración (config.import.json)")
        self.btn_export.clicked.connect(self.on_export)
        self.btn_import.clicked.connect(self.on_import)

        layout.addWidget(QLabel("Activación / Apariencia se maneja en config.json (fuente, colores, opacidad)."))
        layout.addWidget(self.performance)
        layout.addWidget(QLabel("Módulos (activar/desactivar en config.json): optimizer, clipboard, snippets, ai, files, links, macros"))
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_import)

    def on_perf(self, state):
        self.config.toggle_performance_mode(bool(state))

    def on_export(self):
        from pathlib import Path
        self.config.export(Path.home() / ".fastlauncher" / "config.export.json")

    def on_import(self):
        from pathlib import Path
        src = Path.home() / ".fastlauncher" / "config.import.json"
        if src.exists():
            self.config.import_file(src)