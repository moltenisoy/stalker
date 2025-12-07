import json
import time
import threading
import keyboard
import mouse
from dataclasses import dataclass, field
from typing import List, Literal, Any, Callable, Optional
from core import Storage
from core import SearchResult

EventType = Literal["key", "click"]

@dataclass
class MacroEvent:
    t: EventType
    data: Any
    dt: float

@dataclass
class Macro:
    name: str
    events: List[MacroEvent] = field(default_factory=list)

class MacroRecorder:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()
        self._recording = False
        self._start_time = 0
        self._events: List[MacroEvent] = []
        self._registered = {}

    def start(self):
        if self._recording:
            return
        self._recording = True
        self._start_time = time.time()
        self._events = []
        threading.Thread(target=self._record, daemon=True).start()

    def stop_and_save(self, name: str):
        self._recording = False
        macro = {"name": name, "events": [e.__dict__ for e in self._events]}
        self.storage.add_quicklink(name=name, target=json.dumps(macro), kind="command", category="macro")
        return macro

    def _record(self):
        def on_key(e):
            if not self._recording:
                return
            self._events.append(MacroEvent("key", {"name": e.name, "event_type": e.event_type}, time.time() - self._start_time))
        def on_click(x, y, button, pressed):
            if not self._recording:
                return
            self._events.append(MacroEvent("click", {"x": x, "y": y, "button": button, "pressed": pressed}, time.time() - self._start_time))
        keyboard.hook(on_key, suppress=False)
        mouse.hook(on_click)
        while self._recording:
            time.sleep(0.05)
        keyboard.unhook(on_key)
        mouse.unhook(on_click)

    def playback(self, macro_data: dict):
        events = [MacroEvent(**e) for e in macro_data.get("events", [])]
        last_dt = 0
        for ev in events:
            time.sleep(max(0, ev.dt - last_dt))
            last_dt = ev.dt
            if ev.t == "key":
                if ev.data.get("event_type") == "down":
                    keyboard.press(ev.data["name"])
                elif ev.data.get("event_type") == "up":
                    keyboard.release(ev.data["name"])
            elif ev.t == "click":
                if ev.data.get("pressed"):
                    mouse.press(ev.data["x"], ev.data["y"], button=ev.data["button"])
                else:
                    mouse.release(ev.data["x"], ev.data["y"], button=ev.data["button"])

    def search_macros(self, q: str = "", limit: int = 30):
        results = []
        for link in self.storage.list_quicklinks(q=q, limit=limit):
            if link["category"] != "macro":
                continue
            macro_data = json.loads(link["target"])
            results.append(
                SearchResult(
                    title=f"Macro: {macro_data['name']}",
                    subtitle=f"{len(macro_data.get('events', []))} eventos",
                    action=lambda m=macro_data: self.playback(m),
                    group="macro",
                )
            )
        return results



import re
import win32clipboard
import win32gui
from typing import List, Optional, Dict
from core import SearchResult

class ContextualActionsManager:
    
    def __init__(self):
        self.last_clipboard = ""
        self.active_window_title = ""
        self.active_window_class = ""
    
    def update_active_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            self.active_window_title = win32gui.GetWindowText(hwnd)
            self.active_window_class = win32gui.GetClassName(hwnd)
        except Exception as e:
            print(f"Error getting active window: {e}")
    
    def get_clipboard_content(self) -> str:
        try:
            win32clipboard.OpenClipboard()
            content = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return content
        except Exception as e:
            print(f"Error reading clipboard: {e}")
            return ""
    
    def set_clipboard_content(self, text: str):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error setting clipboard: {e}")
    
    def get_available_actions(self, query: str = "") -> List[SearchResult]:
        self.update_active_window()
        clipboard_content = self.get_clipboard_content()
        
        actions = []
        
        actions.extend(self._get_paste_actions(clipboard_content))
        
        if clipboard_content and clipboard_content.strip():
            actions.extend(self._get_transform_actions(clipboard_content))
            actions.extend(self._get_format_actions(clipboard_content))
            actions.extend(self._get_extraction_actions(clipboard_content))
        
        if query:
            qlow = query.lower()
            actions = [a for a in actions if qlow in a.title.lower() or qlow in a.subtitle.lower()]
        
        return actions
    
    def _get_paste_actions(self, clipboard_content: str) -> List[SearchResult]:
        actions = []
        
        actions.append(SearchResult(
            title="📋 Pegar Texto Plano",
            subtitle="Pegar sin formato (IME-safe)",
            action=lambda: self._paste_plain(),
            group="context_paste"
        ))
        
        if self._is_url(clipboard_content):
            actions.append(SearchResult(
                title="🌐 Pegar y Navegar",
                subtitle="Pegar URL y presionar Enter",
                action=lambda: self._paste_and_go(),
                group="context_paste"
            ))
        
        return actions
    
    def _get_transform_actions(self, text: str) -> List[SearchResult]:
        actions = []
        
        actions.append(SearchResult(
            title="🔠 MAYÚSCULAS",
            subtitle=f"Convertir a mayúsculas: {text[:50]}...",
            action=lambda: self._transform_and_paste(text, "uppercase"),
            group="context_transform"
        ))
        
        actions.append(SearchResult(
            title="🔡 minúsculas",
            subtitle=f"Convertir a minúsculas: {text[:50]}...",
            action=lambda: self._transform_and_paste(text, "lowercase"),
            group="context_transform"
        ))
        
        actions.append(SearchResult(
            title="🔤 Título",
            subtitle=f"Convertir a Título: {text[:50]}...",
            action=lambda: self._transform_and_paste(text, "title"),
            group="context_transform"
        ))
        
        return actions
    
    def _get_format_actions(self, text: str) -> List[SearchResult]:
        actions = []
        
        actions.append(SearchResult(
            title="✨ Limpiar Formato",
            subtitle="Eliminar formato, espacios extra y caracteres especiales",
            action=lambda: self._clean_and_paste(text),
            group="context_format"
        ))
        
        if '\n' in text or '\r' in text:
            actions.append(SearchResult(
                title="📏 Unir Líneas",
                subtitle="Eliminar saltos de línea",
                action=lambda: self._remove_linebreaks_and_paste(text),
                group="context_format"
            ))
        
        actions.append(SearchResult(
            title='💬 Entrecomillar',
            subtitle='Agregar comillas alrededor del texto',
            action=lambda: self._quote_and_paste(text),
            group="context_format"
        ))
        
        return actions
    
    def _get_extraction_actions(self, text: str) -> List[SearchResult]:
        actions = []
        
        urls = self._extract_urls(text)
        if urls:
            actions.append(SearchResult(
                title=f"🔗 Extraer Enlaces ({len(urls)})",
                subtitle="Extraer todos los URLs del texto",
                action=lambda: self._extract_and_paste(text, "urls"),
                group="context_extract"
            ))
        
        emails = self._extract_emails(text)
        if emails:
            actions.append(SearchResult(
                title=f"📧 Extraer Emails ({len(emails)})",
                subtitle="Extraer todas las direcciones de email",
                action=lambda: self._extract_and_paste(text, "emails"),
                group="context_extract"
            ))
        
        numbers = self._extract_numbers(text)
        if numbers:
            actions.append(SearchResult(
                title=f"🔢 Extraer Números ({len(numbers)})",
                subtitle="Extraer todos los números",
                action=lambda: self._extract_and_paste(text, "numbers"),
                group="context_extract"
            ))
        
        if self._looks_like_table(text):
            actions.append(SearchResult(
                title="📊 Convertir a CSV",
                subtitle="Convertir tabla a formato CSV",
                action=lambda: self._table_to_csv_and_paste(text),
                group="context_extract"
            ))
        
        return actions
    
    
    def _paste_plain(self):
        text = self.get_clipboard_content()
        if text:
            send_text_ime_safe(text)
    
    def _paste_and_go(self):
        text = self.get_clipboard_content()
        if text:
            send_text_ime_safe(text)
            import keyboard
            keyboard.send('enter')
    
    def _transform_and_paste(self, text: str, transform_type: str):
        if transform_type == "uppercase":
            result = text.upper()
        elif transform_type == "lowercase":
            result = text.lower()
        elif transform_type == "title":
            result = text.title()
        else:
            result = text
        
        send_text_ime_safe(result)
    
    def _clean_and_paste(self, text: str):
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = cleaned.strip()
        
        cleaned = cleaned.replace('\u200b', '')  # Zero-width space
        cleaned = cleaned.replace('\ufeff', '')  # BOM
        
        send_text_ime_safe(cleaned)
    
    def _remove_linebreaks_and_paste(self, text: str):
        result = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        result = re.sub(r'\s+', ' ', result).strip()
        send_text_ime_safe(result)
    
    def _quote_and_paste(self, text: str):
        result = f'"{text}"'
        send_text_ime_safe(result)
    
    def _extract_and_paste(self, text: str, extract_type: str):
        if extract_type == "urls":
            items = self._extract_urls(text)
        elif extract_type == "emails":
            items = self._extract_emails(text)
        elif extract_type == "numbers":
            items = self._extract_numbers(text)
        else:
            items = []
        
        result = '\n'.join(items)
        send_text_ime_safe(result)
    
    def _table_to_csv_and_paste(self, text: str):
        lines = text.split('\n')
        csv_lines = []
        
        for line in lines:
            if '\t' in line:
                cells = line.split('\t')
            elif '|' in line:
                cells = [c.strip() for c in line.split('|') if c.strip()]
            else:
                cells = re.split(r'\s{2,}', line)
            
            quoted_cells = [f'"{cell}"' if ',' in cell else cell for cell in cells]
            csv_lines.append(','.join(quoted_cells))
        
        result = '\n'.join(csv_lines)
        send_text_ime_safe(result)
    
    
    def _is_url(self, text: str) -> bool:
        from core import is_url
        return is_url(text)
    
    def _extract_urls(self, text: str) -> List[str]:
        from core import extract_urls
        return extract_urls(text)
    
    def _extract_emails(self, text: str) -> List[str]:
        from core import extract_emails
        return extract_emails(text)
    
    def _extract_numbers(self, text: str) -> List[str]:
        from core import extract_numbers
        return extract_numbers(text)
    
    def _looks_like_table(self, text: str) -> bool:
        lines = text.split('\n')
        if len(lines) < 2:
            return False
        
        table_lines = 0
        for line in lines:
            if '\t' in line or re.search(r'\s{2,}', line) or '|' in line:
                table_lines += 1
        
        return table_lines >= len(lines) * 0.5  # At least 50% of lines look like table rows



