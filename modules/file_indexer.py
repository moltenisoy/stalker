import os
import threading
import time
from pathlib import Path
from typing import Iterable, List, Optional
from core.storage import Storage
from core.config import ConfigManager
from modules.diagnostics import log

class FileIndexer:
    def __init__(self, storage: Storage | None = None, roots: Iterable[str] | None = None, config: ConfigManager | None = None):
        self.storage = storage or Storage()
        self.config = config or ConfigManager()
        
        # Load roots from config if not explicitly provided
        if roots is not None:
            self.roots = list(roots)
        else:
            config_roots = self.config.get_file_indexer_roots()
            self.roots = config_roots if config_roots else [str(Path.home())]
        
        self._thread = None
        self.paused = False
        self._watch_enabled = self.config.get_file_indexer_watch_enabled()
        self._observer = None
        self._stats = {"files_indexed": 0, "errors": 0, "last_run": None}

    def start(self):
        if self.paused:
            return
        if self._thread and self._thread.is_alive():
            return
        log("FileIndexer: Starting indexing thread")
        self._thread = threading.Thread(target=self._build_index, daemon=True)
        self._thread.start()
        
        # Start watchdog if enabled
        if self._watch_enabled:
            self._start_watchdog()

    def pause(self, value: bool = True):
        self.paused = value
        if value:
            log("FileIndexer: Paused")
            self._stop_watchdog()
        else:
            log("FileIndexer: Resumed")

    def _build_index(self):
        if self.paused:
            return
        
        log(f"FileIndexer: Building index for roots: {self.roots}")
        records = []
        now = time.time()
        self._stats["files_indexed"] = 0
        self._stats["errors"] = 0
        
        for root in self.roots:
            try:
                root_path = Path(root)
                if not root_path.exists():
                    log(f"FileIndexer: Root path does not exist: {root}")
                    continue
                
                drive = root_path.drive or str(root_path.anchor)
                log(f"FileIndexer: Scanning {root} (drive: {drive})")
                
                for dirpath, _, filenames in os.walk(root):
                    if self.paused:
                        log("FileIndexer: Indexing paused")
                        return
                    
                    for fname in filenames:
                        try:
                            full = Path(dirpath) / fname
                            records.append((str(full), drive, fname, now))
                            self._stats["files_indexed"] += 1
                        except Exception as e:
                            # Silent error for individual files
                            self._stats["errors"] += 1
                            
            except Exception as e:
                log(f"FileIndexer: Error scanning root {root}: {e}")
                self._stats["errors"] += 1
        
        if not self.paused:
            try:
                self.storage.replace_file_index(records)
                self._stats["last_run"] = time.time()
                log(f"FileIndexer: Completed. Indexed {self._stats['files_indexed']} files with {self._stats['errors']} errors")
            except Exception as e:
                log(f"FileIndexer: Error updating index: {e}")
                self._stats["errors"] += 1

    def set_roots(self, roots: List[str]):
        self.roots = roots
        # Persist to config
        self.config.set_file_indexer_roots(roots)
        log(f"FileIndexer: Roots updated to {roots}")
        if not self.paused:
            self.start()

    def add_root(self, root: str):
        """Add a new root to the indexer."""
        if root not in self.roots:
            self.roots.append(root)
            self.config.set_file_indexer_roots(self.roots)
            log(f"FileIndexer: Added root {root}")
            if not self.paused:
                self.start()

    def remove_root(self, root: str):
        """Remove a root from the indexer."""
        if root in self.roots:
            self.roots.remove(root)
            self.config.set_file_indexer_roots(self.roots)
            log(f"FileIndexer: Removed root {root}")
            if not self.paused:
                self.start()

    def search(self, q: str, limit: int = 80):
        if self.paused:
            return []
        return self.storage.list_files(q=q, limit=limit)

    def get_stats(self):
        """Get indexing statistics for diagnostics."""
        return self._stats.copy()

    def _start_watchdog(self):
        """Start watchdog observer for incremental indexing."""
        if self._observer is not None:
            return
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class IndexerEventHandler(FileSystemEventHandler):
                def __init__(self, indexer):
                    self.indexer = indexer
                
                def on_created(self, event):
                    if not event.is_directory:
                        # Could implement incremental update here
                        pass
                
                def on_deleted(self, event):
                    if not event.is_directory:
                        # Could implement incremental update here
                        pass
                
                def on_modified(self, event):
                    if not event.is_directory:
                        # Could implement incremental update here
                        pass
            
            self._observer = Observer()
            handler = IndexerEventHandler(self)
            
            for root in self.roots:
                if Path(root).exists():
                    self._observer.schedule(handler, root, recursive=True)
            
            self._observer.start()
            log("FileIndexer: Watchdog started")
        except Exception as e:
            log(f"FileIndexer: Could not start watchdog: {e}")
            self._observer = None

    def _stop_watchdog(self):
        """Stop watchdog observer."""
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join()
                self._observer = None
                log("FileIndexer: Watchdog stopped")
            except Exception as e:
                log(f"FileIndexer: Error stopping watchdog: {e}")