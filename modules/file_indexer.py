import os
import threading
import time
from pathlib import Path
from typing import Iterable, List
from core.storage import Storage

class FileIndexer:
    def __init__(self, storage: Storage | None = None, roots: Iterable[str] | None = None):
        self.storage = storage or Storage()
        self.roots = list(roots) if roots else [str(Path.home())]
        self._thread = None
        self.paused = False

    def start(self):
        if self.paused:
            return
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._build_index, daemon=True)
        self._thread.start()

    def pause(self, value: bool = True):
        self.paused = value

    def _build_index(self):
        if self.paused:
            return
        records = []
        now = time.time()
        for root in self.roots:
            root_path = Path(root)
            if not root_path.exists():
                continue
            drive = root_path.drive or str(root_path.anchor)
            for dirpath, _, filenames in os.walk(root):
                if self.paused:
                    return
                for fname in filenames:
                    full = Path(dirpath) / fname
                    records.append((str(full), drive, fname, now))
        if not self.paused:
            self.storage.replace_file_index(records)

    def set_roots(self, roots: List[str]):
        self.roots = roots
        if not self.paused:
            self.start()

    def search(self, q: str, limit: int = 80):
        if self.paused:
            return []
        return self.storage.list_files(q=q, limit=limit)