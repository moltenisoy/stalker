"""
Editor minimal de notas en texto plano/Markdown.
CRÍTICO: Se desactiva el rich-text para evitar conversión de <, >, & a entidades HTML.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPlainTextEdit, QPushButton
from PySide6.QtCore import Qt
from modules.notes import NotesManager

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