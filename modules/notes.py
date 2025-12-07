"""
Gestión de notas en markdown con manejo correcto de caracteres especiales (<, >, &).
- Se almacena el texto plano sin escapar (no se convierten a entidades HTML).
- Úsalo con editores de texto plano (QPlainTextEdit) o setAcceptRichText(False) si usas QTextEdit.
"""
import time
from typing import Optional, List
from dataclasses import dataclass
from core.storage import Storage

@dataclass
class Note:
    id: Optional[int]
    title: str
    body: str
    tags: str
    created_at: float
    updated_at: float

class NotesManager:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()

    def create(self, title: str, body: str, tags: str = "") -> Note:
        return self.storage.add_note(title, body, tags)

    def update(self, note_id: int, title: Optional[str] = None, body: Optional[str] = None, tags: Optional[str] = None):
        self.storage.update_note(note_id, title=title, body=body, tags=tags)

    def search(self, q: str = "", limit: int = 50) -> List[Note]:
        return self.storage.list_notes(q=q, limit=limit)