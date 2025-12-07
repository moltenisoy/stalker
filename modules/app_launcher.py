import os
import subprocess
from typing import List, Optional
from pathlib import Path
from core.storage import Storage
from core.types import SearchResult
from modules.diagnostics import log

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
        # alias directo
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
        # fallback alias predefinidos
        for alias, (name, path) in COMMON_APPS.items():
            if q.lower() in alias.lower() or q.lower() in name.lower():
                results.append(SearchResult(title=name, subtitle=path, action=lambda p=path: self.launch(p), group="app"))
        return results

    def launch(self, path: str):
        try:
            subprocess.Popen(path if isinstance(path, list) else [path], shell=True)
        except FileNotFoundError:
            # intentar start "" path
            subprocess.Popen(['start', '', path], shell=True)

    def scan_installed_apps(self):
        """Scan Start Menu and Program Files for installed applications."""
        log("AppLauncher: Starting app scan")
        
        # Clear existing cache (except aliased apps)
        self.storage.clear_app_cache()
        
        apps_found = []
        
        # Scan Start Menu
        start_menu_paths = [
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        ]
        
        for start_menu in start_menu_paths:
            if start_menu.exists():
                apps_found.extend(self._scan_start_menu(start_menu))
        
        # Scan Program Files
        program_files_paths = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")),
        ]
        
        for program_files in program_files_paths:
            if program_files.exists():
                apps_found.extend(self._scan_program_files(program_files))
        
        # Add to storage
        for name, path in apps_found:
            try:
                self.storage.add_app(name, path)
            except Exception as e:
                log(f"AppLauncher: Error adding app {name}: {e}")
        
        self._cache_loaded = True
        log(f"AppLauncher: Scan complete. Found {len(apps_found)} apps")
        return len(apps_found)

    def _scan_start_menu(self, start_menu: Path):
        """Scan Start Menu for .lnk files."""
        apps = []
        try:
            for lnk_file in start_menu.rglob("*.lnk"):
                try:
                    name = lnk_file.stem
                    # Use the .lnk file directly (Windows will resolve it)
                    apps.append((name, str(lnk_file)))
                except Exception as e:
                    log(f"AppLauncher: Error processing {lnk_file}: {e}")
        except Exception as e:
            log(f"AppLauncher: Error scanning Start Menu {start_menu}: {e}")
        return apps

    def _scan_program_files(self, program_files: Path):
        """Scan Program Files for .exe files."""
        apps = []
        try:
            # Only scan one level deep to avoid too many files
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
        """Add a persistent alias for an app."""
        try:
            self.storage.add_app(name, path, alias)
            log(f"AppLauncher: Added alias '{alias}' for {name}")
        except Exception as e:
            log(f"AppLauncher: Error adding alias: {e}")

    def ensure_cache_loaded(self):
        """Ensure app cache is loaded, scan if needed."""
        if not self._cache_loaded:
            # Check if we have apps in the database
            apps = self.storage.list_apps(limit=1)
            if not apps:
                # No apps, trigger a scan
                self.scan_installed_apps()
            else:
                self._cache_loaded = True