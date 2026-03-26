from __future__ import annotations

import re
from dataclasses import dataclass

CURRENCY_SYMBOLS: dict[str, str] = {
    "€": "EUR",
    "eur": "EUR",
    "₽": "RUB",
    "руб": "RUB",
    "р": "RUB",
    "rub": "RUB",
    "zł": "PLN",
    "zl": "PLN",
    "pln": "PLN",
    "$": "USD",
    "usd": "USD",
    "£": "GBP",
    "gbp": "GBP",
    "czk": "CZK",
    "kč": "CZK",
}

# Amount pattern: digits with optional decimal (comma or dot)
_AMT = r"(\d+(?:[.,]\d{1,2})?)"
# Currency symbol/code pattern
_CUR = r"([€₽$£]|eur|rub|руб|р|pln|zł|zl|usd|gbp|czk|kč)"

# Patterns tried in order — amount first, then amount last
_PATTERNS = [
    # "500€ lidl" or "500 eur lidl" or "500€" — amount + currency + optional description
    re.compile(rf"^{_AMT}\s*{_CUR}\s*(.*)$", re.IGNORECASE),
    # "500 lidl" — amount + description (no currency)
    re.compile(rf"^{_AMT}\s+(.+)$"),
    # "lidl 500€" or "lidl 500 eur" — description + amount + currency
    re.compile(rf"^(.+?)\s+{_AMT}\s*{_CUR}?\s*$", re.IGNORECASE),
    # "500" — just amount
    re.compile(rf"^{_AMT}\s*{_CUR}?\s*$", re.IGNORECASE),
]


@dataclass
class ParsedExpense:
    amount: float
    currency: str | None  # None means use user's default
    description: str


def parse_expense(text: str) -> ParsedExpense | None:
    """Parse a text message into an expense. Returns None if not parseable."""
    text = text.strip()
    if not text:
        return None

    # Pattern 1: amount + currency + description  "500€ lidl"
    m = _PATTERNS[0].match(text)
    if m:
        amount = _parse_amount(m.group(1))
        currency = _resolve_currency(m.group(2))
        desc = m.group(3).strip()
        return ParsedExpense(amount=amount, currency=currency, description=desc)

    # Pattern 2: amount + description (no currency)  "500 lidl"
    m = _PATTERNS[1].match(text)
    if m:
        amount = _parse_amount(m.group(1))
        desc = m.group(2).strip()
        # Check if first word of desc is a currency code
        parts = desc.split(None, 1)
        if parts and parts[0].lower() in CURRENCY_SYMBOLS:
            currency = _resolve_currency(parts[0])
            desc = parts[1] if len(parts) > 1 else ""
            return ParsedExpense(amount=amount, currency=currency, description=desc.strip())
        return ParsedExpense(amount=amount, currency=None, description=desc)

    # Pattern 3: description + amount + optional currency  "lidl 500€"
    m = _PATTERNS[2].match(text)
    if m:
        desc = m.group(1).strip()
        amount = _parse_amount(m.group(2))
        currency = _resolve_currency(m.group(3)) if m.group(3) else None
        return ParsedExpense(amount=amount, currency=currency, description=desc)

    # Pattern 4: just amount + optional currency  "500" or "500€"
    m = _PATTERNS[3].match(text)
    if m:
        amount = _parse_amount(m.group(1))
        currency = _resolve_currency(m.group(2)) if m.group(2) else None
        return ParsedExpense(amount=amount, currency=currency, description="")

    return None


def _parse_amount(s: str) -> float:
    return float(s.replace(",", "."))


def _resolve_currency(s: str) -> str:
    return CURRENCY_SYMBOLS.get(s.lower(), s.upper())
