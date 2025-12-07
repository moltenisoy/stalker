from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont, QCursor, QGuiApplication
from core.search import PredictiveSearch
from core.engine import SearchResult
from modules.keystroke import send_text_ime_safe
from modules.grid_preview import GridPreview
from modules.hotkeys_window import WindowHotkeys

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__(flags=Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus, False)
        self.setWindowModality(Qt.NonModal)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setStyleSheet("""
        QWidget { background-color: rgba(15, 23, 42, 215); border-radius: 12px; color: #eaeaea; }
        QLineEdit { padding: 10px 12px; border: 1px solid #3a86ff; border-radius: 8px; background: rgba(26, 32, 44, 230); color: #eaeaea; selection-background-color: #3a86ff; }
        QListWidget { border: 1px solid #1f2937; border-radius: 8px; background: rgba(17, 24, 39, 230); outline: none; }
        QListWidget::item { padding: 8px 10px; }
        QListWidget::item:selected { background: #3a86ff; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Apps, /files, /links, /clipboard, /snippets, /macros, /syshealth…")
        self.input.setFont(QFont("Segoe UI", 11))
        self.input.textChanged.connect(self.on_text_changed)
        self.input.installEventFilter(self)

        self.list = QListWidget(self)
        self.list.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(self.input)
        layout.addWidget(self.list)

        self.search = PredictiveSearch(debounce_ms=250)
        self.search.results_ready.connect(self.populate_results)

        self.resize(580, 380)
        self._inactive_opacity = 0.6
        self._active_opacity = 0.98
        self._set_inactive()

        # Visual grid preview + window hotkeys
        self.grid_preview = GridPreview(cols=2, rows=2)
        self.win_hotkeys = WindowHotkeys(preview=self.grid_preview)
        self.win_hotkeys.register()

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

    def _paste_plain_current(self):
        current = self.list.currentItem()
        if not current:
            return
        res: SearchResult = current.data(Qt.UserRole)
        if res and res.copy_text:
            send_text_ime_safe(res.copy_text)
            self.hide()

    def _kill_current_if_process(self):
        current = self.list.currentItem()
        if not current:
            return
        res: SearchResult = current.data(Qt.UserRole)
        if res and res.group == "process" and res.meta and "pid" in res.meta:
            try:
                res.action()  # kill
            except Exception as ex:
                print(f"Error al terminar proceso: {ex}")
            self.hide()

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