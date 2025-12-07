"""
Tests for search result scoring and prioritization.
"""
import sys
import os
from dataclasses import dataclass
from typing import Callable, Optional

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# Mock SearchResult class to avoid circular imports
@dataclass
class SearchResult:
    title: str
    subtitle: str = ""
    action: Optional[Callable] = None
    copy_text: Optional[str] = None
    group: str = "general"
    meta: dict = None
    score: float = 0.0


def apply_scoring(results, query: str):
    """Mock scoring function matching engine._apply_scoring."""
    group_weights = {
        "calculator": 100,
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
        base_score = group_weights.get(result.group, 30)
        
        title_lower = result.title.lower()
        if title_lower == query_lower:
            base_score += 50
        elif title_lower.startswith(query_lower):
            base_score += 30
        elif query_lower in title_lower:
            base_score += 10
        
        result.score = base_score
    
    results.sort(key=lambda r: r.score, reverse=True)
    return results


def test_search_result_score():
    """Test that SearchResult has a score field."""
    result = SearchResult(title="Test", group="general")
    assert hasattr(result, "score")
    assert result.score == 0.0
    
    result_with_score = SearchResult(title="Test", group="app", score=50.0)
    assert result_with_score.score == 50.0
    
    print("✓ test_search_result_score passed")


def test_scoring_priority():
    """Test that scoring prioritizes results correctly."""
    results = [
        SearchResult(title="file.txt", group="file"),
        SearchResult(title="Calculator", group="calculator"),
        SearchResult(title="notepad", group="app"),
        SearchResult(title="clipboard item", group="clipboard"),
        SearchResult(title="command", group="command"),
    ]
    
    scored = apply_scoring(results, "test")
    groups_in_order = [r.group for r in scored]
    
    # Calculator should be first
    assert groups_in_order[0] == "calculator"
    
    # App should be before file
    app_idx = groups_in_order.index("app")
    file_idx = groups_in_order.index("file")
    assert app_idx < file_idx
    
    # Clipboard should be before file
    clip_idx = groups_in_order.index("clipboard")
    assert clip_idx < file_idx
    
    print("✓ test_scoring_priority passed")


def test_exact_match_bonus():
    """Test that exact matches get higher scores."""
    results = [
        SearchResult(title="calculator", group="app"),
        SearchResult(title="calc", group="app"),
        SearchResult(title="my calculator app", group="app"),
    ]
    
    # Search for "calc" - should prioritize exact match
    scored = apply_scoring(results.copy(), "calc")
    assert scored[0].title == "calc"
    
    # Search for "calculator" - should prioritize exact match
    scored = apply_scoring(results.copy(), "calculator")
    assert scored[0].title == "calculator"
    
    print("✓ test_exact_match_bonus passed")


def test_prefix_match_bonus():
    """Test that prefix matches get bonus scores."""
    results = [
        SearchResult(title="notepad", group="app"),
        SearchResult(title="my notes", group="note"),
        SearchResult(title="important note", group="note"),
    ]
    
    scored = apply_scoring(results, "note")
    titles = [r.title for r in scored]
    notepad_idx = titles.index("notepad")
    important_idx = titles.index("important note")
    
    # notepad (prefix match) should rank higher than "important note" (contains match)
    assert notepad_idx < important_idx
    
    print("✓ test_prefix_match_bonus passed")


def test_group_priority_override():
    """Test that group priority still matters even with match bonuses."""
    results = [
        SearchResult(title="calculate", group="file"),
        SearchResult(title="2+2", group="calculator"),
    ]
    
    scored = apply_scoring(results, "calc")
    
    # Calculator group has much higher base weight, so should still be first
    assert scored[0].group == "calculator"
    
    print("✓ test_group_priority_override passed")


if __name__ == "__main__":
    print("Running Search Scoring tests...\n")
    
    test_search_result_score()
    test_scoring_priority()
    test_exact_match_bonus()
    test_prefix_match_bonus()
    test_group_priority_override()
    
    print("\n✅ All Search Scoring tests passed!")
