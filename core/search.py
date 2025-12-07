from PySide6.QtCore import QTimer, Signal, QObject
from core.engine import SearchEngine, SearchResult

class PredictiveSearch(QObject):
    results_ready = Signal(list)

    def __init__(self, debounce_ms=300):
        super().__init__()
        self.debounce_ms = debounce_ms
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._emit_results)
        self._pending_query = ""
        self.engine = SearchEngine()

    def query(self, text: str):
        self._pending_query = text
        self._timer.start(self.debounce_ms)

    def _emit_results(self):
        results = self.engine.search(self._pending_query)
        self.results_ready.emit(results)