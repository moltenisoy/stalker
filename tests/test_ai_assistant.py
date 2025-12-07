"""
Tests for AI assistant improvements.
Validates error handling, timeout logic, and retry behavior.
"""
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.ai_assistant import AIAssistant
from core.storage import Storage


def test_missing_api_key():
    """Test that appropriate error is returned when API key is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        storage = Storage(path=db_path)
        ai = AIAssistant(storage=storage)
        
        # Try to ask without setting API key
        response, success = ai.ask("test query", provider="openai")
        
        assert not success, "Should fail when API key is missing"
        assert "API key" in response or "Falta" in response, \
            f"Error message should mention API key, got: {response}"
        assert "❌" in response, "Error message should have error icon"
        
        print("✓ test_missing_api_key passed")


def test_unsupported_provider():
    """Test that appropriate error is returned for unsupported provider."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        storage = Storage(path=db_path)
        ai = AIAssistant(storage=storage)
        
        # Try to use an unsupported provider
        response, success = ai.ask("test query", provider="invalid")  # type: ignore
        
        assert not success, "Should fail for unsupported provider"
        assert "❌" in response, "Error message should have error icon"
        
        print("✓ test_unsupported_provider passed")


def test_timeout_configuration():
    """Test that timeout can be configured."""
    ai1 = AIAssistant(timeout=10)
    assert ai1.timeout == 10, "Timeout should be configurable"
    
    ai2 = AIAssistant(timeout=60)
    assert ai2.timeout == 60, "Timeout should be configurable"
    
    print("✓ test_timeout_configuration passed")


def test_retry_configuration():
    """Test that retry count can be configured."""
    ai1 = AIAssistant(max_retries=1)
    assert ai1.max_retries == 1, "Max retries should be configurable"
    
    ai2 = AIAssistant(max_retries=5)
    assert ai2.max_retries == 5, "Max retries should be configurable"
    
    print("✓ test_retry_configuration passed")


def test_api_key_encryption_integration():
    """Test that AI assistant can retrieve encrypted API keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        key_file = Path(tmpdir) / "encryption.key"
        
        # Temporarily override KEY_FILE location
        import core.storage
        original_key_file = core.storage.KEY_FILE
        core.storage.KEY_FILE = key_file
        
        try:
            storage = Storage(path=db_path, encrypt_keys=True)
            ai = AIAssistant(storage=storage)
            
            # Set encrypted API key
            test_key = "sk-test-encrypted-key-12345"
            ai.set_api_key("openai", test_key)
            
            # Verify it can be retrieved (decrypted)
            retrieved_key = ai._get_api_key("openai")
            assert retrieved_key == test_key, \
                f"AI should retrieve decrypted key. Expected {test_key}, got {retrieved_key}"
            
            print("✓ test_api_key_encryption_integration passed")
        
        finally:
            # Restore original KEY_FILE
            core.storage.KEY_FILE = original_key_file


def test_response_format():
    """Test that AI responses follow the expected format (tuple)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        storage = Storage(path=db_path)
        ai = AIAssistant(storage=storage)
        
        # Test response format
        response, success = ai.ask("test", provider="openai")
        
        assert isinstance(response, str), "Response should be a string"
        assert isinstance(success, bool), "Success should be a boolean"
        assert not success, "Should fail without API key"
        
        print("✓ test_response_format passed")


def test_error_messages_are_clear():
    """Test that error messages are clear and actionable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        storage = Storage(path=db_path)
        ai = AIAssistant(storage=storage)
        
        # Test missing API key error
        response, _ = ai.ask("test", provider="openai")
        assert "❌" in response, "Should have error icon"
        assert len(response) > 10, "Error message should be descriptive"
        assert "API key" in response or "clave" in response.lower(), \
            "Should mention API key issue"
        
        print("✓ test_error_messages_are_clear passed")


if __name__ == "__main__":
    print("Running AI assistant tests...\n")
    test_missing_api_key()
    test_unsupported_provider()
    test_timeout_configuration()
    test_retry_configuration()
    test_api_key_encryption_integration()
    test_response_format()
    test_error_messages_are_clear()
    print("\n✅ All AI assistant tests passed!")
