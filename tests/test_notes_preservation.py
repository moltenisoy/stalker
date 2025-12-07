"""
Tests for notes character preservation.
Validates that special characters like <, >, & are preserved without HTML escaping.
"""
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import Storage
from modules_ai import NotesManager


def test_special_characters_preserved():
    """Test that special characters <, >, & are preserved in notes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_notes.db"
        storage = Storage(path=db_path)
        notes_mgr = NotesManager(storage=storage)
        
        # Test cases with special characters
        test_cases = [
            {
                "title": "HTML Tags Test",
                "body": "<html><body><h1>Title</h1></body></html>",
                "expected": "<html><body><h1>Title</h1></body></html>"
            },
            {
                "title": "Ampersand Test",
                "body": "Rock & Roll, Tom & Jerry, A&B",
                "expected": "Rock & Roll, Tom & Jerry, A&B"
            },
            {
                "title": "Comparison Operators",
                "body": "if (x > 5 && y < 10) { return x >= y; }",
                "expected": "if (x > 5 && y < 10) { return x >= y; }"
            },
            {
                "title": "Markdown Code Block",
                "body": "```cpp\ntemplate<typename T>\nclass Vector {};\n```",
                "expected": "```cpp\ntemplate<typename T>\nclass Vector {};\n```"
            },
            {
                "title": "Mixed Characters",
                "body": "Price: $5 < $10 & quantity > 0",
                "expected": "Price: $5 < $10 & quantity > 0"
            }
        ]
        
        # Create notes and verify
        for test_case in test_cases:
            notes_mgr.create(
                title=test_case["title"],
                body=test_case["body"],
                tags="test"
            )
        
        # Retrieve and verify
        all_notes = notes_mgr.search(q="", limit=100)
        assert len(all_notes) == len(test_cases), f"Expected {len(test_cases)} notes, got {len(all_notes)}"
        
        for i, note in enumerate(all_notes):
            # Find matching test case by title
            matching_case = None
            for tc in test_cases:
                if tc["title"] == note["title"]:
                    matching_case = tc
                    break
            
            assert matching_case is not None, f"Note with title '{note['title']}' not found in test cases"
            
            # Verify body is preserved exactly
            assert note["body"] == matching_case["expected"], \
                f"Body mismatch for '{matching_case['title']}':\n" \
                f"Expected: {matching_case['expected']}\n" \
                f"Got: {note['body']}"
        
        print("✓ test_special_characters_preserved passed")


def test_update_preserves_characters():
    """Test that updating notes preserves special characters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_notes.db"
        storage = Storage(path=db_path)
        notes_mgr = NotesManager(storage=storage)
        
        # Create a note
        notes_mgr.create(
            title="Original",
            body="Original body",
            tags="test"
        )
        
        # Get the note
        notes = notes_mgr.search(q="Original", limit=1)
        assert len(notes) == 1
        note = notes[0]
        note_id = note["id"]
        
        # Update with special characters
        new_body = "<script>alert('XSS');</script> & other > chars"
        notes_mgr.update(note_id, body=new_body)
        
        # Retrieve and verify
        updated_notes = notes_mgr.search(q="Original", limit=1)
        assert len(updated_notes) == 1
        updated_note = updated_notes[0]
        
        assert updated_note["body"] == new_body, \
            f"Body after update mismatch:\nExpected: {new_body}\nGot: {updated_note['body']}"
        
        print("✓ test_update_preserves_characters passed")


def test_search_with_special_characters():
    """Test that searching works with special characters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_notes.db"
        storage = Storage(path=db_path)
        notes_mgr = NotesManager(storage=storage)
        
        # Create notes with special characters
        notes_mgr.create(title="C++ Template", body="template<class T>", tags="cpp")
        notes_mgr.create(title="HTML Tag", body="<div>content</div>", tags="html")
        notes_mgr.create(title="Logic", body="x > 5 && y < 10", tags="logic")
        
        # Search for content with special characters
        results = notes_mgr.search(q="<div>", limit=10)
        assert len(results) >= 1, "Should find note with <div>"
        
        results = notes_mgr.search(q="template", limit=10)
        assert len(results) >= 1, "Should find note with template<class T>"
        
        print("✓ test_search_with_special_characters passed")


if __name__ == "__main__":
    print("Running notes character preservation tests...\n")
    test_special_characters_preserved()
    test_update_preserves_characters()
    test_search_with_special_characters()
    print("\n✅ All notes preservation tests passed!")
