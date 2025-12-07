"""
Shell de extensiones (arquitectura simulada) separada de funciones críticas.
- Plugins declarados con manifest (Dart/JS simulado).
- Se cargan en proceso sandbox (aquí se simula con subprocess/comunicación JSON).
- Capacidades restringidas: lectura, quicklinks, AI proxy, etc.
"""
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
        # Aquí se simula la llamada; en producción se usaría IPC/HTTP hacia sandbox Dart/JS
        manifest = self.plugins[plugin_id]
        if action not in manifest.get("actions", []):
            raise ValueError("Acción no permitida por manifest")
        # Simulación de respuesta
        return {"plugin": plugin_id, "action": action, "ok": True, "payload": payload}