"""
Asistente IA con BYOK:
- Proveedor cloud (OpenAI/Anthropic simulado) vía HTTP usando clave BYOK almacenada.
- Proveedor local simulado (ollama) con endpoint HTTP local.
- Acciones contextuales: toma texto del portapapeles (selección) y ejecuta prompt (resumir, traducir, mejorar).
- API keys cifradas con Fernet
- Timeouts y reintentos configurables
- Mensajes de error claros y profesionales
"""
import os
import requests
import time
from typing import Literal, Optional, Tuple
from core.storage import Storage

Provider = Literal["openai", "anthropic", "local"]

class AIAssistant:
    def __init__(self, storage: Optional[Storage] = None, 
                 timeout: int = 30,
                 max_retries: int = 2):
        """
        Initialize AI Assistant with optional encryption and retry logic.
        
        Args:
            storage: Storage instance for API keys
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 2)
        """
        self.storage = storage or Storage()
        self.local_endpoint = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
        self.timeout = timeout
        self.max_retries = max_retries

    def set_api_key(self, provider: str, key: str):
        self.storage.set_api_key(provider, key)

    def _get_api_key(self, provider: str) -> Optional[str]:
        return self.storage.get_api_key(provider)

    def ask(self, query: str, provider: Provider = "openai", model: str = "gpt-4o-mini") -> Tuple[str, bool]:
        """
        Ask AI a question with retry logic.
        
        Returns:
            Tuple of (response_text, success_flag)
        """
        if provider == "local":
            return self._ask_local(query)
        key = self._get_api_key(provider)
        if not key:
            return ("❌ Error: Falta API key para el proveedor. Configure su clave en ajustes.", False)
        if provider == "openai":
            return self._ask_openai(query, key, model)
        if provider == "anthropic":
            return self._ask_anthropic(query, key, model)
        return ("❌ Error: Proveedor no soportado. Use 'openai', 'anthropic' o 'local'.", False)

    def _ask_openai(self, prompt: str, key: str, model: str) -> Tuple[str, bool]:
        """Call OpenAI API with retry logic."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.4}
        
        for attempt in range(self.max_retries + 1):
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                r.raise_for_status()
                data = r.json()
                return (data["choices"][0]["message"]["content"], True)
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                    continue
                return (f"❌ Error: Tiempo de espera agotado después de {self.max_retries + 1} intentos. Verifique su conexión.", False)
            except requests.exceptions.HTTPError as ex:
                if ex.response.status_code == 401:
                    return ("❌ Error: API key inválida. Verifique su clave de OpenAI.", False)
                elif ex.response.status_code == 429:
                    return ("❌ Error: Límite de tasa excedido. Espere un momento e intente nuevamente.", False)
                elif ex.response.status_code >= 500:
                    if attempt < self.max_retries:
                        time.sleep(2 * (attempt + 1))
                        continue
                    return (f"❌ Error del servidor OpenAI ({ex.response.status_code}). Intente más tarde.", False)
                return (f"❌ Error HTTP {ex.response.status_code}: {str(ex)}", False)
            except requests.exceptions.ConnectionError:
                return ("❌ Error: No se pudo conectar a OpenAI. Verifique su conexión a Internet.", False)
            except KeyError:
                return ("❌ Error: Respuesta inesperada de OpenAI. El formato de respuesta ha cambiado.", False)
            except Exception as ex:
                return (f"❌ Error inesperado: {type(ex).__name__}: {str(ex)}", False)
        
        return ("❌ Error: Todos los intentos fallaron.", False)

    def _ask_anthropic(self, prompt: str, key: str, model: str) -> Tuple[str, bool]:
        """Call Anthropic API with retry logic."""
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        payload = {"model": model, "max_tokens": 512, "messages": [{"role": "user", "content": prompt}]}
        
        for attempt in range(self.max_retries + 1):
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                r.raise_for_status()
                data = r.json()
                result = "".join(block.get("text", "") for block in data.get("content", []) if isinstance(block, dict))
                return (result, True)
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(1 * (attempt + 1))
                    continue
                return (f"❌ Error: Tiempo de espera agotado después de {self.max_retries + 1} intentos. Verifique su conexión.", False)
            except requests.exceptions.HTTPError as ex:
                if ex.response.status_code == 401:
                    return ("❌ Error: API key inválida. Verifique su clave de Anthropic.", False)
                elif ex.response.status_code == 429:
                    return ("❌ Error: Límite de tasa excedido. Espere un momento e intente nuevamente.", False)
                elif ex.response.status_code >= 500:
                    if attempt < self.max_retries:
                        time.sleep(2 * (attempt + 1))
                        continue
                    return (f"❌ Error del servidor Anthropic ({ex.response.status_code}). Intente más tarde.", False)
                return (f"❌ Error HTTP {ex.response.status_code}: {str(ex)}", False)
            except requests.exceptions.ConnectionError:
                return ("❌ Error: No se pudo conectar a Anthropic. Verifique su conexión a Internet.", False)
            except KeyError:
                return ("❌ Error: Respuesta inesperada de Anthropic. El formato de respuesta ha cambiado.", False)
            except Exception as ex:
                return (f"❌ Error inesperado: {type(ex).__name__}: {str(ex)}", False)
        
        return ("❌ Error: Todos los intentos fallaron.", False)

    def _ask_local(self, prompt: str, model: str = "llama3") -> Tuple[str, bool]:
        """Call local AI endpoint (e.g., Ollama) with retry logic."""
        for attempt in range(self.max_retries + 1):
            try:
                r = requests.post(
                    self.local_endpoint, 
                    json={"model": model, "prompt": prompt, "stream": False}, 
                    timeout=self.timeout
                )
                r.raise_for_status()
                data = r.json()
                return (data.get("response", ""), True)
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    time.sleep(1 * (attempt + 1))
                    continue
                return (f"❌ Error: Tiempo de espera agotado para el servidor local. Verifique que Ollama esté ejecutándose.", False)
            except requests.exceptions.ConnectionError:
                return (f"❌ Error: No se pudo conectar al servidor local en {self.local_endpoint}. Verifique que Ollama esté ejecutándose.", False)
            except requests.exceptions.HTTPError as ex:
                return (f"❌ Error del servidor local ({ex.response.status_code}): {str(ex)}", False)
            except Exception as ex:
                return (f"❌ Error inesperado: {type(ex).__name__}: {str(ex)}", False)
        
        return ("❌ Error: Todos los intentos fallaron.", False)

    def analyze_clipboard(self, mode: Literal["resume", "traduce", "mejora"] = "resume",
                          provider: Provider = "openai", model: str = "gpt-4o-mini") -> Tuple[str, bool]:
        """
        Analyze clipboard content with AI.
        
        Returns:
            Tuple of (response_text, success_flag)
        """
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData()
        except Exception as ex:
            return (f"❌ Error al leer el portapapeles: {str(ex)}", False)
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        
        if not text or not text.strip():
            return ("❌ El portapapeles está vacío. Copie algún texto primero.", False)
        
        prompt_map = {
            "resume": f"Resume el siguiente texto en español de forma concisa:\n\n{text}",
            "traduce": f"Traduce al español manteniendo contexto y tono:\n\n{text}",
            "mejora": f"Mejora la redacción y claridad en español:\n\n{text}",
        }
        return self.ask(prompt_map.get(mode, prompt_map["resume"]), provider=provider, model=model)