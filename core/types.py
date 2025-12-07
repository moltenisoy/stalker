"""
Core types shared across the application.
This module avoids circular import issues.
"""
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, Any

@dataclass
class SearchResult:
    """Result from a search query."""
    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    copy_text: Optional[str] = None
    group: str = "general"
    meta: Optional[Dict[str, Any]] = None
    score: float = 0.0  # Higher score = higher priority
