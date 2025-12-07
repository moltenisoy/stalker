import subprocess
import win32clipboard
from dataclasses import dataclass
from typing import Callable, List, Optional
from core.config import ConfigManager
from modules.calculator import Calculator
from modules.clipboard_manager import ClipboardManager
from modules.snippet_manager import SnippetManager
from modules.app_launcher import AppLauncher
from modules.file_indexer import FileIndexer
from modules.quicklinks import Quicklinks
from modules.macro_recorder import MacroRecorder
from modules.syshealth import SysHealth
from modules.ai_assistant import AIAssistant
from modules.notes import NotesManager
from modules.plugin_shell import PluginShell
from modules.diagnostics import log

@dataclass
class SearchResult:
    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    copy_text: Optional[str] = None
    group: str = "general"
    meta: dict = None
    score: float = 0.0  # Higher score = higher priority

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
        
        # AI response panel (lazy initialization)
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
            SearchResult(">config", "Panel de configuración profunda", group="command"),
        ]
    
    def _get_ai_panel(self):
        """Lazy initialization of AI response panel."""
        if self._ai_response_panel is None:
            from ui.ai_response_panel import AIResponsePanel
            self._ai_response_panel = AIResponsePanel()
            # Connect signal to create note from AI response
            self._ai_response_panel.insert_to_note_signal.connect(self._create_note_from_text)
        return self._ai_response_panel
    
    def _create_note_from_text(self, text: str):
        """Create a new note from the given text."""
        title = text[:50] if len(text) > 50 else text
        if '\n' in title:
            title = title.split('\n')[0]
        self.notes.create(title=title.strip() or "Nota de IA", body=text, tags="ia")
        log(f"Note created from AI response: {title}")
    
    def _insert_clipboard_to_note(self):
        """Create a note from clipboard content."""
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
        
        # Create note from clipboard content
        title = text[:50] if len(text) > 50 else text
        if '\n' in title:
            title = title.split('\n')[0]
        self.notes.create(title=title.strip() or "Nota desde portapapeles", body=text, tags="clipboard")
        log(f"Note created from clipboard: {title}")

    def search(self, query: str) -> List[SearchResult]:
        text = query.strip()
        qlow = text.lower()
        results: List[SearchResult] = []

        # Config command
        if qlow.startswith(">config") or qlow.startswith("settings"):
            return self._config_results()

        # Performance mode note
        perf = self.config.get_performance_mode()

        # Calculator
        if (calc := self.calculator.try_calculate(text)):
            results.append(calc)

        # Snippet direct
        if self.snippet_mgr and (text.startswith("@") or text.startswith(";")):
            sn = self.snippet_mgr.resolve_trigger(text)
            if sn:
                results.append(sn)

        # Flags
        is_ai = qlow.startswith("/ai") or qlow.startswith(">")
        is_notes = qlow.startswith("/notes")
        is_clip = qlow.startswith("/clipboard") or qlow.startswith("/clip")
        is_snip = qlow.startswith("/snippets") or qlow.startswith("/snippet")
        is_files = qlow.startswith("/files")
        is_links = qlow.startswith("/links") or qlow.startswith("/link")
        is_macro = qlow.startswith("/macros") or qlow.startswith("/macro")
        is_sys = qlow.startswith("/syshealth") or qlow.startswith("/sys")
        is_overlay = qlow.startswith("/overlay")

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
            # Add option to insert clipboard content into a note
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

        # default search - search apps and other modules
        if not any([is_ai, is_notes, is_clip, is_snip, is_files, is_links, is_macro, is_sys, is_overlay]):
            # Add internal commands
            results += [r for r in self.internal_commands if qlow in r.title.lower()]
            
            # Search apps
            if self.app_launcher and text:
                # Check for direct alias match first
                app_result = self.app_launcher.resolve(text)
                if app_result:
                    results.append(app_result)
                else:
                    # Search in app database
                    app_results = self.app_launcher.search(text)
                    results.extend(app_results)
        
        # Apply scoring and sort by priority
        return self._apply_scoring(results, query)

    def _config_results(self):
        """Return result to open settings panel."""
        return [
            SearchResult(
                "Abrir Panel de Configuración",
                "Gestiona hotkey, tema, módulos, rendimiento y más",
                action=self._open_settings_panel,
                group="config"
            ),
        ]
    
    def _open_settings_panel(self):
        """Open the settings panel UI."""
        from ui.settings_panel import SettingsPanel
        
        # Create settings panel (we keep a reference to prevent garbage collection)
        if not hasattr(self, '_settings_panel'):
            # Try to get app reference from window if available
            app_ref = getattr(self, '_app_ref', None)
            self._settings_panel = SettingsPanel(config=self.config, app_ref=app_ref)
        
        # Show and raise the panel
        self._settings_panel.show()
        self._settings_panel.raise_()
        self._settings_panel.activateWindow()
        log("Settings panel opened")
    
    def _show_ai_response(self, prompt: str):
        """Execute AI query and show response in panel."""
        if not self.ai:
            return
        
        # Get AI response
        response, success = self.ai.ask(prompt)
        
        # Show in panel
        panel = self._get_ai_panel()
        panel.show_response(response, is_error=not success)
        
        # Log the interaction
        log(f"AI query: {prompt[:100]} | Success: {success}")

    def _toggle_perf(self):
        new_val = not self.config.get_performance_mode()
        self.config.toggle_performance_mode(new_val)
        
        # Synchronize performance mode across all components
        if new_val:
            # Enable performance mode: pause indexer, disable AI
            if self.file_indexer:
                self.file_indexer.pause(True)
            if self.ai:
                # Cleanup AI resources if available
                # Note: AIAssistant doesn't have explicit cleanup, but we clear the reference
                self.ai = None
            # Note: Visual effects are handled in UI layer via config
            log("performance_mode=ON (indexer paused, AI disabled)")
        else:
            # Disable performance mode: resume indexer, re-enable AI
            if self.file_indexer:
                self.file_indexer.pause(False)
                self.file_indexer.start()
            # Re-enable AI if module is enabled
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
        # Simple reinicio: re-lanzar indexador si aplica
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
            # Create result with actions for opening folder and copying path
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
        """Open the folder containing the specified file."""
        try:
            # Use explorer with /select to open and highlight the file
            subprocess.Popen(['explorer', '/select,', file_path])
            log(f"Opened folder for: {file_path}")
        except Exception as e:
            log(f"Error opening folder for {file_path}: {e}")

    def _copy_path_to_clipboard(self, path: str):
        """Copy the file path to clipboard."""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(path)
            win32clipboard.CloseClipboard()
            log(f"Copied path to clipboard: {path}")
        except Exception as e:
            log(f"Error copying path to clipboard: {e}")

    def _syshealth_results(self, query: str = ""):
        """Return syshealth results including system info, processes, and system tools."""
        results = []
        
        # System snapshot header
        snap = self.syshealth.snapshot()
        header = SearchResult(
            title=f"CPU {snap.cpu_percent:.0f}% | RAM {snap.ram_used_gb:.1f}/{snap.ram_total_gb:.1f} GB | "
                  f"Disk {snap.disk_read_mb_s:.1f}R/{snap.disk_write_mb_s:.1f}W | "
                  f"Net {snap.net_down_mb_s:.1f}↓/{snap.net_up_mb_s:.1f}↑ MB/s",
            subtitle="Monitor en tiempo real • Ctrl+W para terminar proceso",
            group="syshealth",
        )
        results.append(header)
        
        # System tool shortcuts
        qlow = query.lower()
        
        # Show system tools based on query or show all if no specific query
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
        
        # Top processes - determine sort order from query
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
        """Show feedback for system tool launch."""
        success, message = result
        from modules.diagnostics import log
        if success:
            log(f"✓ {message}")
        else:
            log(f"✗ {message}")
    
    def _kill_process_with_confirmation(self, pid: int):
        """Kill process with optional confirmation."""
        # This will be called from launcher which will handle confirmation
        # The actual kill is done in launcher.py with Ctrl+W
        from modules.diagnostics import log
        log(f"Use Ctrl+W para terminar proceso con PID {pid}")
    
    def _toggle_overlay(self):
        """Toggle system health overlay."""
        if hasattr(self, '_app_ref') and self._app_ref:
            self._app_ref.toggle_syshealth_overlay()
        from modules.diagnostics import log
        log("Toggling system health overlay")

    def _apply_scoring(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Apply scoring and prioritization to search results."""
        # Priority weights by group
        group_weights = {
            "calculator": 100,  # Highest priority
            "app": 90,
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
            # Base score from group
            base_score = group_weights.get(result.group, 30)
            
            # Bonus for exact or prefix matches
            title_lower = result.title.lower()
            if title_lower == query_lower:
                base_score += 50  # Exact match
            elif title_lower.startswith(query_lower):
                base_score += 30  # Prefix match
            elif query_lower in title_lower:
                base_score += 10  # Contains match
            
            result.score = base_score
        
        # Sort by score (descending)
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results