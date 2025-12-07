import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import time
import os
import base64

DB_PATH = Path.home() / ".fastlauncher" / "storage.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Key file for Fernet encryption (stored in %LOCALAPPDATA% / ~/.fastlauncher)
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
        """Initialize Fernet encryption for API keys."""
        try:
            from cryptography.fernet import Fernet
            
            # Create or load encryption key
            if KEY_FILE.exists():
                with open(KEY_FILE, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(KEY_FILE, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions on Unix-like systems
                if hasattr(os, 'chmod'):
                    os.chmod(KEY_FILE, 0o600)
            
            self._cipher = Fernet(key)
        except ImportError:
            # If cryptography is not available, disable encryption
            self.encrypt_keys = False
            self._cipher = None
        except Exception:
            # If encryption fails, disable it
            self.encrypt_keys = False
            self._cipher = None
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet."""
        if not self.encrypt_keys or not self._cipher:
            return data
        try:
            encrypted = self._cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception:
            return data
    
    def _decrypt_data(self, data: str) -> str:
        """Decrypt data using Fernet."""
        if not self.encrypt_keys or not self._cipher:
            return data
        try:
            encrypted = base64.b64decode(data.encode())
            decrypted = self._cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception:
            # Return as-is if decryption fails (might be unencrypted old data)
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
        """Store API key with optional encryption."""
        encrypted_key = self._encrypt_data(key)
        with self._conn() as conn:
            conn.execute("INSERT OR REPLACE INTO api_keys(provider, key, updated_at) VALUES (?, ?, ?)",
                         (provider, encrypted_key, time.time()))
            conn.commit()

    def get_api_key(self, provider: str):
        """Retrieve API key with optional decryption."""
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