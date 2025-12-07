"""
Context Profiles - App-specific automation profiles.
Provides contextual shortcuts, snippets, and actions based on active window.
"""
import json
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from core.engine import SearchResult

@dataclass
class ContextAction:
    """An action available in a specific context."""
    name: str
    description: str
    trigger: str  # Hotkey or command trigger
    action_type: str  # snippet, command, flow
    action_data: Dict
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict):
        return ContextAction(**data)

@dataclass
class AppProfile:
    """Profile for a specific application."""
    app_name: str
    display_name: str
    window_class: str = ""
    window_title_pattern: str = ""
    actions: List[ContextAction] = None
    snippets: Dict[str, str] = None
    shortcuts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.snippets is None:
            self.snippets = {}
        if self.shortcuts is None:
            self.shortcuts = {}
    
    def to_dict(self):
        return {
            "app_name": self.app_name,
            "display_name": self.display_name,
            "window_class": self.window_class,
            "window_title_pattern": self.window_title_pattern,
            "actions": [a.to_dict() for a in self.actions],
            "snippets": self.snippets,
            "shortcuts": self.shortcuts,
        }
    
    @staticmethod
    def from_dict(data: Dict):
        actions = [ContextAction.from_dict(a) for a in data.get("actions", [])]
        return AppProfile(
            app_name=data["app_name"],
            display_name=data["display_name"],
            window_class=data.get("window_class", ""),
            window_title_pattern=data.get("window_title_pattern", ""),
            actions=actions,
            snippets=data.get("snippets", {}),
            shortcuts=data.get("shortcuts", {}),
        )

class ContextProfileManager:
    """
    Manages contextual profiles for different applications.
    Provides app-specific actions, snippets, and shortcuts.
    """
    
    def __init__(self, profiles_dir: str = None):
        if profiles_dir is None:
            profiles_dir = os.path.join(os.path.expanduser("~"), ".stalker", "profiles")
        
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, AppProfile] = {}
        
        # Ensure profiles directory exists
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Register built-in profiles
        self._register_builtin_profiles()
        
        # Load custom profiles
        self._load_profiles()
    
    def _register_builtin_profiles(self):
        """Register built-in application profiles."""
        
        # VSCode profile
        vscode = AppProfile(
            app_name="vscode",
            display_name="Visual Studio Code",
            window_class="Chrome_WidgetWin_1",
            window_title_pattern="Visual Studio Code",
        )
        vscode.actions = [
            ContextAction(
                name="search_symbols",
                description="Buscar símbolos en el proyecto",
                trigger="ctrl+t",
                action_type="command",
                action_data={"command": "workbench.action.showAllSymbols"}
            ),
            ContextAction(
                name="find_file",
                description="Buscar archivo",
                trigger="ctrl+p",
                action_type="command",
                action_data={"command": "workbench.action.quickOpen"}
            ),
            ContextAction(
                name="terminal",
                description="Abrir terminal integrada",
                trigger="ctrl+`",
                action_type="command",
                action_data={"command": "workbench.action.terminal.toggleTerminal"}
            ),
        ]
        vscode.snippets = {
            "@log": "console.log('${1}', ${1});",
            "@func": "function ${1:name}(${2:params}) {\n\t${3}\n}",
            "@class": "class ${1:ClassName} {\n\tconstructor(${2}) {\n\t\t${3}\n\t}\n}",
        }
        self.profiles["vscode"] = vscode
        
        # Browser profile
        browser = AppProfile(
            app_name="browser",
            display_name="Navegador Web",
            window_class="Chrome_WidgetWin_1",
            window_title_pattern="Chrome|Firefox|Edge",
        )
        browser.actions = [
            ContextAction(
                name="save_session",
                description="Guardar sesión de pestañas",
                trigger="ctrl+shift+s",
                action_type="flow",
                action_data={"flow": "save_browser_tabs"}
            ),
            ContextAction(
                name="restore_session",
                description="Restaurar sesión de pestañas",
                trigger="ctrl+shift+r",
                action_type="flow",
                action_data={"flow": "restore_browser_tabs"}
            ),
            ContextAction(
                name="extract_links",
                description="Extraer todos los enlaces",
                trigger="ctrl+shift+l",
                action_type="flow",
                action_data={"flow": "extract_links"}
            ),
        ]
        self.profiles["browser"] = browser
        
        # Figma profile
        figma = AppProfile(
            app_name="figma",
            display_name="Figma",
            window_title_pattern="Figma",
        )
        figma.actions = [
            ContextAction(
                name="export_selection",
                description="Exportar selección",
                trigger="ctrl+shift+e",
                action_type="command",
                action_data={"command": "export"}
            ),
        ]
        self.profiles["figma"] = figma
        
        # File Explorer profile
        explorer = AppProfile(
            app_name="explorer",
            display_name="Explorador de Archivos",
            window_class="CabinetWClass",
        )
        explorer.actions = [
            ContextAction(
                name="copy_path",
                description="Copiar ruta completa",
                trigger="ctrl+shift+c",
                action_type="flow",
                action_data={"flow": "copy_current_path"}
            ),
            ContextAction(
                name="terminal_here",
                description="Abrir terminal aquí",
                trigger="ctrl+shift+t",
                action_type="flow",
                action_data={"flow": "open_terminal_here"}
            ),
        ]
        self.profiles["explorer"] = explorer
    
    def _load_profiles(self):
        """Load custom profiles from disk."""
        if not os.path.exists(self.profiles_dir):
            return
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.profiles_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile = AppProfile.from_dict(data)
                        self.profiles[profile.app_name] = profile
                except Exception as e:
                    print(f"Error loading profile {filename}: {e}")
    
    def save_profile(self, profile: AppProfile):
        """Save a profile to disk."""
        filepath = os.path.join(self.profiles_dir, f"{profile.app_name}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving profile {profile.app_name}: {e}")
    
    def get_profile(self, app_name: str) -> Optional[AppProfile]:
        """Get profile for a specific app."""
        return self.profiles.get(app_name)
    
    def get_profile_for_window(self, window_title: str, window_class: str = "") -> Optional[AppProfile]:
        """
        Get the matching profile for a window.
        
        Args:
            window_title: Title of the active window
            window_class: Window class name
            
        Returns:
            Matching AppProfile or None
        """
        import re
        
        for profile in self.profiles.values():
            # Check window class match
            if profile.window_class and window_class:
                if profile.window_class == window_class:
                    return profile
            
            # Check window title pattern match
            if profile.window_title_pattern:
                if re.search(profile.window_title_pattern, window_title, re.IGNORECASE):
                    return profile
        
        return None
    
    def get_actions_for_profile(self, profile: AppProfile) -> List[SearchResult]:
        """
        Get available actions for a profile as SearchResults.
        
        Args:
            profile: AppProfile to get actions from
            
        Returns:
            List of SearchResults for each action
        """
        results = []
        
        for action in profile.actions:
            results.append(SearchResult(
                title=f"⚡ {action.name}",
                subtitle=f"{action.description} ({action.trigger})",
                action=lambda a=action: self._execute_action(a),
                group=f"context_{profile.app_name}"
            ))
        
        return results
    
    def get_snippets_for_profile(self, profile: AppProfile, query: str = "") -> List[SearchResult]:
        """
        Get snippets for a profile as SearchResults.
        
        Args:
            profile: AppProfile to get snippets from
            query: Optional search query
            
        Returns:
            List of SearchResults for matching snippets
        """
        results = []
        qlow = query.lower()
        
        for trigger, body in profile.snippets.items():
            if not query or qlow in trigger.lower() or qlow in body.lower():
                results.append(SearchResult(
                    title=f"📝 {trigger}",
                    subtitle=body[:80],
                    action=lambda b=body: self._paste_snippet(b),
                    copy_text=body,
                    group=f"snippet_{profile.app_name}"
                ))
        
        return results
    
    def _execute_action(self, action: ContextAction):
        """Execute a context action."""
        from modules.diagnostics import log
        
        if action.action_type == "command":
            # Execute command (placeholder - would need app-specific implementation)
            log(f"Executing command: {action.action_data.get('command')}")
        elif action.action_type == "flow":
            # Execute flow (would integrate with FlowCommands)
            log(f"Executing flow: {action.action_data.get('flow')}")
        elif action.action_type == "snippet":
            # Paste snippet
            text = action.action_data.get("text", "")
            self._paste_snippet(text)
    
    def _paste_snippet(self, text: str):
        """Paste snippet text."""
        try:
            from modules.keystroke import send_text_ime_safe
            send_text_ime_safe(text)
        except Exception as e:
            print(f"Error pasting snippet: {e}")
    
    def create_profile(self, app_name: str, display_name: str) -> AppProfile:
        """Create a new profile."""
        profile = AppProfile(app_name=app_name, display_name=display_name)
        self.profiles[app_name] = profile
        self.save_profile(profile)
        return profile
    
    def add_action_to_profile(self, app_name: str, action: ContextAction):
        """Add an action to a profile."""
        profile = self.get_profile(app_name)
        if profile:
            profile.actions.append(action)
            self.save_profile(profile)
    
    def add_snippet_to_profile(self, app_name: str, trigger: str, body: str):
        """Add a snippet to a profile."""
        profile = self.get_profile(app_name)
        if profile:
            profile.snippets[trigger] = body
            self.save_profile(profile)
