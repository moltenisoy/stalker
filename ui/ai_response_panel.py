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
