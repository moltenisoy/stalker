"""
Flow Commands - Declarative DSL for defining app-specific automation recipes.
Allows users to create custom automation workflows without touching native code.
"""
import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class FlowStep:
    """A single step in a flow."""
    action: str  # Action type: 'keystroke', 'clipboard', 'command', 'wait', 'if'
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # Optional condition for conditional steps
    
    def to_dict(self):
        return {
            "action": self.action,
            "params": self.params,
            "condition": self.condition
        }
    
    @staticmethod
    def from_dict(data: Dict):
        return FlowStep(
            action=data["action"],
            params=data.get("params", {}),
            condition=data.get("condition")
        )

@dataclass
class FlowCommand:
    """A complete flow command/recipe."""
    name: str
    description: str
    app_context: str  # App this flow is designed for
    steps: List[FlowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "app_context": self.app_context,
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables
        }
    
    @staticmethod
    def from_dict(data: Dict):
        steps = [FlowStep.from_dict(s) for s in data.get("steps", [])]
        return FlowCommand(
            name=data["name"],
            description=data["description"],
            app_context=data["app_context"],
            steps=steps,
            variables=data.get("variables", {})
        )

class FlowCommandExecutor:
    """
    Executes flow commands defined in the DSL.
    """
    
    def __init__(self):
        self.action_handlers: Dict[str, Callable] = {
            "keystroke": self._handle_keystroke,
            "clipboard": self._handle_clipboard,
            "command": self._handle_command,
            "wait": self._handle_wait,
            "paste": self._handle_paste,
            "copy": self._handle_copy,
            "open": self._handle_open,
            "save": self._handle_save,
            "transform": self._handle_transform,
        }
    
    def execute(self, flow: FlowCommand, context: Dict[str, Any] = None) -> bool:
        """
        Execute a flow command.
        
        Args:
            flow: FlowCommand to execute
            context: Additional context variables
            
        Returns:
            True if execution succeeded
        """
        if context is None:
            context = {}
        
        # Merge flow variables with context
        variables = {**flow.variables, **context}
        
        try:
            for step in flow.steps:
                # Check condition if present
                if step.condition and not self._evaluate_condition(step.condition, variables):
                    continue
                
                # Execute step
                handler = self.action_handlers.get(step.action)
                if handler:
                    result = handler(step.params, variables)
                    # Update variables with result if it's a dict
                    if isinstance(result, dict):
                        variables.update(result)
                else:
                    print(f"Unknown action: {step.action}")
                    return False
            
            return True
        except Exception as e:
            print(f"Error executing flow {flow.name}: {e}")
            return False
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate a simple condition."""
        # Simple condition evaluation (can be expanded)
        # Format: "variable == value" or "variable != value"
        try:
            parts = condition.split()
            if len(parts) == 3:
                var, op, value = parts
                var_value = variables.get(var)
                
                if op == "==":
                    return str(var_value) == value
                elif op == "!=":
                    return str(var_value) != value
        except:
            pass
        
        return True
    
    def _handle_keystroke(self, params: Dict, variables: Dict) -> None:
        """Handle keystroke action."""
        keys = params.get("keys", "")
        # Replace variables in keys
        for var, value in variables.items():
            keys = keys.replace(f"${{{var}}}", str(value))
        
        try:
            import keyboard
            keyboard.send(keys)
        except Exception as e:
            print(f"Error sending keystroke: {e}")
    
    def _handle_clipboard(self, params: Dict, variables: Dict) -> Dict:
        """Handle clipboard action (get or set)."""
        operation = params.get("operation", "get")
        
        try:
            import win32clipboard
            
            if operation == "get":
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return {"clipboard_content": text}
            elif operation == "set":
                text = params.get("text", "")
                # Replace variables
                for var, value in variables.items():
                    text = text.replace(f"${{{var}}}", str(value))
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error handling clipboard: {e}")
        
        return {}
    
    def _handle_command(self, params: Dict, variables: Dict) -> None:
        """Handle system command execution."""
        command = params.get("command", "")
        # Replace variables
        for var, value in variables.items():
            command = command.replace(f"${{{var}}}", str(value))
        
        try:
            import subprocess
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"Error executing command: {e}")
    
    def _handle_wait(self, params: Dict, variables: Dict) -> None:
        """Handle wait/delay action."""
        import time
        duration = params.get("duration", 0.5)
        time.sleep(duration)
    
    def _handle_paste(self, params: Dict, variables: Dict) -> None:
        """Handle paste text action."""
        text = params.get("text", "")
        # Replace variables
        for var, value in variables.items():
            text = text.replace(f"${{{var}}}", str(value))
        
        try:
            from modules.keystroke import send_text_ime_safe
            send_text_ime_safe(text)
        except Exception as e:
            print(f"Error pasting text: {e}")
    
    def _handle_copy(self, params: Dict, variables: Dict) -> None:
        """Handle copy action."""
        text = params.get("text", "")
        # Replace variables
        for var, value in variables.items():
            text = text.replace(f"${{{var}}}", str(value))
        
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error copying: {e}")
    
    def _handle_open(self, params: Dict, variables: Dict) -> None:
        """Handle open file/folder action."""
        path = params.get("path", "")
        # Replace variables
        for var, value in variables.items():
            path = path.replace(f"${{{var}}}", str(value))
        
        try:
            import subprocess
            subprocess.run(['explorer', path], shell=True)
        except Exception as e:
            print(f"Error opening: {e}")
    
    def _handle_save(self, params: Dict, variables: Dict) -> None:
        """Handle save action."""
        # Trigger save shortcut
        try:
            import keyboard
            keyboard.send('ctrl+s')
        except Exception as e:
            print(f"Error saving: {e}")
    
    def _handle_transform(self, params: Dict, variables: Dict) -> Dict:
        """Handle text transformation."""
        text = params.get("text", variables.get("clipboard_content", ""))
        transform_type = params.get("type", "uppercase")
        
        if transform_type == "uppercase":
            result = text.upper()
        elif transform_type == "lowercase":
            result = text.lower()
        elif transform_type == "title":
            result = text.title()
        elif transform_type == "clean":
            import re
            result = re.sub(r'\s+', ' ', text).strip()
        elif transform_type == "extract_links":
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            result = '\n'.join(urls)
        else:
            result = text
        
        return {"transformed_text": result}

class FlowCommandManager:
    """
    Manages flow commands - loading, saving, and executing.
    """
    
    def __init__(self, flows_dir: str = None):
        if flows_dir is None:
            flows_dir = os.path.join(os.path.expanduser("~"), ".stalker", "flows")
        
        self.flows_dir = flows_dir
        self.flows: Dict[str, FlowCommand] = {}
        self.executor = FlowCommandExecutor()
        
        # Ensure flows directory exists
        os.makedirs(self.flows_dir, exist_ok=True)
        
        # Register built-in flows
        self._register_builtin_flows()
        
        # Load custom flows
        self._load_flows()
    
    def _register_builtin_flows(self):
        """Register built-in flow commands."""
        
        # Copy current path flow
        copy_path = FlowCommand(
            name="copy_current_path",
            description="Copiar ruta del archivo/carpeta actual",
            app_context="explorer"
        )
        copy_path.steps = [
            FlowStep("keystroke", {"keys": "alt+d"}),  # Focus address bar
            FlowStep("wait", {"duration": 0.2}),
            FlowStep("keystroke", {"keys": "ctrl+c"}),  # Copy
            FlowStep("wait", {"duration": 0.1}),
            FlowStep("keystroke", {"keys": "escape"}),  # Close address bar
        ]
        self.flows["copy_current_path"] = copy_path
        
        # Open terminal here flow
        terminal_here = FlowCommand(
            name="open_terminal_here",
            description="Abrir terminal en carpeta actual",
            app_context="explorer"
        )
        terminal_here.steps = [
            FlowStep("keystroke", {"keys": "alt+d"}),
            FlowStep("wait", {"duration": 0.2}),
            FlowStep("clipboard", {"operation": "get"}),
            FlowStep("command", {"command": "cmd /k cd /d ${clipboard_content}"}),
        ]
        self.flows["open_terminal_here"] = terminal_here
        
        # Extract links flow
        extract_links = FlowCommand(
            name="extract_links",
            description="Extraer todos los enlaces de la página",
            app_context="browser"
        )
        extract_links.steps = [
            FlowStep("clipboard", {"operation": "get"}),
            FlowStep("transform", {"type": "extract_links"}),
            FlowStep("copy", {"text": "${transformed_text}"}),
        ]
        self.flows["extract_links"] = extract_links
        
        # Clean and paste flow
        clean_paste = FlowCommand(
            name="clean_and_paste",
            description="Limpiar formato y pegar",
            app_context="any"
        )
        clean_paste.steps = [
            FlowStep("clipboard", {"operation": "get"}),
            FlowStep("transform", {"type": "clean"}),
            FlowStep("paste", {"text": "${transformed_text}"}),
        ]
        self.flows["clean_and_paste"] = clean_paste
    
    def _load_flows(self):
        """Load custom flows from disk."""
        if not os.path.exists(self.flows_dir):
            return
        
        for filename in os.listdir(self.flows_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.flows_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        flow = FlowCommand.from_dict(data)
                        self.flows[flow.name] = flow
                except Exception as e:
                    print(f"Error loading flow {filename}: {e}")
    
    def save_flow(self, flow: FlowCommand):
        """Save a flow to disk."""
        filepath = os.path.join(self.flows_dir, f"{flow.name}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(flow.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving flow {flow.name}: {e}")
    
    def get_flow(self, name: str) -> Optional[FlowCommand]:
        """Get a flow by name."""
        return self.flows.get(name)
    
    def execute_flow(self, name: str, context: Dict[str, Any] = None) -> bool:
        """Execute a flow by name."""
        flow = self.get_flow(name)
        if flow:
            return self.executor.execute(flow, context)
        return False
    
    def create_flow(self, name: str, description: str, app_context: str = "any") -> FlowCommand:
        """Create a new flow."""
        flow = FlowCommand(name=name, description=description, app_context=app_context)
        self.flows[name] = flow
        self.save_flow(flow)
        return flow
    
    def add_step_to_flow(self, flow_name: str, step: FlowStep):
        """Add a step to a flow."""
        flow = self.get_flow(flow_name)
        if flow:
            flow.steps.append(step)
            self.save_flow(flow)
    
    def get_flows_for_app(self, app_context: str) -> List[FlowCommand]:
        """Get all flows for a specific app context."""
        return [f for f in self.flows.values() if f.app_context == app_context or f.app_context == "any"]
