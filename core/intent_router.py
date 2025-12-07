"""
Intent Router - Local intent detection and classification.
Detects user intentions from queries without cloud processing.
"""
import re
from typing import List, Dict, Tuple, Optional
from enum import Enum

class IntentType(Enum):
    """Types of intents that can be detected."""
    OPEN_APP = "open_app"
    SEARCH_FILE = "search_file"
    PASTE_SNIPPET = "paste_snippet"
    SYSTEM_ACTION = "system_action"
    CLIPBOARD_ACTION = "clipboard_action"
    FILE_ACTION = "file_action"
    TEXT_TRANSFORM = "text_transform"
    CALCULATE = "calculate"
    TRANSLATE = "translate"
    WEB_SEARCH = "web_search"
    UNKNOWN = "unknown"

class Intent:
    """Represents a detected user intent."""
    def __init__(self, intent_type: IntentType, confidence: float, params: Dict = None):
        self.type = intent_type
        self.confidence = confidence  # 0.0 to 1.0
        self.params = params or {}
    
    def __repr__(self):
        return f"Intent({self.type.value}, confidence={self.confidence:.2f}, params={self.params})"

class IntentRouter:
    """
    Local intent detection and routing.
    All processing happens on-device for speed and privacy.
    """
    
    # Patterns for intent detection
    APP_PATTERNS = [
        (r"^(open|launch|start|run)\s+(.+)", 0.9),
        (r"^(.+)\s+(app|application|programa)", 0.8),
    ]
    
    FILE_PATTERNS = [
        (r"^(find|search|buscar|locate)\s+(.+)\s+(file|archivo)", 0.9),
        (r"^(file|archivo)[:;]\s*(.+)", 0.85),
        (r"\.(pdf|docx?|xlsx?|pptx?|txt|py|js|java|cpp|cs|html|css)$", 0.7),
    ]
    
    SNIPPET_PATTERNS = [
        (r"^[@;](.+)", 0.95),  # Direct snippet triggers
        (r"^(snippet|snip|paste)\s+(.+)", 0.8),
    ]
    
    SYSTEM_PATTERNS = [
        (r"^(lock|sleep|shutdown|restart|hibernate)", 0.9),
        (r"^(volume|brightness|wifi|bluetooth)\s+(up|down|on|off)", 0.85),
    ]
    
    CLIPBOARD_PATTERNS = [
        (r"^(copy|copiar|paste|pegar)\s+(.+)", 0.85),
        (r"^clip(board)?\s+(.+)", 0.8),
    ]
    
    FILE_ACTION_PATTERNS = [
        (r"^(zip|compress|extract|unzip)\s+(.+)", 0.85),
        (r"^(move|copy|delete|rename)\s+(.+)\s+(to|a)\s+(.+)", 0.85),
    ]
    
    TEXT_TRANSFORM_PATTERNS = [
        (r"^(uppercase|lowercase|capitalize|title)\s+(.+)", 0.9),
        (r"^(clean|limpiar|format|formatear)\s+(.+)", 0.8),
        (r"^(convert|convertir)\s+(.+)\s+(to|a)\s+(.+)", 0.85),
    ]
    
    TRANSLATE_PATTERNS = [
        (r"^(translate|traducir|traduire)\s+(.+)", 0.9),
        (r"^(to|a)\s+(english|spanish|french|german|italian)", 0.8),
    ]
    
    CALCULATE_PATTERNS = [
        # Match math expressions: numbers, operators, parentheses, spaces
        # Must have at least one digit and one operator to be valid
        (r"^\d+[\d+\-*/().\s]*[\d+\-*/()]+[\d+\-*/().\s]*\d+$", 0.7),
        (r"^(calc|calculate|calcula)\s+(.+)", 0.85),
    ]
    
    def __init__(self):
        """Initialize the intent router."""
        pass
    
    def detect_intent(self, query: str) -> Intent:
        """
        Detect the primary intent from a user query.
        
        Args:
            query: User input query
            
        Returns:
            Intent object with detected type and confidence
        """
        query = query.strip()
        qlow = query.lower()
        
        # Check for empty query
        if not query:
            return Intent(IntentType.UNKNOWN, 0.0)
        
        # Check each pattern type
        intents = []
        
        # App opening
        for pattern, confidence in self.APP_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                app_name = match.group(2) if match.lastindex >= 2 else match.group(1)
                intents.append(Intent(IntentType.OPEN_APP, confidence, {"app": app_name}))
        
        # File search
        for pattern, confidence in self.FILE_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                filename = match.group(2) if match.lastindex >= 2 else query
                intents.append(Intent(IntentType.SEARCH_FILE, confidence, {"filename": filename}))
        
        # Snippet paste
        for pattern, confidence in self.SNIPPET_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                trigger = match.group(1) if match.lastindex >= 1 else query
                intents.append(Intent(IntentType.PASTE_SNIPPET, confidence, {"trigger": trigger}))
        
        # System actions
        for pattern, confidence in self.SYSTEM_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                action = match.group(0)
                intents.append(Intent(IntentType.SYSTEM_ACTION, confidence, {"action": action}))
        
        # Clipboard actions
        for pattern, confidence in self.CLIPBOARD_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                text = match.group(2) if match.lastindex >= 2 else ""
                intents.append(Intent(IntentType.CLIPBOARD_ACTION, confidence, {"text": text}))
        
        # File actions
        for pattern, confidence in self.FILE_ACTION_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                action = match.group(1)
                target = match.group(2)
                intents.append(Intent(IntentType.FILE_ACTION, confidence, {"action": action, "target": target}))
        
        # Text transformations
        for pattern, confidence in self.TEXT_TRANSFORM_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                transform = match.group(1)
                text = match.group(2) if match.lastindex >= 2 else ""
                intents.append(Intent(IntentType.TEXT_TRANSFORM, confidence, {"transform": transform, "text": text}))
        
        # Translation
        for pattern, confidence in self.TRANSLATE_PATTERNS:
            if re.search(pattern, qlow):
                match = re.search(pattern, qlow)
                text = match.group(2) if match.lastindex >= 2 else query
                intents.append(Intent(IntentType.TRANSLATE, confidence, {"text": text}))
        
        # Calculate
        for pattern, confidence in self.CALCULATE_PATTERNS:
            if re.fullmatch(pattern, qlow):
                intents.append(Intent(IntentType.CALCULATE, confidence, {"expression": query}))
        
        # Return highest confidence intent
        if intents:
            return max(intents, key=lambda i: i.confidence)
        
        return Intent(IntentType.UNKNOWN, 0.0)
    
    def detect_all_intents(self, query: str) -> List[Intent]:
        """
        Detect all possible intents from a query.
        Useful for compound actions.
        
        Args:
            query: User input query
            
        Returns:
            List of Intent objects sorted by confidence
        """
        # This is a simplified version - implement full detection if needed
        primary = self.detect_intent(query)
        return [primary] if primary.confidence > 0.5 else []
