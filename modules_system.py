import ast
import operator as op
import re
from dataclasses import dataclass
from typing import Optional
from core import SearchResult

_ALLOWED = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}

_CURRENCY_RATES = {
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.09,
    ("USD", "MXN"): 17.0,
    ("MXN", "USD"): 0.059,
    ("EUR", "MXN"): 18.5,
    ("MXN", "EUR"): 0.054,
}

_UNIT_FACTORS = {
    ("m", "cm"): 100.0,
    ("cm", "m"): 0.01,
    ("km", "m"): 1000.0,
    ("m", "km"): 0.001,
    ("kg", "g"): 1000.0,
    ("g", "kg"): 0.001,
}

class Calculator:
    def try_calculate(self, text: str) -> Optional[SearchResult]:
        if not text:
            return None

        m_currency = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]{3})\s+a\s+([A-Za-z]{3})", text, re.IGNORECASE)
        if m_currency:
            amount = float(m_currency.group(1))
            src = m_currency.group(2).upper()
            dst = m_currency.group(3).upper()
            rate = _CURRENCY_RATES.get((src, dst))
            if rate:
                value = amount * rate
                title = f"{amount:.4g} {src} → {value:.4g} {dst}"
                return SearchResult(title=title, subtitle="Conversión (tasas en caché)", copy_text=f"{value:.6g}", group="calculator")

        m_unit = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)\s+a\s+([A-Za-z]+)", text, re.IGNORECASE)
        if m_unit:
            amount = float(m_unit.group(1))
            src = m_unit.group(2).lower()
            dst = m_unit.group(3).lower()
            factor = _UNIT_FACTORS.get((src, dst))
            if factor:
                value = amount * factor
                title = f"{amount:g} {src} → {value:g} {dst}"
                return SearchResult(title=title, subtitle="Conversión de unidades", copy_text=str(value), group="calculator")

        if re.match(r"^[\d\(\).\s\+\-\*\/\^%]+$", text):
            try:
                value = self._safe_eval(text.replace("^", "**"))
                return SearchResult(title=f"{value}", subtitle="Resultado de calculadora", copy_text=str(value), group="calculator")
            except Exception:
                return None

        return None

    def _safe_eval(self, expr: str):
        node = ast.parse(expr, mode="eval")
        return self._eval(node.body)

    def _eval(self, node):
        if isinstance(node, ast.Num):  # literal
            return node.n
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ALLOWED:
                raise ValueError("Operador no permitido")
            return _ALLOWED[type(node.op)](self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in _ALLOWED:
                raise ValueError("Operador no permitido")
            return _ALLOWED[type(node.op)](self._eval(node.operand))
        raise ValueError("Expresión no soportada")



from typing import List
from PySide6.QtCore import QObject, QTimer, QByteArray
from PySide6.QtGui import QClipboard, QGuiApplication
from core import Storage

class ClipboardManager(QObject):
    def __init__(self, poll_ms=500):
        super().__init__()
        self.clip = QGuiApplication.clipboard()
        self.storage = Storage()
        seq_func = getattr(self.clip, "sequenceNumber", None)
        self._seq_func = seq_func if callable(seq_func) else None
        self._last_seq = self._seq_func() if self._seq_func else 0
        self._timer = QTimer()
        self._timer.setInterval(poll_ms)
        self._timer.timeout.connect(self._tick)
        if self._seq_func:
            self._timer.start()

    def _tick(self):
        if not self._seq_func:
            return
        seq = self._seq_func()
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



import threading
import time
from typing import Optional, List
import keyboard
from core import Storage
from core import SearchResult

class SnippetManager:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()
        self._registered = {}  # hotkey -> snippet_id
        self._register_hotkeys()

    def _register_hotkeys(self):
        threading.Thread(target=self._async_register, daemon=True).start()

    def _async_register(self):
        snippets = self.storage.list_snippets()
        for snip in snippets:
            hotkey = snip["hotkey"]
            if hotkey and hotkey not in self._registered:
                keyboard.add_hotkey(hotkey, lambda s=snip: self.expand_snippet(s))
                self._registered[hotkey] = snip["id"]

    def expand_snippet(self, snippet_row):
        body = snippet_row["body"]
        send_text_ime_safe(body)

    def resolve_trigger(self, trigger: str) -> Optional[SearchResult]:
        sn = self.storage.get_snippet_by_trigger(trigger)
        if not sn:
            return None
        return SearchResult(
            title=f"{sn['name']} ({sn['trigger']})",
            subtitle="Snippet",
            action=lambda: self.expand_snippet(sn),
            copy_text=sn["body"],
            group="snippet",
        )

    def search(self, q: str, limit: int = 30) -> List[SearchResult]:
        results = []
        for sn in self.storage.list_snippets(q=q, limit=limit):
            results.append(
                SearchResult(
                    title=f"{sn['name']} ({sn['trigger']})",
                    subtitle=sn["body"][:80],
                    action=lambda s=sn: self.expand_snippet(s),
                    copy_text=sn["body"],
                    group="snippet",
                )
            )
        return results



import time
import win32con
import win32api
import win32clipboard
from ctypes import Structure, c_ulong, POINTER, sizeof
try:
    from ctypes import windll
except ImportError:
    windll = None

class KEYBDINPUT(Structure):
    _fields_ = [("wVk", c_ulong),
                ("wScan", c_ulong),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", c_ulong)]

class INPUT(Structure):
    _fields_ = [("type", c_ulong),
                ("ki", KEYBDINPUT)]

def _send_vk(vk, flags=0):
    try:
        if not windll or not hasattr(windll, "user32"):
            return
        ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=flags, time=0, dwExtraInfo=0)
        inp = INPUT(type=win32con.INPUT_KEYBOARD, ki=ki)
        windll.user32.SendInput(1, POINTER(INPUT)(inp), sizeof(INPUT))
    except Exception:
        return

def _press_ctrl_v():
    _send_vk(win32con.VK_CONTROL)
    _send_vk(ord('V'))
    _send_vk(ord('V'), win32con.KEYEVENTF_KEYUP)
    _send_vk(win32con.VK_CONTROL, win32con.KEYEVENTF_KEYUP)

def send_text_ime_safe(text: str):
    if not text:
        return
    try:
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    backup = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                else:
                    backup = None
            except Exception:
                backup = None
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
    except Exception:
        backup = None

    time.sleep(0.05)
    _press_ctrl_v()
    time.sleep(0.05)

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        if backup is not None:
            win32clipboard.SetClipboardText(backup, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
    except Exception:
        pass



import logging
from pathlib import Path
from datetime import datetime

LOG_PATH = Path.home() / ".fastlauncher" / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_PATH / "app.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def log(msg: str):
    logging.info(msg)

def diag_snapshot(file_indexer=None):
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "log_file": str(LOG_FILE),
    }
    
    if file_indexer:
        stats = file_indexer.get_stats()
        snapshot["file_indexer"] = {
            "files_indexed": stats.get("files_indexed", 0),
            "errors": stats.get("errors", 0),
            "last_run": datetime.fromtimestamp(stats["last_run"]).isoformat() if stats.get("last_run") else None,
            "roots": file_indexer.roots,
        }
    
    return snapshot



import ctypes
from ctypes import wintypes
import win32con
import win32gui
import win32api
import win32process
from typing import Dict, Optional

SPI_GETWORKAREA = 0x0030

def _get_work_area():
    try:
        rect = wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
        return rect
    except Exception:
        class DummyRect:
            left, top, right, bottom = 0, 0, 1920, 1080
        return DummyRect()

def _get_foreground_hwnd():
    return win32gui.GetForegroundWindow()

def get_active_window_info() -> Dict[str, str]:
    try:
        hwnd = win32gui.GetForegroundWindow()
        
        title = win32gui.GetWindowText(hwnd)
        
        window_class = win32gui.GetClassName(hwnd)
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            import psutil
            process = psutil.Process(pid)
            process_name = process.name()
        except:
            process_name = ""
        
        return {
            "hwnd": hwnd,
            "title": title,
            "class": window_class,
            "process": process_name,
            "pid": pid
        }
    except Exception as e:
        return {
            "hwnd": 0,
            "title": "",
            "class": "",
            "process": "",
            "pid": 0
        }

def detect_app_context() -> Optional[str]:
    info = get_active_window_info()
    title = info["title"].lower()
    process = info["process"].lower()
    window_class = info["class"].lower()
    
    if "visual studio code" in title or "code.exe" in process:
        return "vscode"
    
    if any(browser in process for browser in ["chrome.exe", "firefox.exe", "msedge.exe"]):
        return "browser"
    
    if "explorer.exe" in process and "cabinetw" in window_class:
        return "explorer"
    
    if "figma" in title.lower():
        return "figma"
    
    if any(term in process for term in ["cmd.exe", "powershell.exe", "windowsterminal.exe"]):
        return "terminal"
    
    if "winword.exe" in process:
        return "word"
    if "excel.exe" in process:
        return "excel"
    if "powerpnt.exe" in process:
        return "powerpoint"
    
    return None

def _get_monitor_info_from_hwnd(hwnd):
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    return win32api.GetMonitorInfo(monitor)

def _move(hwnd, x, y, w, h):
    win32gui.SetWindowPos(hwnd, None, x, y, w, h, win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)

def snap_left():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    width = (wa.right - wa.left) // 2
    _move(hwnd, wa.left, wa.top, width, wa.bottom - wa.top)

def snap_right():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    width = (wa.right - wa.left) // 2
    _move(hwnd, wa.left + width, wa.top, width, wa.bottom - wa.top)

def snap_top():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    _move(hwnd, wa.left, wa.top, wa.right - wa.left, (wa.bottom - wa.top)//2)

def snap_bottom():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    _move(hwnd, wa.left, wa.top + (wa.bottom - wa.top)//2, wa.right - wa.left, (wa.bottom - wa.top)//2)

def snap_quadrant(position: str):
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    half_w = (wa.right - wa.left)//2
    half_h = (wa.bottom - wa.top)//2
    x = wa.left if "left" in position else wa.left + half_w
    y = wa.top if "top" in position else wa.top + half_h
    _move(hwnd, x, y, half_w, half_h)

def maximize():
    hwnd = _get_foreground_hwnd()
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

def center():
    hwnd = _get_foreground_hwnd()
    wa = _get_work_area()
    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x = wa.left + ((wa.right - wa.left) - w)//2
    y = wa.top + ((wa.bottom - wa.top) - h)//2
    _move(hwnd, x, y, w, h)

def move_next_monitor():
    hwnd = _get_foreground_hwnd()
    info = _get_monitor_info_from_hwnd(hwnd)
    monitors = win32api.EnumDisplayMonitors()
    current_idx = 0
    for idx, mon in enumerate(monitors):
        if mon[0] == info["Monitor"]:
            current_idx = idx
            break
    next_idx = (current_idx + 1) % len(monitors)
    next_info = win32api.GetMonitorInfo(monitors[next_idx][0])
    wa = next_info["Work"]
    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    x = wa[0] + ((wa[2] - wa[0]) - w)//2
    y = wa[1] + ((wa[3] - wa[1]) - h)//2
    _move(hwnd, x, y, w, h)



import json
from pathlib import Path
from typing import Dict, Any, Callable, Optional

class PluginShell:
    def __init__(self):
        self.plugins: Dict[str, Dict[str, Any]] = {}

    def load_manifest(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.plugins[manifest["id"]] = manifest
        return manifest

    def execute(self, plugin_id: str, action: str, payload: dict):
        if plugin_id not in self.plugins:
            raise ValueError("Plugin no cargado")
        manifest = self.plugins[plugin_id]
        if action not in manifest.get("actions", []):
            raise ValueError("Acción no permitida por manifest")
        return {"plugin": plugin_id, "action": action, "ok": True, "payload": payload}



from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen

class GridPreview(QWidget):
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



import keyboard
from PySide6.QtWidgets import QApplication

class WindowHotkeys:
    def __init__(self, preview: GridPreview | None = None):
        self.preview = preview
        self._registered = False

    def register(self):
        if self._registered:
            return
        self._registered = True
        keyboard.add_hotkey("windows+shift+left", lambda: self._with_preview(snap_left))
        keyboard.add_hotkey("windows+shift+right", lambda: self._with_preview(snap_right))
        keyboard.add_hotkey("windows+shift+up", lambda: self._with_preview(lambda: snap_quadrant("top")))
        keyboard.add_hotkey("windows+shift+down", lambda: self._with_preview(lambda: snap_quadrant("bottom")))
        keyboard.add_hotkey("windows+shift+enter", lambda: self._with_preview(center))
        keyboard.add_hotkey("windows+shift+m", lambda: self._with_preview(maximize))
        keyboard.add_hotkey("windows+shift+page_up", lambda: self._with_preview(move_next_monitor))

    def _with_preview(self, action):
        if self.preview:
            self.preview.show()
            QApplication.processEvents()
        try:
            action()
        finally:
            if self.preview:
                self.preview.hide()
