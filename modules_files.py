import os
import subprocess
from typing import List, Optional
from pathlib import Path
from core import Storage
from core import SearchResult

COMMON_APPS = {
    "cal": ("Calculadora", "calc.exe"),
    "calc": ("Calculadora", "calc.exe"),
    "notas": ("Bloc de notas", "notepad.exe"),
    "notepad": ("Bloc de notas", "notepad.exe"),
    "paint": ("Paint", "mspaint.exe"),
}

class AppLauncher:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()
        self._cache_loaded = False

    def resolve(self, text: str) -> Optional[SearchResult]:
        app = self.storage.get_app_by_alias(text)
        if not app and text in COMMON_APPS:
            name, path = COMMON_APPS[text]
            app = {"name": name, "path": path, "alias": text}
        if not app:
            return None
        return SearchResult(
            title=f"{app['name']}",
            subtitle=f"Ejecutar {app['path']}",
            action=lambda p=app["path"]: self.launch(p),
            group="app",
        )

    def search(self, q: str) -> List[SearchResult]:
        results = []
        for app in self.storage.list_apps(q=q):
            results.append(
                SearchResult(
                    title=app["name"],
                    subtitle=app["path"],
                    action=lambda p=app["path"]: self.launch(p),
                    group="app",
                )
            )
        for alias, (name, path) in COMMON_APPS.items():
            if q.lower() in alias.lower() or q.lower() in name.lower():
                results.append(SearchResult(title=name, subtitle=path, action=lambda p=path: self.launch(p), group="app"))
        return results

    def launch(self, path: str):
        try:
            subprocess.Popen(path if isinstance(path, list) else [path], shell=True)
        except FileNotFoundError:
            subprocess.Popen(['start', '', path], shell=True)

    def scan_installed_apps(self):
        log("AppLauncher: Starting app scan")
        
        self.storage.clear_app_cache()
        
        apps_found = []
        
        start_menu_paths = [
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        ]
        
        for start_menu in start_menu_paths:
            if start_menu.exists():
                apps_found.extend(self._scan_start_menu(start_menu))
        
        program_files_paths = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")),
        ]
        
        for program_files in program_files_paths:
            if program_files.exists():
                apps_found.extend(self._scan_program_files(program_files))
        
        for name, path in apps_found:
            try:
                self.storage.add_app(name, path)
            except Exception as e:
                log(f"AppLauncher: Error adding app {name}: {e}")
        
        self._cache_loaded = True
        log(f"AppLauncher: Scan complete. Found {len(apps_found)} apps")
        return len(apps_found)

    def _scan_start_menu(self, start_menu: Path):
        apps = []
        try:
            for lnk_file in start_menu.rglob("*.lnk"):
                try:
                    name = lnk_file.stem
                    apps.append((name, str(lnk_file)))
                except Exception as e:
                    log(f"AppLauncher: Error processing {lnk_file}: {e}")
        except Exception as e:
            log(f"AppLauncher: Error scanning Start Menu {start_menu}: {e}")
        return apps

    def _scan_program_files(self, program_files: Path):
        apps = []
        try:
            for app_dir in program_files.iterdir():
                if app_dir.is_dir():
                    try:
                        for exe_file in app_dir.glob("*.exe"):
                            name = exe_file.stem
                            apps.append((name, str(exe_file)))
                    except Exception as e:
                        log(f"AppLauncher: Error scanning {app_dir}: {e}")
        except Exception as e:
            log(f"AppLauncher: Error scanning Program Files {program_files}: {e}")
        return apps

    def add_alias(self, alias: str, name: str, path: str):
        try:
            self.storage.add_app(name, path, alias)
            log(f"AppLauncher: Added alias '{alias}' for {name}")
        except Exception as e:
            log(f"AppLauncher: Error adding alias: {e}")

    def ensure_cache_loaded(self):
        if not self._cache_loaded:
            apps = self.storage.list_apps(limit=1)
            if not apps:
                self.scan_installed_apps()
            else:
                self._cache_loaded = True



import os
import threading
import time
from pathlib import Path
from typing import Iterable, List, Optional
from core import Storage
from core import ConfigManager

class FileIndexer:
    def __init__(self, storage: Storage | None = None, roots: Iterable[str] | None = None, config: ConfigManager | None = None):
        self.storage = storage or Storage()
        self.config = config or ConfigManager()
        
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
        self.config.set_file_indexer_roots(roots)
        log(f"FileIndexer: Roots updated to {roots}")
        if not self.paused:
            self.start()

    def add_root(self, root: str):
        if root not in self.roots:
            self.roots.append(root)
            self.config.set_file_indexer_roots(self.roots)
            log(f"FileIndexer: Added root {root}")
            if not self.paused:
                self.start()

    def remove_root(self, root: str):
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
        return self._stats.copy()

    def _start_watchdog(self):
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
                        pass
                
                def on_deleted(self, event):
                    if not event.is_directory:
                        pass
                
                def on_modified(self, event):
                    if not event.is_directory:
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
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join()
                self._observer = None
                log("FileIndexer: Watchdog stopped")
            except Exception as e:
                log(f"FileIndexer: Error stopping watchdog: {e}")



import subprocess
from typing import List, Optional
from core import Storage
from core import SearchResult

class Quicklinks:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()

    def search(self, q: str, limit: int = 50) -> List[SearchResult]:
        results = []
        for link in self.storage.list_quicklinks(q=q, limit=limit):
            title = f"{link['name']} [{link['category']}]" if link["category"] else link["name"]
            subtitle = f"{link['target']} {link['args']}".strip()
            results.append(
                SearchResult(
                    title=title,
                    subtitle=subtitle,
                    action=lambda l=link: self.open_link(l),
                    group="quicklink",
                )
            )
        return results

    def open_link(self, link_row):
        kind = link_row["kind"]
        target = link_row["target"]
        args = link_row["args"] or ""
        if kind == "url":
            subprocess.Popen(["start", "", target], shell=True)
        elif kind == "folder":
            subprocess.Popen(["explorer", target])
        else:
            cmd = f"{target} {args}".strip()
            subprocess.Popen(cmd, shell=True)


