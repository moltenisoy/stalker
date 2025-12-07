__version__ = "2.0.0"

from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, Any

@dataclass
class SearchResult:
    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    copy_text: Optional[str] = None
    group: str = "general"
    meta: Optional[Dict[str, Any]] = None
    score: float = 0.0  # Higher score = higher priority




import re

URL_PATTERN = r'http[s]?://(?:[a-zA-Z0-9$\-_.+!*\'(),@&]|(?:%[0-9a-fA-F]{2}))+'

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

NUMBER_PATTERN = r'\b(?:\d+\.?\d*|\.\d+)\b'

WINDOWS_PATH_PATTERN = r'[A-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'

def extract_urls(text: str) -> list:
    return re.findall(URL_PATTERN, text)

def extract_emails(text: str) -> list:
    return re.findall(EMAIL_PATTERN, text)

def extract_numbers(text: str) -> list:
    return re.findall(NUMBER_PATTERN, text)

def is_url(text: str) -> bool:
    return bool(re.match(r'^' + URL_PATTERN + r'$', text.strip()))

def is_email(text: str) -> bool:
    return bool(re.match(r'^' + EMAIL_PATTERN + r'$', text.strip()))

def is_windows_path(text: str) -> bool:
    return bool(re.match(r'^' + WINDOWS_PATH_PATTERN + r'$', text.strip()))




import threading
import keyboard  # global hotkeys on Windows

DEFAULT_HOTKEY = "ctrl+space"  # avoids Alt+Space conflicts with PowerToys

class GlobalHotkey:
    def __init__(self, callback, hotkey: str = DEFAULT_HOTKEY):
        self.callback = callback
        self.hotkey = hotkey
        self._listener_thread = None
        self._registered = False

    def register(self):
        if self._listener_thread and self._listener_thread.is_alive():
            return
        self._registered = True
        self._listener_thread = threading.Thread(target=self._listen, daemon=True)
        self._listener_thread.start()
    
    def unregister(self):
        if self._registered:
            try:
                keyboard.remove_hotkey(self.hotkey)
                self._registered = False
            except (KeyError, RuntimeError) as e:
                import logging
                logging.debug(f"Error unregistering hotkey {self.hotkey}: {e}")
            except Exception as e:
                import logging
                logging.warning(f"Unexpected error unregistering hotkey {self.hotkey}: {e}")

    def _listen(self):
        keyboard.add_hotkey(self.hotkey, self.callback, suppress=False, trigger_on_release=True)
        keyboard.wait()  # block thread to keep listener alive



import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import time
import os
import base64

DB_PATH = Path.home() / ".fastlauncher" / "storage.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

KEY_FILE = Path.home() / ".fastlauncher" / "encryption.key"

class Storage:
    def __init__(self, path: Path = DB_PATH, encrypt_keys: bool = True):
        self.path = path
        self.encrypt_keys = encrypt_keys
        self._cipher = None
        if encrypt_keys:
            self._init_encryption()
        self._init_db()
    
    def _init_encryption(self):
        try:
            from cryptography.fernet import Fernet
            
            if KEY_FILE.exists():
                with open(KEY_FILE, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(KEY_FILE, 'wb') as f:
                    f.write(key)
                if hasattr(os, 'chmod'):
                    os.chmod(KEY_FILE, 0o600)
            
            self._cipher = Fernet(key)
        except ImportError:
            self.encrypt_keys = False
            self._cipher = None
        except Exception:
            self.encrypt_keys = False
            self._cipher = None
    
    def _encrypt_data(self, data: str) -> str:
        if not self.encrypt_keys or not self._cipher:
            return data
        try:
            encrypted = self._cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception:
            return data
    
    def _decrypt_data(self, data: str) -> str:
        if not self.encrypt_keys or not self._cipher:
            return data
        try:
            encrypted = base64.b64decode(data.encode())
            decrypted = self._cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception:
            return data

    def _conn(self):
        return sqlite3.connect(self.path)

    def _init_db(self):
        with self._conn() as conn:
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS clipboard(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                content BLOB NOT NULL,
                metadata TEXT,
                pinned INTEGER DEFAULT 0,
                folder TEXT DEFAULT '',
                created_at REAL NOT NULL
            );""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_clip_created ON clipboard(created_at DESC);")
            c.execute("""
            CREATE TABLE IF NOT EXISTS snippets(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                trigger TEXT NOT NULL UNIQUE,
                body TEXT NOT NULL,
                folder TEXT DEFAULT '',
                icon TEXT DEFAULT '',
                hotkey TEXT UNIQUE,
                created_at REAL NOT NULL
            );""")
            c.execute("""
            CREATE TABLE IF NOT EXISTS quicklinks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                kind TEXT NOT NULL,
                category TEXT DEFAULT '',
                args TEXT DEFAULT '',
                icon TEXT DEFAULT '',
                hotkey TEXT UNIQUE,
                created_at REAL NOT NULL
            );""")
            c.execute("""
            CREATE TABLE IF NOT EXISTS apps(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                alias TEXT UNIQUE,
                created_at REAL NOT NULL
            );""")
            c.execute("""
            CREATE TABLE IF NOT EXISTS file_index(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                drive TEXT,
                name TEXT,
                updated_at REAL NOT NULL
            );""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_file_name ON file_index(name);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_file_drive ON file_index(drive);")
            c.execute("""
            CREATE TABLE IF NOT EXISTS notes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                tags TEXT DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );""")
            c.execute("""
            CREATE TABLE IF NOT EXISTS api_keys(
                provider TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                updated_at REAL NOT NULL
            );""")
            conn.commit()

    def add_note(self, title: str, body: str, tags: str):
        now = time.time()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO notes(title, body, tags, created_at, updated_at) VALUES (?,?,?,?,?)",
                (title, body, tags, now, now),
            )
            conn.commit()

    def update_note(self, note_id: int, title=None, body=None, tags=None):
        fields = {}
        if title is not None: fields["title"] = title
        if body is not None: fields["body"] = body
        if tags is not None: fields["tags"] = tags
        fields["updated_at"] = time.time()
        keys = ", ".join([f"{k}=?" for k in fields.keys()])
        with self._conn() as conn:
            conn.execute(f"UPDATE notes SET {keys} WHERE id=?", list(fields.values()) + [note_id])
            conn.commit()

    def list_notes(self, q: str = "", limit: int = 50):
        sql = "SELECT * FROM notes"
        args = []
        if q:
            sql += " WHERE title LIKE ? OR body LIKE ? OR tags LIKE ?"
            args.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        sql += " ORDER BY updated_at DESC LIMIT ?"
        args.append(limit)
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, args).fetchall()

    def set_api_key(self, provider: str, key: str):
        encrypted_key = self._encrypt_data(key)
        with self._conn() as conn:
            conn.execute("INSERT OR REPLACE INTO api_keys(provider, key, updated_at) VALUES (?, ?, ?)",
                         (provider, encrypted_key, time.time()))
            conn.commit()

    def get_api_key(self, provider: str):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT key, provider FROM api_keys WHERE provider=?", (provider,)).fetchone()
        if row:
            return self._decrypt_data(row["key"])
        return None

    def list_quicklinks(self, q: str = "", limit: int = 50):
        sql = "SELECT * FROM quicklinks"
        args = []
        if q:
            sql += " WHERE name LIKE ? OR target LIKE ? OR category LIKE ?"
            args.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        sql += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, args).fetchall()

    def replace_file_index(self, records: List[tuple]):
        with self._conn() as conn:
            conn.execute("DELETE FROM file_index")
            if records:
                conn.executemany(
                    "INSERT INTO file_index(path, drive, name, updated_at) VALUES (?, ?, ?, ?)",
                    records
                )
            conn.commit()

    def list_files(self, q: str = "", limit: int = 80):
        sql = "SELECT path, drive, name FROM file_index"
        args = []
        if q:
            sql += " WHERE name LIKE ?"
            args.append(f"%{q}%")
        sql += " ORDER BY name LIMIT ?"
        args.append(limit)
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, args).fetchall()

    def get_app_by_alias(self, alias: str):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM apps WHERE alias=?", (alias,)).fetchone()
        return dict(row) if row else None

    def list_apps(self, q: str = "", limit: int = 50):
        sql = "SELECT * FROM apps"
        args = []
        if q:
            sql += " WHERE name LIKE ? OR path LIKE ? OR alias LIKE ?"
            args.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        sql += " ORDER BY name LIMIT ?"
        args.append(limit)
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, args).fetchall()

    def add_app(self, name: str, path: str, alias: str = None):
        now = time.time()
        with self._conn() as conn:
            if alias:
                conn.execute(
                    "INSERT OR REPLACE INTO apps(name, path, alias, created_at) VALUES (?, ?, ?, ?)",
                    (name, path, alias, now)
                )
            else:
                existing = conn.execute("SELECT id FROM apps WHERE path=?", (path,)).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO apps(name, path, alias, created_at) VALUES (?, ?, ?, ?)",
                        (name, path, None, now)
                    )
            conn.commit()

    def clear_app_cache(self):
        with self._conn() as conn:
            conn.execute("DELETE FROM apps WHERE alias IS NULL")
            conn.commit()
    
    def add_clip(self, kind: str, content: bytes, metadata: dict = None):
        now = time.time()
        metadata_json = json.dumps(metadata) if metadata else "{}"
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO clipboard(kind, content, metadata, created_at) VALUES (?, ?, ?, ?)",
                (kind, content, metadata_json, now)
            )
            conn.commit()
    
    def list_clips(self, q: str = "", limit: int = 50):
        sql = "SELECT * FROM clipboard"
        args = []
        if q:
            sql += " WHERE kind LIKE ?"
            args.append(f"%{q}%")
        sql += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(sql, args).fetchall()
    
    def list_snippets(self, q: str = "", limit: int = 50):
        sql = "SELECT * FROM snippets"
        args = []
        if q:
            sql += " WHERE name LIKE ? OR trigger LIKE ? OR body LIKE ?"
            args.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        sql += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(sql, args).fetchall()
    
    def get_snippet_by_trigger(self, trigger: str):
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM snippets WHERE trigger=?", (trigger,)).fetchone()
            return dict(row) if row else None
    
    def add_quicklink(self, name: str, target: str, kind: str, category: str = "", args: str = "", icon: str = "", hotkey: str = None):
        now = time.time()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO quicklinks(name, target, kind, category, args, icon, hotkey, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, target, kind, category, args, icon, hotkey, now)
            )
            conn.commit()



import re
from typing import List, Dict, Tuple, Optional
from enum import Enum

class IntentType(Enum):
    OPEN_APP = "open_app"
    SEARCH_FILE = "search_file"
    PASTE_SNIPPET = "paste_snippet"
    SYSTEM_ACTION = "system_action"
    CLIPBOARD_ACTION = "clipboard_action"
    FILE_ACTION = "file_action"
    TEXT_TRANSFORM = "text_transform"
    CALCULATE = "calculate"
    TRANSLATE = "translate"
    WEB_SEARCH = "web_search"
    UNKNOWN = "unknown"

class Intent:
    def __init__(self, intent_type: IntentType, confidence: float, params: Dict = None):
        self.type = intent_type
        self.confidence = confidence  # 0.0 to 1.0
        self.params = params or {}
    
    def __repr__(self):
        return f"Intent({self.type.value}, confidence={self.confidence:.2f}, params={self.params})"

class IntentRouter:
    
    APP_PATTERNS = [
        (r"^(open|launch|start|run)\s+(.+)", 0.9),
        (r"^(.+)\s+(app|application|programa)", 0.8),
    ]
    
    FILE_PATTERNS = [
        (r"^(find|search|buscar|locate)\s+(.+)\s+(file|archivo)", 0.9),
        (r"^(file|archivo)[:;]\s*(.+)", 0.85),
        (r"\.(pdf|docx?|xlsx?|pptx?|txt|py|js|java|cpp|cs|html|css)$", 0.7),
    ]
    
    SNIPPET_PATTERNS = [
        (r"^[@;](.+)", 0.95),  # Direct snippet triggers
        (r"^(snippet|snip|paste)\s+(.+)", 0.8),
    ]
    
    SYSTEM_PATTERNS = [
        (r"^(lock|sleep|shutdown|restart|hibernate)", 0.9),
        (r"^(volume|brightness|wifi|bluetooth)\s+(up|down|on|off)", 0.85),
    ]
    
    CLIPBOARD_PATTERNS = [
        (r"^(copy|copiar|paste|pegar)\s+(.+)", 0.85),
        (r"^clip(board)?\s+(.+)", 0.8),
    ]
    
    FILE_ACTION_PATTERNS = [
        (r"^(zip|compress|extract|unzip)\s+(.+)", 0.85),
        (r"^(move|copy|delete|rename)\s+(.+)\s+(to|a)\s+(.+)", 0.85),
    ]
    
    TEXT_TRANSFORM_PATTERNS = [
        (r"^(uppercase|lowercase|capitalize|title)\s+(.+)", 0.9),
        (r"^(clean|limpiar|format|formatear)\s+(.+)", 0.8),
        (r"^(convert|convertir)\s+(.+)\s+(to|a)\s+(.+)", 0.85),
    ]
    
    TRANSLATE_PATTERNS = [
        (r"^(translate|traducir|traduire)\s+(.+)", 0.9),
        (r"^(to|a)\s+(english|spanish|french|german|italian)", 0.8),
    ]
    
    CALCULATE_PATTERNS = [
        (r"^\d+[\d+\-*/().\s]*[\d+\-*/()]+[\d+\-*/().\s]*\d+$", 0.7),
        (r"^(calc|calculate|calcula)\s+(.+)", 0.85),
    ]
    
    def __init__(self):
        pass
    
    def detect_intent(self, query: str) -> Intent:
        query = query.strip()
        qlow = query.lower()
        
        if not query:
            return Intent(IntentType.UNKNOWN, 0.0)
        
        intents = []
        
        for pattern, confidence in self.APP_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                app_name = match.group(2) if match.lastindex >= 2 else match.group(1)
                intents.append(Intent(IntentType.OPEN_APP, confidence, {"app": app_name}))
        
        for pattern, confidence in self.FILE_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                filename = match.group(2) if match.lastindex >= 2 else query
                intents.append(Intent(IntentType.SEARCH_FILE, confidence, {"filename": filename}))
        
        for pattern, confidence in self.SNIPPET_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                trigger = match.group(1) if match.lastindex >= 1 else query
                intents.append(Intent(IntentType.PASTE_SNIPPET, confidence, {"trigger": trigger}))
        
        for pattern, confidence in self.SYSTEM_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                action = match.group(0)
                intents.append(Intent(IntentType.SYSTEM_ACTION, confidence, {"action": action}))
        
        for pattern, confidence in self.CLIPBOARD_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                text = match.group(2) if match.lastindex >= 2 else ""
                intents.append(Intent(IntentType.CLIPBOARD_ACTION, confidence, {"text": text}))
        
        for pattern, confidence in self.FILE_ACTION_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                action = match.group(1)
                target = match.group(2)
                intents.append(Intent(IntentType.FILE_ACTION, confidence, {"action": action, "target": target}))
        
        for pattern, confidence in self.TEXT_TRANSFORM_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                transform = match.group(1)
                text = match.group(2) if match.lastindex >= 2 else ""
                intents.append(Intent(IntentType.TEXT_TRANSFORM, confidence, {"transform": transform, "text": text}))
        
        for pattern, confidence in self.TRANSLATE_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                text = match.group(2) if match.lastindex >= 2 else query
                intents.append(Intent(IntentType.TRANSLATE, confidence, {"text": text}))
        
        for pattern, confidence in self.CALCULATE_PATTERNS:
            if re.fullmatch(pattern, qlow):
                intents.append(Intent(IntentType.CALCULATE, confidence, {"expression": query}))
        
        if intents:
            return max(intents, key=lambda i: i.confidence)
        
        return Intent(IntentType.UNKNOWN, 0.0)
    
    def detect_all_intents(self, query: str) -> List[Intent]:
        primary = self.detect_intent(query)
        return [primary] if primary.confidence > 0.5 else []




import os
import zipfile
import shutil
import subprocess
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class ActionStep:
    name: str
    description: str
    action: Callable
    params: Dict[str, Any] = None
    requires_confirmation: bool = False
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}

class CompoundAction:
    
    def __init__(self, name: str, description: str, steps: List[ActionStep]):
        self.name = name
        self.description = description
        self.steps = steps
        self.current_step = 0
    
    def execute_next(self) -> bool:
        if self.current_step >= len(self.steps):
            return False
        
        step = self.steps[self.current_step]
        if step.action:
            step.action(**step.params)
        self.current_step += 1
        
        return self.current_step < len(self.steps)
    
    def reset(self):
        self.current_step = 0
    
    def get_current_step(self) -> Optional[ActionStep]:
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

class CompoundActionManager:
    
    def __init__(self):
        self._actions = {}
        self._register_builtin_actions()
    
    def _register_builtin_actions(self):
        self.register_action(
            "zip_and_share",
            "Zip y Compartir",
            "Comprimir archivos y copiar ruta al portapapeles",
            [
                ActionStep("zip", "Comprimir archivos", self._zip_files),
                ActionStep("copy_path", "Copiar ruta", self._copy_path_to_clipboard),
            ]
        )
        
        self.register_action(
            "copy_and_open",
            "Copiar Ruta y Abrir Carpeta",
            "Copiar ruta del archivo y abrir carpeta contenedora",
            [
                ActionStep("copy", "Copiar ruta", self._copy_path_to_clipboard),
                ActionStep("open", "Abrir carpeta", self._open_folder),
            ]
        )
        
        self.register_action(
            "convert_and_paste",
            "Convertir y Pegar",
            "Convertir texto y pegar resultado",
            [
                ActionStep("convert", "Convertir", self._convert_text),
                ActionStep("paste", "Pegar", self._paste_text),
            ]
        )
        
        self.register_action(
            "translate_and_paste",
            "Traducir y Pegar",
            "Traducir texto y pegar resultado",
            [
                ActionStep("translate", "Traducir", self._translate_text),
                ActionStep("paste", "Pegar", self._paste_text),
            ]
        )
        
        self.register_action(
            "clean_and_paste",
            "Limpiar y Pegar",
            "Limpiar formato de texto y pegar",
            [
                ActionStep("clean", "Limpiar formato", self._clean_format),
                ActionStep("paste", "Pegar", self._paste_text),
            ]
        )
    
    def register_action(self, action_id: str, name: str, description: str, steps: List[ActionStep]):
        self._actions[action_id] = CompoundAction(name, description, steps)
    
    def get_action(self, action_id: str) -> Optional[CompoundAction]:
        return self._actions.get(action_id)
    
    def get_all_actions(self) -> Dict[str, CompoundAction]:
        return self._actions.copy()
    
    def suggest_actions_for_context(self, context: str, selected_item: Optional[Dict] = None) -> List[SearchResult]:
        suggestions = []
        
        if context == "file_selected" and selected_item:
            filepath = selected_item.get("path", "")
            
            suggestions.append(SearchResult(
                title="🗜️ Zip y Compartir",
                subtitle="Comprimir archivo(s) y copiar ruta",
                action=lambda: self._execute_zip_and_share(filepath),
                group="compound"
            ))
            
            suggestions.append(SearchResult(
                title="📋 Copiar Ruta y Abrir Carpeta",
                subtitle="Copiar ruta y abrir ubicación",
                action=lambda: self._execute_copy_and_open(filepath),
                group="compound"
            ))
        
        elif context == "text_copied":
            suggestions.append(SearchResult(
                title="🌐 Traducir y Pegar",
                subtitle="Traducir texto copiado y pegar",
                action=lambda: self._execute_translate_and_paste(),
                group="compound"
            ))
            
            suggestions.append(SearchResult(
                title="✨ Limpiar y Pegar",
                subtitle="Limpiar formato y pegar como texto plano",
                action=lambda: self._execute_clean_and_paste(),
                group="compound"
            ))
            
            suggestions.append(SearchResult(
                title="🔄 Convertir y Pegar",
                subtitle="Convertir formato y pegar",
                action=lambda: self._execute_convert_and_paste(),
                group="compound"
            ))
        
        return suggestions
    
    def _execute_zip_and_share(self, filepath: str):
        action = self.get_action("zip_and_share")
        if action:
            action.reset()
            action.steps[0].params = {"filepath": filepath}
            action.steps[1].params = {"path": filepath + ".zip"}
            action.execute_next()
            action.execute_next()
    
    def _execute_copy_and_open(self, filepath: str):
        action = self.get_action("copy_and_open")
        if action:
            action.reset()
            action.steps[0].params = {"path": filepath}
            action.steps[1].params = {"path": os.path.dirname(filepath)}
            action.execute_next()
            action.execute_next()
    
    def _execute_translate_and_paste(self):
        action = self.get_action("translate_and_paste")
        if action:
            action.reset()
            action.execute_next()
            action.execute_next()
    
    def _execute_clean_and_paste(self):
        action = self.get_action("clean_and_paste")
        if action:
            action.reset()
            action.execute_next()
            action.execute_next()
    
    def _execute_convert_and_paste(self):
        action = self.get_action("convert_and_paste")
        if action:
            action.reset()
            action.execute_next()
            action.execute_next()
    
    def _zip_files(self, filepath: str, **kwargs):
        try:
            output_path = filepath + ".zip"
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(filepath):
                    zipf.write(filepath, os.path.basename(filepath))
                elif os.path.isdir(filepath):
                    for root, dirs, files in os.walk(filepath):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(filepath))
                            zipf.write(file_path, arcname)
            return output_path
        except Exception as e:
            print(f"Error zipping files: {e}")
            return None
    
    def _copy_path_to_clipboard(self, path: str, **kwargs):
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(path, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    
    def _open_folder(self, path: str, **kwargs):
        try:
            if os.path.isfile(path):
                folder = os.path.dirname(path)
            else:
                folder = path
            
            subprocess.run(['explorer', folder], shell=True)
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def _convert_text(self, text: str = None, target_format: str = "uppercase", **kwargs):
        if text is None:
            import win32clipboard
            try:
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except:
                return ""
        
        if target_format == "uppercase":
            return text.upper()
        elif target_format == "lowercase":
            return text.lower()
        elif target_format == "title":
            return text.title()
        return text
    
    def _translate_text(self, text: str = None, target_lang: str = "en", **kwargs):
        from modules_system import log
        log("Translation not yet implemented - returning original text")
        return f"[Translation pending: {text}]"
    
    def _paste_text(self, text: str = None, **kwargs):
        if text is None:
            import win32clipboard
            try:
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except:
                return
        
        try:
            from modules_system import send_text_ime_safe
            send_text_ime_safe(text)
        except Exception as e:
            print(f"Error pasting text: {e}")
    
    def _clean_format(self, text: str = None, **kwargs):
        if text is None:
            import win32clipboard
            try:
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except:
                return ""
        
        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text




import json
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict

@dataclass
class ContextAction:
    name: str
    description: str
    trigger: str  # Hotkey or command trigger
    action_type: str  # snippet, command, flow
    action_data: Dict
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict):
        return ContextAction(**data)

@dataclass
class AppProfile:
    app_name: str
    display_name: str
    window_class: str = ""
    window_title_pattern: str = ""
    actions: List[ContextAction] = None
    snippets: Dict[str, str] = None
    shortcuts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.snippets is None:
            self.snippets = {}
        if self.shortcuts is None:
            self.shortcuts = {}
    
    def to_dict(self):
        return {
            "app_name": self.app_name,
            "display_name": self.display_name,
            "window_class": self.window_class,
            "window_title_pattern": self.window_title_pattern,
            "actions": [a.to_dict() for a in self.actions],
            "snippets": self.snippets,
            "shortcuts": self.shortcuts,
        }
    
    @staticmethod
    def from_dict(data: Dict):
        actions = [ContextAction.from_dict(a) for a in data.get("actions", [])]
        return AppProfile(
            app_name=data["app_name"],
            display_name=data["display_name"],
            window_class=data.get("window_class", ""),
            window_title_pattern=data.get("window_title_pattern", ""),
            actions=actions,
            snippets=data.get("snippets", {}),
            shortcuts=data.get("shortcuts", {}),
        )

class ContextProfileManager:
    
    def __init__(self, profiles_dir: str = None):
        if profiles_dir is None:
            profiles_dir = os.path.join(os.path.expanduser("~"), ".stalker", "profiles")
        
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, AppProfile] = {}
        
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        self._register_builtin_profiles()
        
        self._load_profiles()
    
    def _register_builtin_profiles(self):
        
        vscode = AppProfile(
            app_name="vscode",
            display_name="Visual Studio Code",
            window_class="Chrome_WidgetWin_1",
            window_title_pattern="Visual Studio Code",
        )
        vscode.actions = [
            ContextAction(
                name="search_symbols",
                description="Buscar símbolos en el proyecto",
                trigger="ctrl+t",
                action_type="command",
                action_data={"command": "workbench.action.showAllSymbols"}
            ),
            ContextAction(
                name="find_file",
                description="Buscar archivo",
                trigger="ctrl+p",
                action_type="command",
                action_data={"command": "workbench.action.quickOpen"}
            ),
            ContextAction(
                name="terminal",
                description="Abrir terminal integrada",
                trigger="ctrl+`",
                action_type="command",
                action_data={"command": "workbench.action.terminal.toggleTerminal"}
            ),
        ]
        vscode.snippets = {
            "@log": "console.log('${1}', ${1});",
            "@func": "function ${1:name}(${2:params}) {\n\t${3}\n}",
            "@class": "class ${1:ClassName} {\n\tconstructor(${2}) {\n\t\t${3}\n\t}\n}",
        }
        self.profiles["vscode"] = vscode
        
        browser = AppProfile(
            app_name="browser",
            display_name="Navegador Web",
            window_class="Chrome_WidgetWin_1",
            window_title_pattern="Chrome|Firefox|Edge",
        )
        browser.actions = [
            ContextAction(
                name="save_session",
                description="Guardar sesión de pestañas",
                trigger="ctrl+shift+s",
                action_type="flow",
                action_data={"flow": "save_browser_tabs"}
            ),
            ContextAction(
                name="restore_session",
                description="Restaurar sesión de pestañas",
                trigger="ctrl+shift+r",
                action_type="flow",
                action_data={"flow": "restore_browser_tabs"}
            ),
            ContextAction(
                name="extract_links",
                description="Extraer todos los enlaces",
                trigger="ctrl+shift+l",
                action_type="flow",
                action_data={"flow": "extract_links"}
            ),
        ]
        self.profiles["browser"] = browser
        
        figma = AppProfile(
            app_name="figma",
            display_name="Figma",
            window_title_pattern="Figma",
        )
        figma.actions = [
            ContextAction(
                name="export_selection",
                description="Exportar selección",
                trigger="ctrl+shift+e",
                action_type="command",
                action_data={"command": "export"}
            ),
        ]
        self.profiles["figma"] = figma
        
        explorer = AppProfile(
            app_name="explorer",
            display_name="Explorador de Archivos",
            window_class="CabinetWClass",
        )
        explorer.actions = [
            ContextAction(
                name="copy_path",
                description="Copiar ruta completa",
                trigger="ctrl+shift+c",
                action_type="flow",
                action_data={"flow": "copy_current_path"}
            ),
            ContextAction(
                name="terminal_here",
                description="Abrir terminal aquí",
                trigger="ctrl+shift+t",
                action_type="flow",
                action_data={"flow": "open_terminal_here"}
            ),
        ]
        self.profiles["explorer"] = explorer
    
    def _load_profiles(self):
        if not os.path.exists(self.profiles_dir):
            return
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.profiles_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile = AppProfile.from_dict(data)
                        self.profiles[profile.app_name] = profile
                except Exception as e:
                    print(f"Error loading profile {filename}: {e}")
    
    def save_profile(self, profile: AppProfile):
        filepath = os.path.join(self.profiles_dir, f"{profile.app_name}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profile {profile.app_name}: {e}")
    
    def get_profile(self, app_name: str) -> Optional[AppProfile]:
        return self.profiles.get(app_name)
    
    def get_profile_for_window(self, window_title: str, window_class: str = "") -> Optional[AppProfile]:
        import re
        
        for profile in self.profiles.values():
            if profile.window_class and window_class:
                if profile.window_class == window_class:
                    return profile
            
            if profile.window_title_pattern:
                if re.search(profile.window_title_pattern, window_title, re.IGNORECASE):
                    return profile
        
        return None
    
    def get_actions_for_profile(self, profile: AppProfile) -> List[SearchResult]:
        results = []
        
        for action in profile.actions:
            results.append(SearchResult(
                title=f"⚡ {action.name}",
                subtitle=f"{action.description} ({action.trigger})",
                action=lambda a=action: self._execute_action(a),
                group=f"context_{profile.app_name}"
            ))
        
        return results
    
    def get_snippets_for_profile(self, profile: AppProfile, query: str = "") -> List[SearchResult]:
        results = []
        qlow = query.lower()
        
        for trigger, body in profile.snippets.items():
            if not query or qlow in trigger.lower() or qlow in body.lower():
                results.append(SearchResult(
                    title=f"📝 {trigger}",
                    subtitle=body[:80],
                    action=lambda b=body: self._paste_snippet(b),
                    copy_text=body,
                    group=f"snippet_{profile.app_name}"
                ))
        
        return results
    
    def _execute_action(self, action: ContextAction):
        from modules_system import log
        
        if action.action_type == "command":
            log(f"Executing command: {action.action_data.get('command')}")
        elif action.action_type == "flow":
            log(f"Executing flow: {action.action_data.get('flow')}")
        elif action.action_type == "snippet":
            text = action.action_data.get("text", "")
            self._paste_snippet(text)
    
    def _paste_snippet(self, text: str):
        try:
            from modules_system import send_text_ime_safe
            send_text_ime_safe(text)
        except Exception as e:
            print(f"Error pasting snippet: {e}")
    
    def create_profile(self, app_name: str, display_name: str) -> AppProfile:
        profile = AppProfile(app_name=app_name, display_name=display_name)
        self.profiles[app_name] = profile
        self.save_profile(profile)
        return profile
    
    def add_action_to_profile(self, app_name: str, action: ContextAction):
        profile = self.get_profile(app_name)
        if profile:
            profile.actions.append(action)
            self.save_profile(profile)
    
    def add_snippet_to_profile(self, app_name: str, trigger: str, body: str):
        profile = self.get_profile(app_name)
        if profile:
            profile.snippets[trigger] = body
            self.save_profile(profile)




import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class FlowStep:
    action: str  # Action type: 'keystroke', 'clipboard', 'command', 'wait', 'if'
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # Optional condition for conditional steps
    
    def to_dict(self):
        return {
            "action": self.action,
            "params": self.params,
            "condition": self.condition
        }
    
    @staticmethod
    def from_dict(data: Dict):
        return FlowStep(
            action=data["action"],
            params=data.get("params", {}),
            condition=data.get("condition")
        )

@dataclass
class FlowCommand:
    name: str
    description: str
    app_context: str  # App this flow is designed for
    steps: List[FlowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "app_context": self.app_context,
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables
        }
    
    @staticmethod
    def from_dict(data: Dict):
        steps = [FlowStep.from_dict(s) for s in data.get("steps", [])]
        return FlowCommand(
            name=data["name"],
            description=data["description"],
            app_context=data["app_context"],
            steps=steps,
            variables=data.get("variables", {})
        )

class FlowCommandExecutor:
    
    def __init__(self):
        self.action_handlers: Dict[str, Callable] = {
            "keystroke": self._handle_keystroke,
            "clipboard": self._handle_clipboard,
            "command": self._handle_command,
            "wait": self._handle_wait,
            "paste": self._handle_paste,
            "copy": self._handle_copy,
            "open": self._handle_open,
            "save": self._handle_save,
            "transform": self._handle_transform,
        }
    
    def execute(self, flow: FlowCommand, context: Dict[str, Any] = None) -> bool:
        from modules_system import log
        
        if context is None:
            context = {}
        
        variables = {**flow.variables, **context}
        
        try:
            for step in flow.steps:
                if step.condition and not self._evaluate_condition(step.condition, variables):
                    continue
                
                handler = self.action_handlers.get(step.action)
                if handler:
                    result = handler(step.params, variables)
                    if isinstance(result, dict):
                        variables.update(result)
                else:
                    log(f"Unknown action: {step.action}")
                    return False
            
            return True
        except Exception as e:
            log(f"Error executing flow {flow.name}: {e}")
            return False
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        try:
            parts = condition.split()
            if len(parts) == 3:
                var, op, value = parts
                var_value = variables.get(var)
                
                if op == "==":
                    return str(var_value) == value
                elif op == "!=":
                    return str(var_value) != value
        except:
            pass
        
        return True
    
    def _handle_keystroke(self, params: Dict, variables: Dict) -> None:
        keys = params.get("keys", "")
        for var, value in variables.items():
            keys = keys.replace(f"${{{var}}}", str(value))
        
        try:
            import keyboard
            keyboard.send(keys)
        except Exception as e:
            print(f"Error sending keystroke: {e}")
    
    def _handle_clipboard(self, params: Dict, variables: Dict) -> Dict:
        operation = params.get("operation", "get")
        
        try:
            import win32clipboard
            
            if operation == "get":
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return {"clipboard_content": text}
            elif operation == "set":
                text = params.get("text", "")
                for var, value in variables.items():
                    text = text.replace(f"${{{var}}}", str(value))
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error handling clipboard: {e}")
        
        return {}
    
    def _handle_command(self, params: Dict, variables: Dict) -> None:
        command = params.get("command", "")
        for var, value in variables.items():
            command = command.replace(f"${{{var}}}", str(value))
        
        try:
            import subprocess
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"Error executing command: {e}")
    
    def _handle_wait(self, params: Dict, variables: Dict) -> None:
        import time
        duration = params.get("duration", 0.5)
        time.sleep(duration)
    
    def _handle_paste(self, params: Dict, variables: Dict) -> None:
        text = params.get("text", "")
        for var, value in variables.items():
            text = text.replace(f"${{{var}}}", str(value))
        
        try:
            from modules_system import send_text_ime_safe
            send_text_ime_safe(text)
        except Exception as e:
            print(f"Error pasting text: {e}")
    
    def _handle_copy(self, params: Dict, variables: Dict) -> None:
        text = params.get("text", "")
        for var, value in variables.items():
            text = text.replace(f"${{{var}}}", str(value))
        
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error copying: {e}")
    
    def _handle_open(self, params: Dict, variables: Dict) -> None:
        path = params.get("path", "")
        for var, value in variables.items():
            path = path.replace(f"${{{var}}}", str(value))
        
        try:
            import subprocess
            subprocess.run(['explorer', path], shell=True)
        except Exception as e:
            print(f"Error opening: {e}")
    
    def _handle_save(self, params: Dict, variables: Dict) -> None:
        try:
            import keyboard
            keyboard.send('ctrl+s')
        except Exception as e:
            print(f"Error saving: {e}")
    
    def _handle_transform(self, params: Dict, variables: Dict) -> Dict:
        text = params.get("text", variables.get("clipboard_content", ""))
        transform_type = params.get("type", "uppercase")
        
        if transform_type == "uppercase":
            result = text.upper()
        elif transform_type == "lowercase":
            result = text.lower()
        elif transform_type == "title":
            result = text.title()
        elif transform_type == "clean":
            import re
            result = re.sub(r'\s+', ' ', text).strip()
        elif transform_type == "extract_links":
            urls = extract_urls(text)
            result = '\n'.join(urls)
        else:
            result = text
        
        return {"transformed_text": result}

class FlowCommandManager:
    
    def __init__(self, flows_dir: str = None):
        if flows_dir is None:
            flows_dir = os.path.join(os.path.expanduser("~"), ".stalker", "flows")
        
        self.flows_dir = flows_dir
        self.flows: Dict[str, FlowCommand] = {}
        self.executor = FlowCommandExecutor()
        
        os.makedirs(self.flows_dir, exist_ok=True)
        
        self._register_builtin_flows()
        
        self._load_flows()
    
    def _register_builtin_flows(self):
        
        copy_path = FlowCommand(
            name="copy_current_path",
            description="Copiar ruta del archivo/carpeta actual",
            app_context="explorer"
        )
        copy_path.steps = [
            FlowStep("keystroke", {"keys": "alt+d"}),  # Focus address bar
            FlowStep("wait", {"duration": 0.2}),
            FlowStep("keystroke", {"keys": "ctrl+c"}),  # Copy
            FlowStep("wait", {"duration": 0.1}),
            FlowStep("keystroke", {"keys": "escape"}),  # Close address bar
        ]
        self.flows["copy_current_path"] = copy_path
        
        terminal_here = FlowCommand(
            name="open_terminal_here",
            description="Abrir terminal en carpeta actual",
            app_context="explorer"
        )
        terminal_here.steps = [
            FlowStep("keystroke", {"keys": "alt+d"}),
            FlowStep("wait", {"duration": 0.2}),
            FlowStep("clipboard", {"operation": "get"}),
            FlowStep("command", {"command": "cmd /k cd /d ${clipboard_content}"}),
        ]
        self.flows["open_terminal_here"] = terminal_here
        
        extract_links = FlowCommand(
            name="extract_links",
            description="Extraer todos los enlaces de la página",
            app_context="browser"
        )
        extract_links.steps = [
            FlowStep("clipboard", {"operation": "get"}),
            FlowStep("transform", {"type": "extract_links"}),
            FlowStep("copy", {"text": "${transformed_text}"}),
        ]
        self.flows["extract_links"] = extract_links
        
        clean_paste = FlowCommand(
            name="clean_and_paste",
            description="Limpiar formato y pegar",
            app_context="any"
        )
        clean_paste.steps = [
            FlowStep("clipboard", {"operation": "get"}),
            FlowStep("transform", {"type": "clean"}),
            FlowStep("paste", {"text": "${transformed_text}"}),
        ]
        self.flows["clean_and_paste"] = clean_paste
    
    def _load_flows(self):
        if not os.path.exists(self.flows_dir):
            return
        
        for filename in os.listdir(self.flows_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.flows_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        flow = FlowCommand.from_dict(data)
                        self.flows[flow.name] = flow
                except Exception as e:
                    print(f"Error loading flow {filename}: {e}")
    
    def save_flow(self, flow: FlowCommand):
        filepath = os.path.join(self.flows_dir, f"{flow.name}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(flow.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving flow {flow.name}: {e}")
    
    def get_flow(self, name: str) -> Optional[FlowCommand]:
        return self.flows.get(name)
    
    def execute_flow(self, name: str, context: Dict[str, Any] = None) -> bool:
        flow = self.get_flow(name)
        if flow:
            return self.executor.execute(flow, context)
        return False
    
    def create_flow(self, name: str, description: str, app_context: str = "any") -> FlowCommand:
        flow = FlowCommand(name=name, description=description, app_context=app_context)
        self.flows[name] = flow
        self.save_flow(flow)
        return flow
    
    def add_step_to_flow(self, flow_name: str, step: FlowStep):
        flow = self.get_flow(flow_name)
        if flow:
            flow.steps.append(step)
            self.save_flow(flow)
    
    def get_flows_for_app(self, app_context: str) -> List[FlowCommand]:
        return [f for f in self.flows.values() if f.app_context == app_context or f.app_context == "any"]




import json
import copy
import sys
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_PATH = Path.home() / ".fastlauncher" / "config.json"


def _get_bundled_config_path() -> Path:
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent.parent
    
    return bundle_dir / "config.default.json"


def _copy_default_config_on_first_run():
    if CONFIG_PATH.exists():
        return  # Config already exists
    
    default_config_path = _get_bundled_config_path()
    
    if default_config_path.exists():
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(default_config_path, CONFIG_PATH)
            print(f"First run: Copied default config to {CONFIG_PATH}")
        except Exception as e:
            print(f"Warning: Could not copy default config: {e}")
    else:
        print(f"Warning: Default config not found at {default_config_path}")

_DEFAULTS: Dict[str, Any] = {
    "ui": {
        "font_family": "Segoe UI",
        "font_size": 11,
        "theme": "dark",  # dark|light
        "opacity_active": 0.98,
        "opacity_inactive": 0.6,
        "accent": "#3a86ff",
        "effects": True,
    },
    "hotkey": "ctrl+space",
    "modules": {
        "optimizer": True,
        "clipboard": True,
        "snippets": True,
        "ai": True,
        "files": True,
        "links": True,
        "macros": True,
    },
    "performance_mode": False,
    "plugin_shell": {"enabled": True},
    "file_indexer": {
        "roots": [],  # Empty means use home directory as default
        "watch_enabled": False,  # Optional watchdog feature
    },
    "syshealth": {
        "sampling_interval": 2.0,  # Seconds between samples (low overhead)
        "process_refresh_interval": 3.0,  # Seconds between process list updates
        "process_limit": 15,  # Max processes to display
        "confirm_kill": True,  # Ask for confirmation before killing process
        "overlay_enabled": False,  # Show persistent system health overlay
        "overlay_update_interval": 5.0,  # Seconds between overlay updates
        "overlay_position": "top-right",  # Position of overlay: top-left, top-right, bottom-left, bottom-right
    },
}


def _validate_ui_config(ui_config: Dict[str, Any]) -> Dict[str, Any]:
    validated = {}
    
    validated["font_family"] = str(ui_config.get("font_family", _DEFAULTS["ui"]["font_family"]))
    
    try:
        font_size = int(ui_config.get("font_size", _DEFAULTS["ui"]["font_size"]))
        validated["font_size"] = max(8, min(24, font_size))
    except (ValueError, TypeError):
        validated["font_size"] = _DEFAULTS["ui"]["font_size"]
    
    theme = ui_config.get("theme", _DEFAULTS["ui"]["theme"])
    validated["theme"] = theme if theme in ("dark", "light") else _DEFAULTS["ui"]["theme"]
    
    for key in ("opacity_active", "opacity_inactive"):
        try:
            opacity = float(ui_config.get(key, _DEFAULTS["ui"][key]))
            validated[key] = max(0.0, min(1.0, opacity))
        except (ValueError, TypeError):
            validated[key] = _DEFAULTS["ui"][key]
    
    accent = ui_config.get("accent", _DEFAULTS["ui"]["accent"])
    if isinstance(accent, str) and accent.startswith("#") and len(accent) in (4, 7):
        validated["accent"] = accent
    else:
        validated["accent"] = _DEFAULTS["ui"]["accent"]
    
    validated["effects"] = bool(ui_config.get("effects", _DEFAULTS["ui"]["effects"]))
    
    return validated


def _validate_hotkey(hotkey: Any) -> str:
    if not isinstance(hotkey, str):
        return _DEFAULTS["hotkey"]
    
    hotkey = hotkey.strip().lower()
    if not hotkey or "+" not in hotkey:
        return _DEFAULTS["hotkey"]
    
    return hotkey


def _validate_modules(modules: Any) -> Dict[str, bool]:
    if not isinstance(modules, dict):
        return copy.deepcopy(_DEFAULTS["modules"])
    
    validated = {}
    for key in _DEFAULTS["modules"].keys():
        validated[key] = bool(modules.get(key, _DEFAULTS["modules"][key]))
    
    return validated


def _deep_merge(base: Dict, override: Dict) -> Dict:
    result = copy.deepcopy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


class ConfigManager:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = path
        self.data = copy.deepcopy(_DEFAULTS)
        _copy_default_config_on_first_run()
        self._ensure_config_dir()
        self.load()

    def _ensure_config_dir(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create config directory: {e}")

    def load(self):
        if not self.path.exists():
            self.save()
            return
        
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            if not isinstance(loaded_data, dict):
                raise ValueError("Config file must contain a JSON object")
            
            merged = _deep_merge(_DEFAULTS, loaded_data)
            
            merged["ui"] = _validate_ui_config(merged.get("ui", {}))
            merged["hotkey"] = _validate_hotkey(merged.get("hotkey"))
            merged["modules"] = _validate_modules(merged.get("modules"))
            merged["performance_mode"] = bool(merged.get("performance_mode", False))
            
            self.data = merged
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            print("Using default configuration")
            self.data = copy.deepcopy(_DEFAULTS)
            self._backup_and_save()
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            self.data = copy.deepcopy(_DEFAULTS)
            self._backup_and_save()

    def save(self):
        try:
            self._ensure_config_dir()
            self.data["ui"] = _validate_ui_config(self.data.get("ui", {}))
            self.data["hotkey"] = _validate_hotkey(self.data.get("hotkey"))
            self.data["modules"] = _validate_modules(self.data.get("modules"))
            
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _backup_and_save(self):
        try:
            if self.path.exists():
                backup_path = self.path.with_suffix(".json.backup")
                self.path.rename(backup_path)
                print(f"Backed up corrupted config to {backup_path}")
        except Exception as e:
            print(f"Could not backup config: {e}")
        
        self.save()

    def export(self, dest: Path):
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            return dest
        except Exception as e:
            print(f"Error exporting config: {e}")
            return None

    def import_file(self, src: Path):
        try:
            if not src.exists():
                raise FileNotFoundError(f"Config file not found: {src}")
            
            with open(src, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            if not isinstance(loaded_data, dict):
                raise ValueError("Config file must contain a JSON object")
            
            merged = _deep_merge(_DEFAULTS, loaded_data)
            merged["ui"] = _validate_ui_config(merged.get("ui", {}))
            merged["hotkey"] = _validate_hotkey(merged.get("hotkey"))
            merged["modules"] = _validate_modules(merged.get("modules"))
            
            self.data = merged
            self.save()
        except Exception as e:
            print(f"Error importing config: {e}")
            raise

    def toggle_performance_mode(self, value: bool):
        self.data["performance_mode"] = bool(value)
        self.save()

    def set_module_enabled(self, module: str, enabled: bool):
        if "modules" not in self.data:
            self.data["modules"] = copy.deepcopy(_DEFAULTS["modules"])
        
        if module in _DEFAULTS["modules"]:
            self.data["modules"][module] = bool(enabled)
            self.save()

    def set_ui(self, **kwargs):
        if "ui" not in self.data:
            self.data["ui"] = copy.deepcopy(_DEFAULTS["ui"])
        
        self.data["ui"].update(kwargs)
        self.data["ui"] = _validate_ui_config(self.data["ui"])
        self.save()

    def set_hotkey(self, hotkey: str):
        validated = _validate_hotkey(hotkey)
        self.data["hotkey"] = validated
        self.save()
        return validated

    def get_ui(self, key: Optional[str] = None) -> Any:
        if key is None:
            return self.data.get("ui", copy.deepcopy(_DEFAULTS["ui"]))
        return self.data.get("ui", {}).get(key, _DEFAULTS["ui"].get(key))

    def get_performance_mode(self) -> bool:
        return bool(self.data.get("performance_mode", False))

    def get_module_enabled(self, module: str) -> bool:
        return bool(self.data.get("modules", {}).get(module, _DEFAULTS["modules"].get(module, False)))

    def get_file_indexer_roots(self):
        file_indexer = self.data.get("file_indexer", _DEFAULTS.get("file_indexer", {}))
        return file_indexer.get("roots", [])

    def set_file_indexer_roots(self, roots: list):
        if "file_indexer" not in self.data:
            self.data["file_indexer"] = copy.deepcopy(_DEFAULTS["file_indexer"])
        self.data["file_indexer"]["roots"] = roots
        self.save()

    def get_file_indexer_watch_enabled(self) -> bool:
        file_indexer = self.data.get("file_indexer", _DEFAULTS.get("file_indexer", {}))
        return bool(file_indexer.get("watch_enabled", False))

    def set_file_indexer_watch_enabled(self, enabled: bool):
        if "file_indexer" not in self.data:
            self.data["file_indexer"] = copy.deepcopy(_DEFAULTS["file_indexer"])
        self.data["file_indexer"]["watch_enabled"] = bool(enabled)
        self.save()

    def get_syshealth_config(self, key: Optional[str] = None) -> Any:
        default_config = _DEFAULTS.get("syshealth", {})
        syshealth_config = self.data.get("syshealth", default_config)
        if key is None:
            return syshealth_config
        return syshealth_config.get(key, default_config.get(key))

    def set_syshealth_config(self, **kwargs):
        if "syshealth" not in self.data:
            self.data["syshealth"] = copy.deepcopy(_DEFAULTS["syshealth"])
        self.data["syshealth"].update(kwargs)
        self.save()



import subprocess
import win32clipboard
from typing import List, Optional
from modules_system import Calculator
from modules_system import ClipboardManager
from modules_system import SnippetManager
from modules_files import AppLauncher
from modules_files import FileIndexer
from modules_files import Quicklinks
from modules_automation import MacroRecorder
from modules_monitoring import SysHealth
from modules_ai import AIAssistant
from modules_ai import NotesManager
from modules_system import PluginShell
from modules_system import log
from modules_automation import ContextualActionsManager
from modules_system import get_active_window_info, detect_app_context

class SearchEngine:
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
        perf = self.config.get_performance_mode()

        self.calculator = Calculator()
        self.clipboard_mgr = ClipboardManager() if self.config.get_module_enabled("clipboard") else None
        self.snippet_mgr = SnippetManager() if self.config.get_module_enabled("snippets") else None
        self.app_launcher = AppLauncher()
        self.file_indexer = FileIndexer(config=self.config) if self.config.get_module_enabled("files") else None
        if self.file_indexer and perf:
            self.file_indexer.pause(True)
        self.quicklinks = Quicklinks() if self.config.get_module_enabled("links") else None
        self.macro_recorder = MacroRecorder() if self.config.get_module_enabled("macros") else None
        self.syshealth = SysHealth(config=self.config) if self.config.get_module_enabled("optimizer") else None
        if self.syshealth:
            self.syshealth.start_background_refresh()
        self.ai = AIAssistant() if self.config.get_module_enabled("ai") and not perf else None
        self.notes = NotesManager()
        self.plugin_shell = PluginShell()
        
        self.intent_router = IntentRouter()
        self.compound_actions = CompoundActionManager()
        self.context_profiles = ContextProfileManager()
        self.flow_commands = FlowCommandManager()
        self.contextual_actions = ContextualActionsManager()
        
        self._ai_response_panel = None

        if self.file_indexer and not perf:
            self.file_indexer.start()

        self.internal_commands = [
            SearchResult("/clipboard", "Historial de portapapeles", group="command"),
            SearchResult("/snippets", "Gestionar snippets", group="command"),
            SearchResult("/files", "Buscar en índice de archivos", group="command"),
            SearchResult("/links", "Accesos directos personalizados", group="command"),
            SearchResult("/macros", "Macros grabadas", group="command"),
            SearchResult("/syshealth", "Monitor de sistema y procesos", group="command"),
            SearchResult("/overlay", "Toggle system health overlay", group="command"),
            SearchResult("/ai", "Asistente de IA (cloud/local) o '>'", group="command"),
            SearchResult("/notes", "Notas markdown seguras", group="command"),
            SearchResult("/context", "Acciones contextuales para app activa", group="command"),
            SearchResult("/actions", "Acciones rápidas sobre portapapeles", group="command"),
            SearchResult(">config", "Panel de configuración profunda", group="command"),
        ]
    
    def _get_ai_panel(self):
        if self._ai_response_panel is None:
            from ui import AIResponsePanel
            self._ai_response_panel = AIResponsePanel()
            self._ai_response_panel.insert_to_note_signal.connect(self._create_note_from_text)
        return self._ai_response_panel
    
    def _create_note_from_text(self, text: str):
        title = text[:50] if len(text) > 50 else text
        if '\n' in title:
            title = title.split('\n')[0]
        self.notes.create(title=title.strip() or "Nota de IA", body=text, tags="ia")
        log(f"Note created from AI response: {title}")
    
    def _insert_clipboard_to_note(self):
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData()
        except Exception as ex:
            log(f"Error reading clipboard: {ex}")
            return
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        
        if not text or not text.strip():
            log("Clipboard is empty, cannot create note")
            return
        
        title = text[:50] if len(text) > 50 else text
        if '\n' in title:
            title = title.split('\n')[0]
        self.notes.create(title=title.strip() or "Nota desde portapapeles", body=text, tags="clipboard")
        log(f"Note created from clipboard: {title}")

    def search(self, query: str) -> List[SearchResult]:
        text = query.strip()
        qlow = text.lower()
        results: List[SearchResult] = []

        if qlow.startswith(">config") or qlow.startswith("settings"):
            return self._config_results()

        perf = self.config.get_performance_mode()

        if (calc := self.calculator.try_calculate(text)):
            results.append(calc)

        if self.snippet_mgr and (text.startswith("@") or text.startswith(";")):
            sn = self.snippet_mgr.resolve_trigger(text)
            if sn:
                results.append(sn)

        is_ai = qlow.startswith("/ai") or qlow.startswith(">")
        is_notes = qlow.startswith("/notes")
        is_clip = qlow.startswith("/clipboard") or qlow.startswith("/clip")
        is_snip = qlow.startswith("/snippets") or qlow.startswith("/snippet")
        is_files = qlow.startswith("/files")
        is_links = qlow.startswith("/links") or qlow.startswith("/link")
        is_macro = qlow.startswith("/macros") or qlow.startswith("/macro")
        is_sys = qlow.startswith("/syshealth") or qlow.startswith("/sys")
        is_overlay = qlow.startswith("/overlay")
        is_context = qlow.startswith("/context")
        is_actions = qlow.startswith("/actions")

        if is_ai and self.ai:
            prompt = text[1:] if qlow.startswith(">") else text.replace("/ai", "").strip()
            if prompt:  # Only show if there's a prompt
                results.append(SearchResult(
                    title=f"Preguntar IA: {prompt[:64]}",
                    subtitle="Cloud/Local BYOK - Enter para ejecutar",
                    action=lambda p=prompt: self._show_ai_response(p),
                    group="ai",
                ))
        elif is_ai and perf:
            results.append(SearchResult(title="IA desactivada en Modo Ahorro", group="ai"))

        if is_notes:
            qnotes = text.replace("/notes", "").strip()
            for n in self.notes.search(qnotes, limit=30):
                results.append(SearchResult(title=n.title, subtitle=n.body[:80], copy_text=n.body, group="note"))
            results.append(SearchResult(title="Crear nota rápida", subtitle=qnotes or "Sin título",
                                        action=lambda t=qnotes: self.notes.create(t or "Sin título", "", ""), group="note"))
            results.append(SearchResult(
                title="📋 Insertar selección en nota",
                subtitle="Crear nota con el contenido del portapapeles",
                action=self._insert_clipboard_to_note,
                group="note"
            ))
        if is_clip and self.clipboard_mgr:
            results += self._clipboard_results(text.replace("/clipboard", "").replace("/clip", "").strip())
        if is_snip and self.snippet_mgr:
            results += self.snippet_mgr.search(text.replace("/snippets", "").replace("/snippet", "").strip(), limit=30)
        if is_files and self.file_indexer:
            results += self._file_results(text.replace("/files", "").strip())
        if is_links and self.quicklinks:
            results += self.quicklinks.search(text.replace("/links", "").replace("/link", "").strip(), limit=50)
        if is_macro and self.macro_recorder:
            results += self.macro_recorder.search_macros(text.replace("/macros", "").replace("/macro", "").strip(), limit=30)
        if is_sys and self.syshealth:
            qsys = text.replace("/syshealth", "").replace("/sys", "").strip()
            results += self._syshealth_results(qsys)
        if is_overlay:
            results.append(SearchResult(
                title="Toggle System Health Overlay",
                subtitle="Show/hide persistent CPU/RAM/Disk/Net monitor",
                action=self._toggle_overlay,
                group="command",
            ))
        
        if is_context:
            results += self._context_results()
        
        if is_actions:
            qactions = text.replace("/actions", "").strip()
            results += self.contextual_actions.get_available_actions(qactions)

        if not any([is_ai, is_notes, is_clip, is_snip, is_files, is_links, is_macro, is_sys, is_overlay, is_context, is_actions]):
            if text and len(text) > 2:
                intent = self.intent_router.detect_intent(text)
                if intent.confidence > 0.7:
                    results += self._intent_suggestions(intent)

        if not any([is_ai, is_notes, is_clip, is_snip, is_files, is_links, is_macro, is_sys, is_overlay, is_context, is_actions]):
            results += [r for r in self.internal_commands if qlow in r.title.lower()]
            
            if self.app_launcher and text:
                app_result = self.app_launcher.resolve(text)
                if app_result:
                    results.append(app_result)
                else:
                    app_results = self.app_launcher.search(text)
                    results.extend(app_results)
        
        return self._apply_scoring(results, query)

    def _config_results(self):
        return [
            SearchResult(
                "Abrir Panel de Configuración",
                "Gestiona hotkey, tema, módulos, rendimiento y más",
                action=self._open_settings_panel,
                group="config"
            ),
        ]
    
    def _open_settings_panel(self):
        from ui import SettingsPanel
        
        if not hasattr(self, '_settings_panel'):
            app_ref = getattr(self, '_app_ref', None)
            self._settings_panel = SettingsPanel(config=self.config, app_ref=app_ref)
        
        self._settings_panel.show()
        self._settings_panel.raise_()
        self._settings_panel.activateWindow()
        log("Settings panel opened")
    
    def _show_ai_response(self, prompt: str):
        if not self.ai:
            return
        
        response, success = self.ai.ask(prompt)
        
        panel = self._get_ai_panel()
        panel.show_response(response, is_error=not success)
        
        log(f"AI query: {prompt[:100]} | Success: {success}")

    def _toggle_perf(self):
        new_val = not self.config.get_performance_mode()
        self.config.toggle_performance_mode(new_val)
        
        if new_val:
            if self.file_indexer:
                self.file_indexer.pause(True)
            if self.ai:
                self.ai = None
            log("performance_mode=ON (indexer paused, AI disabled)")
        else:
            if self.file_indexer:
                self.file_indexer.pause(False)
                self.file_indexer.start()
            if self.config.get_module_enabled("ai") and not self.ai:
                self.ai = AIAssistant()
            log("performance_mode=OFF (indexer resumed, AI enabled)")

    def _toggle_module(self, key: str, val: bool):
        self.config.set_module_enabled(key, val)
        log(f"module {key} => {val}")

    def _export_config(self):
        from pathlib import Path
        dest = Path.home() / ".fastlauncher" / "config.export.json"
        self.config.export(dest)
        log(f"config export {dest}")

    def _import_config(self):
        from pathlib import Path
        src = Path.home() / ".fastlauncher" / "config.import.json"
        if src.exists():
            self.config.import_file(src)
            log(f"config import {src}")

    def _restart_services(self):
        if self.file_indexer and not self.config.get_performance_mode():
            self.file_indexer.start()
        log("Servicios reiniciados")

    def _clipboard_results(self, q: str):
        rows = self.clipboard_mgr.search(q=q, limit=40)
        out = []
        for row in rows:
            kind = row["kind"]
            content = row["content"]
            display = content if kind == "image" else content.decode("utf-8", errors="ignore")
            title = display if len(display) < 80 else display[:77] + "..."
            out.append(SearchResult(title=title, subtitle=f"Clipboard • {kind}", copy_text=display, group="clipboard"))
        return out

    def _file_results(self, q: str):
        rows = self.file_indexer.search(q=q, limit=60)
        results = []
        for r in rows:
            file_path = r["path"]
            result = SearchResult(
                title=r["name"], 
                subtitle=f"{r['drive']} • {file_path}", 
                copy_text=file_path, 
                group="file",
                meta={
                    "path": file_path,
                    "open_folder_action": lambda p=file_path: self._open_containing_folder(p),
                    "copy_path_action": lambda p=file_path: self._copy_path_to_clipboard(p),
                }
            )
            results.append(result)
        return results

    def _open_containing_folder(self, file_path: str):
        try:
            subprocess.Popen(['explorer', '/select,', file_path])
            log(f"Opened folder for: {file_path}")
        except Exception as e:
            log(f"Error opening folder for {file_path}: {e}")

    def _copy_path_to_clipboard(self, path: str):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(path)
            win32clipboard.CloseClipboard()
            log(f"Copied path to clipboard: {path}")
        except Exception as e:
            log(f"Error copying path to clipboard: {e}")

    def _syshealth_results(self, query: str = ""):
        results = []
        
        snap = self.syshealth.snapshot()
        header = SearchResult(
            title=f"CPU {snap.cpu_percent:.0f}% | RAM {snap.ram_used_gb:.1f}/{snap.ram_total_gb:.1f} GB | "
                  f"Disk {snap.disk_read_mb_s:.1f}R/{snap.disk_write_mb_s:.1f}W | "
                  f"Net {snap.net_down_mb_s:.1f}↓/{snap.net_up_mb_s:.1f}↑ MB/s",
            subtitle="Monitor en tiempo real • Ctrl+W para terminar proceso",
            group="syshealth",
        )
        results.append(header)
        
        qlow = query.lower()
        
        tools = []
        if not qlow or "task" in qlow or "admin" in qlow:
            tools.append(SearchResult(
                title="🖥️ Task Manager",
                subtitle="Administrador de tareas de Windows",
                action=lambda: self._show_tool_feedback(self.syshealth.open_task_manager()),
                group="syshealth",
            ))
        
        if not qlow or "startup" in qlow or "inicio" in qlow:
            tools.append(SearchResult(
                title="🚀 Startup Apps",
                subtitle="Aplicaciones de inicio de Windows",
                action=lambda: self._show_tool_feedback(self.syshealth.open_startup_apps()),
                group="syshealth",
            ))
        
        if not qlow or "defrag" in qlow or "disco" in qlow:
            tools.append(SearchResult(
                title="💿 Defragmentador de Disco",
                subtitle="Optimizar y desfragmentar unidades",
                action=lambda: self._show_tool_feedback(self.syshealth.open_defragmenter()),
                group="syshealth",
            ))
        
        if not qlow or "resource" in qlow or "monitor" in qlow:
            tools.append(SearchResult(
                title="📊 Monitor de Recursos",
                subtitle="Monitor detallado de recursos del sistema",
                action=lambda: self._show_tool_feedback(self.syshealth.open_resource_monitor()),
                group="syshealth",
            ))
        
        if not qlow or "info" in qlow or "system" in qlow:
            tools.append(SearchResult(
                title="ℹ️ Información del Sistema",
                subtitle="Información detallada del hardware y software",
                action=lambda: self._show_tool_feedback(self.syshealth.open_system_info()),
                group="syshealth",
            ))
        
        results.extend(tools)
        
        sort_by = "ram" if "ram" in qlow or "memoria" in qlow else "cpu"
        limit = self.config.get_syshealth_config("process_limit") if self.config else 15
        procs = self.syshealth.top_procs(by=sort_by, limit=limit, use_cache=True)
        
        for proc in procs:
            results.append(SearchResult(
                title=f"{proc.name} (PID {proc.pid})",
                subtitle=f"CPU {proc.cpu:.1f}% • RAM {proc.ram_mb:.0f} MB • {proc.username}",
                action=lambda p=proc.pid: self._kill_process_with_confirmation(p),
                group="process",
                meta={"pid": proc.pid, "name": proc.name},
            ))
        
        return results
    
    def _show_tool_feedback(self, result: tuple):
        success, message = result
        from modules_system import log
        if success:
            log(f"✓ {message}")
        else:
            log(f"✗ {message}")
    
    def _kill_process_with_confirmation(self, pid: int):
        from modules_system import log
        log(f"Use Ctrl+W para terminar proceso con PID {pid}")
    
    def _toggle_overlay(self):
        if hasattr(self, '_app_ref') and self._app_ref:
            self._app_ref.toggle_syshealth_overlay()
        from modules_system import log
        log("Toggling system health overlay")
    
    def _context_results(self) -> List[SearchResult]:
        results = []
        
        app_context = detect_app_context()
        window_info = get_active_window_info()
        
        app_name = app_context or window_info.get("process", "Unknown")
        results.append(SearchResult(
            title=f"🎯 Contexto: {app_name}",
            subtitle=f"Ventana activa: {window_info.get('title', '')[:60]}",
            group="context"
        ))
        
        profile = None
        if app_context:
            profile = self.context_profiles.get_profile(app_context)
        
        if not profile:
            profile = self.context_profiles.get_profile_for_window(
                window_info.get("title", ""),
                window_info.get("class", "")
            )
        
        if profile:
            results += self.context_profiles.get_actions_for_profile(profile)
            results += self.context_profiles.get_snippets_for_profile(profile)
        
        if app_context:
            flows = self.flow_commands.get_flows_for_app(app_context)
            for flow in flows:
                results.append(SearchResult(
                    title=f"⚡ {flow.name}",
                    subtitle=flow.description,
                    action=lambda f=flow.name: self.flow_commands.execute_flow(f),
                    group="flow"
                ))
        
        results += self.contextual_actions.get_available_actions()
        
        return results
    
    def _intent_suggestions(self, intent) -> List[SearchResult]:
        results = []
        
        if intent.type == IntentType.SEARCH_FILE:
            results.append(SearchResult(
                title="🔍 Buscar archivo y abrir carpeta",
                subtitle="Buscar el archivo y abrir su ubicación",
                group="intent"
            ))
        
        elif intent.type == IntentType.FILE_ACTION:
            action = intent.params.get("action", "")
            if action in ["zip", "compress"]:
                results.append(SearchResult(
                    title="🗜️ Comprimir y Compartir",
                    subtitle="Crear ZIP y copiar ruta al portapapeles",
                    group="intent"
                ))
        
        elif intent.type == IntentType.TEXT_TRANSFORM:
            transform = intent.params.get("transform", "")
            results.append(SearchResult(
                title=f"🔄 Transformar y Pegar ({transform})",
                subtitle="Aplicar transformación y pegar resultado",
                group="intent"
            ))
        
        elif intent.type == IntentType.TRANSLATE:
            results.append(SearchResult(
                title="🌐 Traducir y Pegar",
                subtitle="Traducir texto y pegar resultado",
                action=lambda: self.compound_actions._execute_translate_and_paste(),
                group="intent"
            ))
        
        return results

    def _apply_scoring(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        group_weights = {
            "calculator": 100,  # Highest priority
            "app": 90,
            "context": 88,  # High priority for context actions
            "compound": 87,
            "intent": 86,
            "flow": 85,
            "ai": 85,
            "clipboard": 80,
            "snippet": 75,
            "note": 70,
            "quicklink": 65,
            "file": 60,
            "command": 50,
            "macro": 45,
            "syshealth": 40,
            "general": 30,
        }
        
        query_lower = query.lower()
        
        for result in results:
            base_score = group_weights.get(result.group, 30)
            
            title_lower = result.title.lower()
            if title_lower == query_lower:
                base_score += 50  # Exact match
            elif title_lower.startswith(query_lower):
                base_score += 30  # Prefix match
            elif query_lower in title_lower:
                base_score += 10  # Contains match
            
            result.score = base_score
        
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results



from PySide6.QtCore import QTimer, Signal, QObject

class PredictiveSearch(QObject):
    results_ready = Signal(list)

    def __init__(self, debounce_ms=300, config=None):
        super().__init__()
        self.debounce_ms = debounce_ms
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._emit_results)
        self._pending_query = ""
        self.engine = SearchEngine(config=config)

    def query(self, text: str):
        self._pending_query = text
        self._timer.start(self.debounce_ms)

    def _emit_results(self):
        results = self.engine.search(self._pending_query)
        self.results_ready.emit(results)



from PySide6.QtGui import QPalette, QColor, QIcon, QAction
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from ui import LauncherWindow
from services import ensure_autostart
from typing import Optional

class LauncherApp:
    def __init__(self, qt_app):
        self.qt_app = qt_app
        self.config = ConfigManager()
        self.window = LauncherWindow(config=self.config, app_ref=self)
        
        hotkey = self.config.data.get("hotkey", "ctrl+space")
        self.hotkey = GlobalHotkey(self.toggle_visibility, hotkey=hotkey)
        
        self._syshealth_overlay: Optional[object] = None
        
        self._tray_icon: Optional[QSystemTrayIcon] = None
        self._init_system_tray()

    def start(self):
        theme = self.config.get_ui("theme")
        self._apply_theme(dark=(theme == "dark"))
        ensure_autostart()  # silently ensure autostart at logon
        self.hotkey.register()  # register global hotkey
        self.window.hide()      # start silent/minimized
        
        if self.config.get_syshealth_config("overlay_enabled"):
            self._init_syshealth_overlay()

    def toggle_visibility(self):
        if self.window.isVisible() and self.window.isActiveWindow():
            self.window.hide()
        else:
            self.window.center_and_show()
    
    def _init_syshealth_overlay(self):
        if not self.config.get_module_enabled("optimizer"):
            return
        
        if hasattr(self.window, 'search') and hasattr(self.window.search, 'engine'):
            syshealth = self.window.search.engine.syshealth
            if syshealth:
                from ui import SysHealthOverlay
                self._syshealth_overlay = SysHealthOverlay(syshealth, self.config)
                self._syshealth_overlay.show()
    
    def toggle_syshealth_overlay(self):
        if not self._syshealth_overlay:
            self._init_syshealth_overlay()
        
        if self._syshealth_overlay:
            self._syshealth_overlay.toggle_visibility()

    def _init_system_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self._tray_icon = QSystemTrayIcon(self.qt_app)
        
        icon = self.qt_app.style().standardIcon(self.qt_app.style().StandardPixmap.SP_ComputerIcon)
        self._tray_icon.setIcon(icon)
        self._tray_icon.setToolTip("Stalker - Fast Launcher")
        
        tray_menu = QMenu()
        
        show_action = QAction("Show Launcher", self.qt_app)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)
        
        settings_action = QAction("Settings", self.qt_app)
        settings_action.triggered.connect(self._open_settings_from_tray)
        tray_menu.addAction(settings_action)
        
        overlay_action = QAction("Toggle System Health Overlay", self.qt_app)
        overlay_action.triggered.connect(self.toggle_syshealth_overlay)
        tray_menu.addAction(overlay_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self.qt_app)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        self._tray_icon.setContextMenu(tray_menu)
        
        self._tray_icon.activated.connect(self._on_tray_activated)
        
        self._tray_icon.show()
    
    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visibility()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if not self.window.isVisible():
                self.window.center_and_show()
            else:
                self.window.raise_()
                self.window.activateWindow()
    
    def _open_settings_from_tray(self):
        self.window.center_and_show()
        self.window.query_edit.setText(">config")
        self.window.query_edit.returnPressed.emit()
    
    def quit_application(self):
        try:
            if self.hotkey:
                self.hotkey.unregister()
        except Exception as e:
            print(f"Error unregistering hotkey: {e}")
        
        try:
            if self._tray_icon:
                self._tray_icon.hide()
        except Exception as e:
            print(f"Error hiding tray icon: {e}")
        
        try:
            if self._syshealth_overlay:
                self._syshealth_overlay.close()
        except Exception as e:
            print(f"Error closing overlay: {e}")
        
        self.qt_app.quit()
    
    def _apply_theme(self, dark=True):
        palette = QPalette()
        
        accent_hex = self.config.get_ui("accent")
        accent = QColor(accent_hex)
        
        if dark:
            bg = QColor("#121212")
            fg = QColor("#eaeaea")
            panel = QColor("#1c1c1c")
        else:
            bg = QColor("#f5f7fb")
            fg = QColor("#0f172a")
            panel = QColor("#e2e8f0")

        palette.setColor(QPalette.Window, bg)
        palette.setColor(QPalette.WindowText, fg)
        palette.setColor(QPalette.Base, panel)
        palette.setColor(QPalette.AlternateBase, bg)
        palette.setColor(QPalette.Text, fg)
        palette.setColor(QPalette.Button, panel)
        palette.setColor(QPalette.ButtonText, fg)
        palette.setColor(QPalette.Highlight, accent)
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.qt_app.setPalette(palette)
        self.qt_app.setStyle("Fusion")


