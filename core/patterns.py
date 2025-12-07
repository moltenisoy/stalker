"""
Shared regex patterns and utilities.
Centralized location for common patterns used across modules.
"""
import re

# URL patterns
# Match http/https URLs with common characters in URLs
URL_PATTERN = r'http[s]?://(?:[a-zA-Z0-9$\-_.+!*\'(),@&]|(?:%[0-9a-fA-F]{2}))+'

# Email pattern
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Number pattern (matches integers and decimals)
NUMBER_PATTERN = r'\b(?:\d+\.?\d*|\.\d+)\b'

# File path patterns (Windows)
WINDOWS_PATH_PATTERN = r'[A-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'

def extract_urls(text: str) -> list:
    """Extract all URLs from text."""
    return re.findall(URL_PATTERN, text)

def extract_emails(text: str) -> list:
    """Extract all email addresses from text."""
    return re.findall(EMAIL_PATTERN, text)

def extract_numbers(text: str) -> list:
    """Extract all numbers from text."""
    return re.findall(NUMBER_PATTERN, text)

def is_url(text: str) -> bool:
    """Check if text is a URL."""
    return bool(re.match(r'^' + URL_PATTERN + r'$', text.strip()))

def is_email(text: str) -> bool:
    """Check if text is an email address."""
    return bool(re.match(r'^' + EMAIL_PATTERN + r'$', text.strip()))

def is_windows_path(text: str) -> bool:
    """Check if text looks like a Windows file path."""
    return bool(re.match(r'^' + WINDOWS_PATH_PATTERN + r'$', text.strip()))
