import json
import time
import threading
import keyboard
import mouse
from dataclasses import dataclass, field
from typing import List, Literal, Any, Callable, Optional
from core.storage import Storage
from core.types import SearchResult

EventType = Literal["key", "click"]

@dataclass
class MacroEvent:
    t: EventType
    data: Any
    dt: float

@dataclass
class Macro:
    name: str
    events: List[MacroEvent] = field(default_factory=list)

class MacroRecorder:
    """Graba teclas/clics y las guarda en storage; ejecuta con hotkey."""
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()
        self._recording = False
        self._start_time = 0
        self._events: List[MacroEvent] = []
        self._registered = {}

    def start(self):
        if self._recording:
            return
        self._recording = True
        self._start_time = time.time()
        self._events = []
        threading.Thread(target=self._record, daemon=True).start()

    def stop_and_save(self, name: str):
        self._recording = False
        macro = {"name": name, "events": [e.__dict__ for e in self._events]}
        # Reuse quicklinks table to store FlowCommand-like macros with kind="command"
        self.storage.add_quicklink(name=name, target=json.dumps(macro), kind="command", category="macro")
        return macro

    def _record(self):
        def on_key(e):
            if not self._recording:
                return
            self._events.append(MacroEvent("key", {"name": e.name, "event_type": e.event_type}, time.time() - self._start_time))
        def on_click(x, y, button, pressed):
            if not self._recording:
                return
            self._events.append(MacroEvent("click", {"x": x, "y": y, "button": button, "pressed": pressed}, time.time() - self._start_time))
        keyboard.hook(on_key, suppress=False)
        mouse.hook(on_click)
        while self._recording:
            time.sleep(0.05)
        keyboard.unhook(on_key)
        mouse.unhook(on_click)

    def playback(self, macro_data: dict):
        events = [MacroEvent(**e) for e in macro_data.get("events", [])]
        last_dt = 0
        for ev in events:
            time.sleep(max(0, ev.dt - last_dt))
            last_dt = ev.dt
            if ev.t == "key":
                if ev.data.get("event_type") == "down":
                    keyboard.press(ev.data["name"])
                elif ev.data.get("event_type") == "up":
                    keyboard.release(ev.data["name"])
            elif ev.t == "click":
                if ev.data.get("pressed"):
                    mouse.press(ev.data["x"], ev.data["y"], button=ev.data["button"])
                else:
                    mouse.release(ev.data["x"], ev.data["y"], button=ev.data["button"])

    def search_macros(self, q: str = "", limit: int = 30):
        results = []
        for link in self.storage.list_quicklinks(q=q, limit=limit):
            if link["category"] != "macro":
                continue
            macro_data = json.loads(link["target"])
            results.append(
                SearchResult(
                    title=f"Macro: {macro_data['name']}",
                    subtitle=f"{len(macro_data.get('events', []))} eventos",
                    action=lambda m=macro_data: self.playback(m),
                    group="macro",
                )
            )
        return results