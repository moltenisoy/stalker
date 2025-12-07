import threading
import time
from typing import Optional, List
import keyboard
from core.storage import Storage
from core.types import SearchResult
from modules.keystroke import send_text_ime_safe

class SnippetManager:
    """Gestión de snippets con triggers y hotkeys globales."""
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()
        self._registered = {}  # hotkey -> snippet_id
        self._register_hotkeys()

    def _register_hotkeys(self):
        # registra hotkeys únicas en segundo plano
        threading.Thread(target=self._async_register, daemon=True).start()

    def _async_register(self):
        snippets = self.storage.list_snippets()
        for snip in snippets:
            hotkey = snip["hotkey"]
            if hotkey and hotkey not in self._registered:
                keyboard.add_hotkey(hotkey, lambda s=snip: self.expand_snippet(s))
                self._registered[hotkey] = snip["id"]

    def expand_snippet(self, snippet_row):
        body = snippet_row["body"]
        send_text_ime_safe(body)

    def resolve_trigger(self, trigger: str) -> Optional[SearchResult]:
        sn = self.storage.get_snippet_by_trigger(trigger)
        if not sn:
            return None
        return SearchResult(
            title=f"{sn['name']} ({sn['trigger']})",
            subtitle="Snippet",
            action=lambda: self.expand_snippet(sn),
            copy_text=sn["body"],
            group="snippet",
        )

    def search(self, q: str, limit: int = 30) -> List[SearchResult]:
        results = []
        for sn in self.storage.list_snippets(q=q, limit=limit):
            results.append(
                SearchResult(
                    title=f"{sn['name']} ({sn['trigger']})",
                    subtitle=sn["body"][:80],
                    action=lambda s=sn: self.expand_snippet(s),
                    copy_text=sn["body"],
                    group="snippet",
                )
            )
        return results