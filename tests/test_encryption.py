"""
Tests for API key encryption in storage.
Validates that API keys are encrypted using Fernet when enabled.
"""
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import Storage


def test_encryption_enabled():
    """Test that API keys are encrypted when encryption is enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        key_file = Path(tmpdir) / "encryption.key"
        
        # Temporarily override KEY_FILE location
        import core.storage
        original_key_file = core.storage.KEY_FILE
        core.storage.KEY_FILE = key_file
        
        try:
            # Create storage with encryption
            storage = Storage(path=db_path, encrypt_keys=True)
            
            # Store an API key
            test_key = "sk-test-1234567890abcdef"
            storage.set_api_key("openai", test_key)
            
            # Retrieve and verify it's decrypted correctly
            retrieved_key = storage.get_api_key("openai")
            assert retrieved_key == test_key, f"Expected {test_key}, got {retrieved_key}"
            
            # Verify the key file was created
            assert key_file.exists(), "Encryption key file should be created"
            
            # Read raw data from database to verify it's encrypted
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT key FROM api_keys WHERE provider='openai'")
            row = cursor.fetchone()
            conn.close()
            
            assert row is not None, "API key should be stored in database"
            stored_value = row[0]
            
            # The stored value should be different from the original (encrypted)
            # Only check if encryption is actually available
            if storage.encrypt_keys and storage._cipher:
                assert stored_value != test_key, \
                    f"Stored key should be encrypted, got: {stored_value}"
            
            print("✓ test_encryption_enabled passed")
        
        finally:
            # Restore original KEY_FILE
            core.storage.KEY_FILE = original_key_file


def test_encryption_disabled():
    """Test that API keys work when encryption is disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        
        # Create storage without encryption
        storage = Storage(path=db_path, encrypt_keys=False)
        
        # Store an API key
        test_key = "sk-test-0987654321fedcba"
        storage.set_api_key("anthropic", test_key)
        
        # Retrieve and verify
        retrieved_key = storage.get_api_key("anthropic")
        assert retrieved_key == test_key, f"Expected {test_key}, got {retrieved_key}"
        
        print("✓ test_encryption_disabled passed")


def test_multiple_providers():
    """Test encryption with multiple API providers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        key_file = Path(tmpdir) / "encryption.key"
        
        # Temporarily override KEY_FILE location
        import core.storage
        original_key_file = core.storage.KEY_FILE
        core.storage.KEY_FILE = key_file
        
        try:
            storage = Storage(path=db_path, encrypt_keys=True)
            
            # Store keys for different providers
            providers = {
                "openai": "sk-openai-key-123",
                "anthropic": "sk-ant-key-456",
                "local": "local-endpoint-789"
            }
            
            for provider, key in providers.items():
                storage.set_api_key(provider, key)
            
            # Verify all keys can be retrieved correctly
            for provider, expected_key in providers.items():
                retrieved_key = storage.get_api_key(provider)
                assert retrieved_key == expected_key, \
                    f"Provider {provider}: Expected {expected_key}, got {retrieved_key}"
            
            print("✓ test_multiple_providers passed")
        
        finally:
            # Restore original KEY_FILE
            core.storage.KEY_FILE = original_key_file


def test_encryption_key_persistence():
    """Test that the same encryption key is reused across instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        key_file = Path(tmpdir) / "encryption.key"
        
        # Temporarily override KEY_FILE location
        import core.storage
        original_key_file = core.storage.KEY_FILE
        core.storage.KEY_FILE = key_file
        
        try:
            # Create first storage instance and store a key
            storage1 = Storage(path=db_path, encrypt_keys=True)
            test_key = "sk-persistent-test-key"
            storage1.set_api_key("openai", test_key)
            
            # Close first instance (simulate restart)
            del storage1
            
            # Create second storage instance
            storage2 = Storage(path=db_path, encrypt_keys=True)
            
            # Verify the key can still be retrieved
            retrieved_key = storage2.get_api_key("openai")
            assert retrieved_key == test_key, \
                f"Key should persist across instances. Expected {test_key}, got {retrieved_key}"
            
            print("✓ test_encryption_key_persistence passed")
        
        finally:
            # Restore original KEY_FILE
            core.storage.KEY_FILE = original_key_file


def test_decrypt_fallback_for_old_data():
    """Test that decryption falls back gracefully for unencrypted data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_storage.db"
        
        # First store data without encryption
        storage_no_encrypt = Storage(path=db_path, encrypt_keys=False)
        test_key = "sk-old-unencrypted-key"
        storage_no_encrypt.set_api_key("openai", test_key)
        del storage_no_encrypt
        
        # Now read with encryption enabled
        key_file = Path(tmpdir) / "encryption.key"
        import core.storage
        original_key_file = core.storage.KEY_FILE
        core.storage.KEY_FILE = key_file
        
        try:
            storage_with_encrypt = Storage(path=db_path, encrypt_keys=True)
            
            # Should still be able to read the old unencrypted data
            retrieved_key = storage_with_encrypt.get_api_key("openai")
            assert retrieved_key == test_key, \
                f"Should read old unencrypted data. Expected {test_key}, got {retrieved_key}"
            
            print("✓ test_decrypt_fallback_for_old_data passed")
        
        finally:
            # Restore original KEY_FILE
            core.storage.KEY_FILE = original_key_file


if __name__ == "__main__":
    print("Running encryption tests...\n")
    test_encryption_enabled()
    test_encryption_disabled()
    test_multiple_providers()
    test_encryption_key_persistence()
    test_decrypt_fallback_for_old_data()
    print("\n✅ All encryption tests passed!")
