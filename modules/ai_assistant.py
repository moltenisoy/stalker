"""
Asistente IA con BYOK:
- Proveedor cloud (OpenAI/Anthropic simulado) vía HTTP usando clave BYOK almacenada.
- Proveedor local simulado (ollama) con endpoint HTTP local.
- Acciones contextuales: toma texto del portapapeles (selección) y ejecuta prompt (resumir, traducir, mejorar).
Esta implementación es síncrona y minimalista; agrega colas/async según necesidad.
"""
import os
import requests
from typing import Literal, Optional
from core.storage import Storage

Provider = Literal["openai", "anthropic", "local"]

class AIAssistant:
    def __init__(self, storage: Optional[Storage] = None):
        self.storage = storage or Storage()
        self.local_endpoint = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")

    def set_api_key(self, provider: str, key: str):
        self.storage.set_api_key(provider, key)

    def _get_api_key(self, provider: str) -> Optional[str]:
        return self.storage.get_api_key(provider)

    def ask(self, query: str, provider: Provider = "openai", model: str = "gpt-4o-mini") -> str:
        if provider == "local":
            return self._ask_local(query)
        key = self._get_api_key(provider)
        if not key:
            return "Falta API key para el proveedor."
        if provider == "openai":
            return self._ask_openai(query, key, model)
        if provider == "anthropic":
            return self._ask_anthropic(query, key, model)
        return "Proveedor no soportado."

    def _ask_openai(self, prompt: str, key: str, model: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}"}
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.4}
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as ex:
            return f"Error OpenAI: {ex}"

    def _ask_anthropic(self, prompt: str, key: str, model: str) -> str:
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        payload = {"model": model, "max_tokens": 512, "messages": [{"role": "user", "content": prompt}]}
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            # Assume text in content list
            return "".join(block.get("text", "") for block in data.get("content", []) if isinstance(block, dict))
        except Exception as ex:
            return f"Error Anthropic: {ex}"

    def _ask_local(self, prompt: str, model: str = "llama3") -> str:
        try:
            r = requests.post(self.local_endpoint, json={"model": model, "prompt": prompt, "stream": False}, timeout=15)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "")
        except Exception as ex:
            return f"Error local: {ex}"

    def analyze_clipboard(self, mode: Literal["resume", "traduce", "mejora"] = "resume",
                          provider: Provider = "openai", model: str = "gpt-4o-mini"):
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData()
        finally:
            win32clipboard.CloseClipboard()
        if not text:
            return "Clipboard vacío."
        prompt_map = {
            "resume": f"Resume el siguiente texto en español de forma concisa:\n\n{text}",
            "traduce": f"Traduce al español manteniendo contexto y tono:\n\n{text}",
            "mejora": f"Mejora la redacción y claridad en español:\n\n{text}",
        }
        return self.ask(prompt_map.get(mode, prompt_map["resume"]), provider=provider, model=model)