from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen

class GridPreview(QWidget):
    """Overlay semitransparente para visualizar snaps; mostrar/ocultar rápido."""
    def __init__(self, parent=None, cols=2, rows=2):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.cols = cols
        self.rows = rows
        screen_geo = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geo)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0.12)
        painter.fillRect(self.rect(), QColor(33, 150, 243))  # azul tenue
        pen = QPen(QColor(255, 255, 255, 160), 2, Qt.DashLine)
        painter.setPen(pen)
        cell_w = self.width() / self.cols
        cell_h = self.height() / self.rows
        for c in range(1, self.cols):
            x = int(c * cell_w)
            painter.drawLine(x, 0, x, self.height())
        for r in range(1, self.rows):
            y = int(r * cell_h)
            painter.drawLine(0, y, self.width(), y)