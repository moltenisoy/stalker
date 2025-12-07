import os
import subprocess
from typing import List, Optional
from core.storage import Storage
from core.engine import SearchResult

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