import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import time

DB_PATH = Path.home() / ".fastlauncher" / "storage.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class Storage:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self._init_db()

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
                id INTEGER PRIMARY KEY CHECK (id=1),
                provider TEXT NOT NULL,
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
        with self._conn() as conn:
            conn.execute("INSERT OR REPLACE INTO api_keys(id, provider, key, updated_at) VALUES (1, ?, ?, ?)",
                         (provider, key, time.time()))
            conn.commit()

    def get_api_key(self, provider: str):
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT key, provider FROM api_keys WHERE provider=?", (provider,)).fetchone()
        return row["key"] if row else None

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