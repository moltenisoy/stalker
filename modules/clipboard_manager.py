from typing import List
from PySide6.QtCore import QObject, QTimer, QByteArray
from PySide6.QtGui import QClipboard, QGuiApplication
from core.storage import Storage

class ClipboardManager(QObject):
    """Monitorea el portapapeles de Qt y persiste entradas (texto, imágenes, urls, rutas)."""
    def __init__(self, poll_ms=500):
        super().__init__()
        self.clip = QGuiApplication.clipboard()
        self.storage = Storage()
        self._last_seq = self.clip.sequenceNumber()
        self._timer = QTimer()
        self._timer.setInterval(poll_ms)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        seq = self.clip.sequenceNumber()
        if seq == self._last_seq:
            return
        self._last_seq = seq
        mimedata = self.clip.mimeData()
        if mimedata.hasImage():
            img = self.clip.image()
            ba = QByteArray()
            img.save(ba, "PNG")
            self.storage.add_clip("image", bytes(ba), metadata={"format": "png"})
        elif mimedata.hasUrls():
            urls = [u.toString() for u in mimedata.urls()]
            self.storage.add_clip("url", "\n".join(urls).encode("utf-8"), metadata={})
        elif mimedata.hasText():
            text = mimedata.text()
            kind = "file" if ("\\" in text or "/" in text) and len(text) < 1024 else "text"
            self.storage.add_clip(kind, text.encode("utf-8"), metadata={})

    def search(self, q: str, limit: int = 50):
        return self.storage.list_clips(q=q, limit=limit)