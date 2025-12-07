import ast
import operator as op
import re
from dataclasses import dataclass
from typing import Optional
from core.types import SearchResult

# Operadores seguros
_ALLOWED = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}

# Tasas mock con cache sencillo (podrías actualizarlas vía API externa)
_CURRENCY_RATES = {
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.09,
    ("USD", "MXN"): 17.0,
    ("MXN", "USD"): 0.059,
    ("EUR", "MXN"): 18.5,
    ("MXN", "EUR"): 0.054,
}

_UNIT_FACTORS = {
    ("m", "cm"): 100.0,
    ("cm", "m"): 0.01,
    ("km", "m"): 1000.0,
    ("m", "km"): 0.001,
    ("kg", "g"): 1000.0,
    ("g", "kg"): 0.001,
}

class Calculator:
    def try_calculate(self, text: str) -> Optional[SearchResult]:
        if not text:
            return None

        # 1) Conversión de moneda: "100 USD a EUR"
        m_currency = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]{3})\s+a\s+([A-Za-z]{3})", text, re.IGNORECASE)
        if m_currency:
            amount = float(m_currency.group(1))
            src = m_currency.group(2).upper()
            dst = m_currency.group(3).upper()
            rate = _CURRENCY_RATES.get((src, dst))
            if rate:
                value = amount * rate
                title = f"{amount:.4g} {src} → {value:.4g} {dst}"
                return SearchResult(title=title, subtitle="Conversión (tasas en caché)", copy_text=f"{value:.6g}", group="calculator")

        # 2) Conversión de unidades: "2.5 km a m"
        m_unit = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)\s+a\s+([A-Za-z]+)", text, re.IGNORECASE)
        if m_unit:
            amount = float(m_unit.group(1))
            src = m_unit.group(2).lower()
            dst = m_unit.group(3).lower()
            factor = _UNIT_FACTORS.get((src, dst))
            if factor:
                value = amount * factor
                title = f"{amount:g} {src} → {value:g} {dst}"
                return SearchResult(title=title, subtitle="Conversión de unidades", copy_text=str(value), group="calculator")

        # 3) Expresión matemática simple al inicio
        if re.match(r"^[\d\(\).\s\+\-\*\/\^%]+$", text):
            try:
                value = self._safe_eval(text.replace("^", "**"))
                return SearchResult(title=f"{value}", subtitle="Resultado de calculadora", copy_text=str(value), group="calculator")
            except Exception:
                return None

        return None

    def _safe_eval(self, expr: str):
        node = ast.parse(expr, mode="eval")
        return self._eval(node.body)

    def _eval(self, node):
        if isinstance(node, ast.Num):  # literal
            return node.n
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ALLOWED:
                raise ValueError("Operador no permitido")
            return _ALLOWED[type(node.op)](self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in _ALLOWED:
                raise ValueError("Operador no permitido")
            return _ALLOWED[type(node.op)](self._eval(node.operand))
        raise ValueError("Expresión no soportada")