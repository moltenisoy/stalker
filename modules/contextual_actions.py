"""
Contextual Actions - One-tap actions based on active window and selection.
Provides quick actions for text/selection in the active application.
"""
import re
import win32clipboard
import win32gui
from typing import List, Optional, Dict
from core.engine import SearchResult
from modules.keystroke import send_text_ime_safe

class ContextualActionsManager:
    """
    Manages contextual actions based on active window and clipboard content.
    Provides one-tap actions for common text operations.
    """
    
    def __init__(self):
        self.last_clipboard = ""
        self.active_window_title = ""
        self.active_window_class = ""
    
    def update_active_window(self):
        """Update information about the active window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            self.active_window_title = win32gui.GetWindowText(hwnd)
            self.active_window_class = win32gui.GetClassName(hwnd)
        except Exception as e:
            print(f"Error getting active window: {e}")
    
    def get_clipboard_content(self) -> str:
        """Get current clipboard content."""
        try:
            win32clipboard.OpenClipboard()
            content = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return content
        except Exception as e:
            print(f"Error reading clipboard: {e}")
            return ""
    
    def set_clipboard_content(self, text: str):
        """Set clipboard content."""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error setting clipboard: {e}")
    
    def get_available_actions(self, query: str = "") -> List[SearchResult]:
        """
        Get available contextual actions based on current context.
        
        Args:
            query: Optional search query to filter actions
            
        Returns:
            List of available actions as SearchResults
        """
        self.update_active_window()
        clipboard_content = self.get_clipboard_content()
        
        actions = []
        
        # Always available actions
        actions.extend(self._get_paste_actions(clipboard_content))
        
        # Text transformation actions
        if clipboard_content and clipboard_content.strip():
            actions.extend(self._get_transform_actions(clipboard_content))
            actions.extend(self._get_format_actions(clipboard_content))
            actions.extend(self._get_extraction_actions(clipboard_content))
        
        # Filter by query if provided
        if query:
            qlow = query.lower()
            actions = [a for a in actions if qlow in a.title.lower() or qlow in a.subtitle.lower()]
        
        return actions
    
    def _get_paste_actions(self, clipboard_content: str) -> List[SearchResult]:
        """Get paste-related actions."""
        actions = []
        
        # Paste plain text (without formatting)
        actions.append(SearchResult(
            title="📋 Pegar Texto Plano",
            subtitle="Pegar sin formato (IME-safe)",
            action=lambda: self._paste_plain(),
            group="context_paste"
        ))
        
        # Paste and go (for URLs)
        if self._is_url(clipboard_content):
            actions.append(SearchResult(
                title="🌐 Pegar y Navegar",
                subtitle="Pegar URL y presionar Enter",
                action=lambda: self._paste_and_go(),
                group="context_paste"
            ))
        
        return actions
    
    def _get_transform_actions(self, text: str) -> List[SearchResult]:
        """Get text transformation actions."""
        actions = []
        
        # Uppercase
        actions.append(SearchResult(
            title="🔠 MAYÚSCULAS",
            subtitle=f"Convertir a mayúsculas: {text[:50]}...",
            action=lambda: self._transform_and_paste(text, "uppercase"),
            group="context_transform"
        ))
        
        # Lowercase
        actions.append(SearchResult(
            title="🔡 minúsculas",
            subtitle=f"Convertir a minúsculas: {text[:50]}...",
            action=lambda: self._transform_and_paste(text, "lowercase"),
            group="context_transform"
        ))
        
        # Title Case
        actions.append(SearchResult(
            title="🔤 Título",
            subtitle=f"Convertir a Título: {text[:50]}...",
            action=lambda: self._transform_and_paste(text, "title"),
            group="context_transform"
        ))
        
        return actions
    
    def _get_format_actions(self, text: str) -> List[SearchResult]:
        """Get formatting actions."""
        actions = []
        
        # Clean format (remove extra spaces, special chars)
        actions.append(SearchResult(
            title="✨ Limpiar Formato",
            subtitle="Eliminar formato, espacios extra y caracteres especiales",
            action=lambda: self._clean_and_paste(text),
            group="context_format"
        ))
        
        # Remove line breaks
        if '\n' in text or '\r' in text:
            actions.append(SearchResult(
                title="📏 Unir Líneas",
                subtitle="Eliminar saltos de línea",
                action=lambda: self._remove_linebreaks_and_paste(text),
                group="context_format"
            ))
        
        # Quote text
        actions.append(SearchResult(
            title='💬 Entrecomillar',
            subtitle='Agregar comillas alrededor del texto',
            action=lambda: self._quote_and_paste(text),
            group="context_format"
        ))
        
        return actions
    
    def _get_extraction_actions(self, text: str) -> List[SearchResult]:
        """Get extraction actions."""
        actions = []
        
        # Extract URLs
        urls = self._extract_urls(text)
        if urls:
            actions.append(SearchResult(
                title=f"🔗 Extraer Enlaces ({len(urls)})",
                subtitle="Extraer todos los URLs del texto",
                action=lambda: self._extract_and_paste(text, "urls"),
                group="context_extract"
            ))
        
        # Extract emails
        emails = self._extract_emails(text)
        if emails:
            actions.append(SearchResult(
                title=f"📧 Extraer Emails ({len(emails)})",
                subtitle="Extraer todas las direcciones de email",
                action=lambda: self._extract_and_paste(text, "emails"),
                group="context_extract"
            ))
        
        # Extract numbers
        numbers = self._extract_numbers(text)
        if numbers:
            actions.append(SearchResult(
                title=f"🔢 Extraer Números ({len(numbers)})",
                subtitle="Extraer todos los números",
                action=lambda: self._extract_and_paste(text, "numbers"),
                group="context_extract"
            ))
        
        # Table to CSV (if text looks like a table)
        if self._looks_like_table(text):
            actions.append(SearchResult(
                title="📊 Convertir a CSV",
                subtitle="Convertir tabla a formato CSV",
                action=lambda: self._table_to_csv_and_paste(text),
                group="context_extract"
            ))
        
        return actions
    
    # Action implementations
    
    def _paste_plain(self):
        """Paste plain text without formatting."""
        text = self.get_clipboard_content()
        if text:
            send_text_ime_safe(text)
    
    def _paste_and_go(self):
        """Paste and press Enter (useful for URLs)."""
        text = self.get_clipboard_content()
        if text:
            send_text_ime_safe(text)
            import keyboard
            keyboard.send('enter')
    
    def _transform_and_paste(self, text: str, transform_type: str):
        """Transform text and paste."""
        if transform_type == "uppercase":
            result = text.upper()
        elif transform_type == "lowercase":
            result = text.lower()
        elif transform_type == "title":
            result = text.title()
        else:
            result = text
        
        send_text_ime_safe(result)
    
    def _clean_and_paste(self, text: str):
        """Clean formatting and paste."""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = cleaned.strip()
        
        # Remove common special characters that cause issues
        cleaned = cleaned.replace('\u200b', '')  # Zero-width space
        cleaned = cleaned.replace('\ufeff', '')  # BOM
        
        send_text_ime_safe(cleaned)
    
    def _remove_linebreaks_and_paste(self, text: str):
        """Remove line breaks and paste."""
        result = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        result = re.sub(r'\s+', ' ', result).strip()
        send_text_ime_safe(result)
    
    def _quote_and_paste(self, text: str):
        """Add quotes around text and paste."""
        result = f'"{text}"'
        send_text_ime_safe(result)
    
    def _extract_and_paste(self, text: str, extract_type: str):
        """Extract specific content and paste."""
        if extract_type == "urls":
            items = self._extract_urls(text)
        elif extract_type == "emails":
            items = self._extract_emails(text)
        elif extract_type == "numbers":
            items = self._extract_numbers(text)
        else:
            items = []
        
        result = '\n'.join(items)
        send_text_ime_safe(result)
    
    def _table_to_csv_and_paste(self, text: str):
        """Convert table-like text to CSV and paste."""
        lines = text.split('\n')
        csv_lines = []
        
        for line in lines:
            # Try to detect separator (tab, multiple spaces, pipe)
            if '\t' in line:
                cells = line.split('\t')
            elif '|' in line:
                cells = [c.strip() for c in line.split('|') if c.strip()]
            else:
                cells = re.split(r'\s{2,}', line)
            
            # Quote cells that contain commas
            quoted_cells = [f'"{cell}"' if ',' in cell else cell for cell in cells]
            csv_lines.append(','.join(quoted_cells))
        
        result = '\n'.join(csv_lines)
        send_text_ime_safe(result)
    
    # Helper methods
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a URL."""
        from core.patterns import is_url
        return is_url(text)
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        from core.patterns import extract_urls
        return extract_urls(text)
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        from core.patterns import extract_emails
        return extract_emails(text)
    
    def _extract_numbers(self, text: str) -> List[str]:
        """Extract numbers from text."""
        from core.patterns import extract_numbers
        return extract_numbers(text)
    
    def _looks_like_table(self, text: str) -> bool:
        """Check if text looks like a table."""
        lines = text.split('\n')
        if len(lines) < 2:
            return False
        
        # Check if multiple lines have tabs or multiple spaces (suggesting columns)
        table_lines = 0
        for line in lines:
            if '\t' in line or re.search(r'\s{2,}', line) or '|' in line:
                table_lines += 1
        
        return table_lines >= len(lines) * 0.5  # At least 50% of lines look like table rows
