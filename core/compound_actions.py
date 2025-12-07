"""
Compound Actions - Chain multiple actions together.
Allows users to perform complex workflows with a single command.
"""
import os
import zipfile
import shutil
import subprocess
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass
from core.engine import SearchResult

@dataclass
class ActionStep:
    """A single step in a compound action."""
    name: str
    description: str
    action: Callable
    params: Dict[str, Any] = None
    requires_confirmation: bool = False
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}

class CompoundAction:
    """Represents a multi-step compound action."""
    
    def __init__(self, name: str, description: str, steps: List[ActionStep]):
        self.name = name
        self.description = description
        self.steps = steps
        self.current_step = 0
    
    def execute_next(self) -> bool:
        """
        Execute the next step in the compound action.
        
        Returns:
            True if there are more steps, False if complete
        """
        if self.current_step >= len(self.steps):
            return False
        
        step = self.steps[self.current_step]
        if step.action:
            step.action(**step.params)
        self.current_step += 1
        
        return self.current_step < len(self.steps)
    
    def reset(self):
        """Reset to the first step."""
        self.current_step = 0
    
    def get_current_step(self) -> Optional[ActionStep]:
        """Get the current step."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

class CompoundActionManager:
    """
    Manages compound actions and provides common workflows.
    All actions run locally for speed and privacy.
    """
    
    def __init__(self):
        self._actions = {}
        self._register_builtin_actions()
    
    def _register_builtin_actions(self):
        """Register built-in compound actions."""
        # Zip and Share
        self.register_action(
            "zip_and_share",
            "Zip y Compartir",
            "Comprimir archivos y copiar ruta al portapapeles",
            [
                ActionStep("zip", "Comprimir archivos", self._zip_files),
                ActionStep("copy_path", "Copiar ruta", self._copy_path_to_clipboard),
            ]
        )
        
        # Copy path and open folder
        self.register_action(
            "copy_and_open",
            "Copiar Ruta y Abrir Carpeta",
            "Copiar ruta del archivo y abrir carpeta contenedora",
            [
                ActionStep("copy", "Copiar ruta", self._copy_path_to_clipboard),
                ActionStep("open", "Abrir carpeta", self._open_folder),
            ]
        )
        
        # Convert and paste
        self.register_action(
            "convert_and_paste",
            "Convertir y Pegar",
            "Convertir texto y pegar resultado",
            [
                ActionStep("convert", "Convertir", self._convert_text),
                ActionStep("paste", "Pegar", self._paste_text),
            ]
        )
        
        # Translate and paste
        self.register_action(
            "translate_and_paste",
            "Traducir y Pegar",
            "Traducir texto y pegar resultado",
            [
                ActionStep("translate", "Traducir", self._translate_text),
                ActionStep("paste", "Pegar", self._paste_text),
            ]
        )
        
        # Clean format and paste
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
        """Register a new compound action."""
        self._actions[action_id] = CompoundAction(name, description, steps)
    
    def get_action(self, action_id: str) -> Optional[CompoundAction]:
        """Get a compound action by ID."""
        return self._actions.get(action_id)
    
    def get_all_actions(self) -> Dict[str, CompoundAction]:
        """Get all registered compound actions."""
        return self._actions.copy()
    
    def suggest_actions_for_context(self, context: str, selected_item: Optional[Dict] = None) -> List[SearchResult]:
        """
        Suggest compound actions based on current context.
        
        Args:
            context: Current context (e.g., "file_selected", "text_copied")
            selected_item: Optional item information
            
        Returns:
            List of suggested compound actions as SearchResults
        """
        suggestions = []
        
        if context == "file_selected" and selected_item:
            # Suggest file-related compound actions
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
            # Suggest text-related compound actions
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
    
    # Helper methods for executing compound actions
    def _execute_zip_and_share(self, filepath: str):
        """Execute zip and share action."""
        action = self.get_action("zip_and_share")
        if action:
            action.reset()
            action.steps[0].params = {"filepath": filepath}
            action.steps[1].params = {"path": filepath + ".zip"}
            action.execute_next()
            action.execute_next()
    
    def _execute_copy_and_open(self, filepath: str):
        """Execute copy path and open folder action."""
        action = self.get_action("copy_and_open")
        if action:
            action.reset()
            action.steps[0].params = {"path": filepath}
            action.steps[1].params = {"path": os.path.dirname(filepath)}
            action.execute_next()
            action.execute_next()
    
    def _execute_translate_and_paste(self):
        """Execute translate and paste action."""
        action = self.get_action("translate_and_paste")
        if action:
            action.reset()
            action.execute_next()
            action.execute_next()
    
    def _execute_clean_and_paste(self):
        """Execute clean and paste action."""
        action = self.get_action("clean_and_paste")
        if action:
            action.reset()
            action.execute_next()
            action.execute_next()
    
    def _execute_convert_and_paste(self):
        """Execute convert and paste action."""
        action = self.get_action("convert_and_paste")
        if action:
            action.reset()
            action.execute_next()
            action.execute_next()
    
    # Individual action implementations
    def _zip_files(self, filepath: str, **kwargs):
        """Compress files into a zip archive."""
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
        """Copy path to clipboard."""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(path, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    
    def _open_folder(self, path: str, **kwargs):
        """Open folder in file explorer."""
        try:
            if os.path.isfile(path):
                folder = os.path.dirname(path)
            else:
                folder = path
            
            subprocess.run(['explorer', folder], shell=True)
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def _convert_text(self, text: str = None, target_format: str = "uppercase", **kwargs):
        """Convert text format."""
        # This would get text from clipboard if not provided
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
        """Translate text (placeholder - would integrate with translation service)."""
        # TODO: Integrate with translation service (Google Translate API, DeepL, or local model)
        # For now, return text with a marker indicating translation is not implemented
        from modules.diagnostics import log
        log("Translation not yet implemented - returning original text")
        return f"[Translation pending: {text}]"
    
    def _paste_text(self, text: str = None, **kwargs):
        """Paste text using keystroke."""
        if text is None:
            # Get from clipboard
            import win32clipboard
            try:
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except:
                return
        
        try:
            from modules.keystroke import send_text_ime_safe
            send_text_ime_safe(text)
        except Exception as e:
            print(f"Error pasting text: {e}")
    
    def _clean_format(self, text: str = None, **kwargs):
        """Clean text formatting (remove special characters, extra spaces, etc.)."""
        if text is None:
            import win32clipboard
            try:
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except:
                return ""
        
        # Remove extra whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
