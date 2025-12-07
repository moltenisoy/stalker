"""
Core types shared across the application.
This module avoids circular import issues.
"""
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class SearchResult:
    """Result from a search query."""
    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    copy_text: Optional[str] = None
    group: str = "general"
    meta: dict = None
    score: float = 0.0  # Higher score = higher priority
