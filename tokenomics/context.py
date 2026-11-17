"""Tokenomics Context Detection v2.0 — Agentic-aware content classification.

Detects content type to apply the right compression strategy.
Not just "is this code?" — understands code vs docs vs secrets vs config vs prose.
"""

from __future__ import annotations

import re
from typing import Any

CONTEXT_PATTERNS: dict[str, list[str]] = {
    "code": [
        r"def\s+\w+", r"class\s+\w+", r"import\s+\w+", r"from\s+\w+\s+import",
        r"function\s+\w+", r"const\s+\w+", r"let\s+\w+", r"public\s+",
        r"private\s+", r"->\s*\w+", r":\s*\w+\s*=>",
        r"if\s+\w+", r"for\s+\w+", r"while\s+\w+", r"return\s+",
    ],
    "config": [
        r"^\s*\w+\s*=\s*", r"^\s*\[.*\]\s*$", r"^\s*#.*=.*$",
        r"yaml:", r"json:", r"toml:", r"ini:", r"\.env",
    ],
    "secrets": [
        r"api[_-]?key", r"secret[_-]?key", r"password",
        r"private[_-]?key", r"access[_-]?token", r"auth[_-]?token",
        r"sk-[A-Za-z0-9]{20,}", r"ghp_[A-Za-z0-9]{36,}",
    ],
    "docs": [
        r"^#+\s", r"^\*\*.*\*\*$", r"\[.*\]\(.*\)", r"---",
        r"README", r"CHANGELOG", r"docs/",
    ],
    "sql": [
        r"SELECT\s+", r"INSERT\s+INTO", r"UPDATE\s+", r"DELETE\s+FROM",
        r"CREATE\s+TABLE", r"DROP\s+", r"ALTER\s+TABLE",
    ],
}


def detect_context(text: str) -> str:
    """Detect content type for targeted compression strategy.

    Returns one of: code, config, secrets, docs, sql, prose
    """
    scores: dict[str, int] = dict.fromkeys(CONTEXT_PATTERNS, 0)
    for context, patterns in CONTEXT_PATTERNS.items():
        for pattern in patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))
            scores[context] += matches

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "prose"
    return best


def is_security_sensitive(text: str) -> bool:
    """Check if text contains secrets/auth/crypto that should never be compressed."""
    return bool(re.search(
        r"api[_-]?key|secret[_-]?key|password|private[_-]?key|"
        r"access[_-]?token|auth[_-]?token|sk-[A-Za-z0-9]{20,}|"
        r"ghp_[A-Za-z0-9]{36,}|jwt|oauth|session|csrf|encrypt|decrypt",
        text, re.IGNORECASE
    ))


def compression_strategy_for(text: str) -> dict[str, Any]:
    """Determine the best compression strategy for a given text.

    Returns dict with context, preset_name, should_compress, reason.
    """
    context = detect_context(text)

    # Secrets are never compressed
    if context == "secrets" or is_security_sensitive(text):
        return {
            "context": context,
            "preset": "secrets",
            "should_compress": False,
            "reason": "Security-sensitive content — never compressed",
        }

    # Code gets minimal compression (structure matters)
    if context == "code":
        return {
            "context": context,
            "preset": "code",
            "should_compress": True,
            "reason": "Code — minimal compression, structure preserved",
        }

    # Config gets light compression
    if context == "config":
        return {
            "context": context,
            "preset": "standard",
            "should_compress": True,
            "reason": "Config — light compression",
        }

    # Docs get moderate compression
    if context == "docs":
        return {
            "context": context,
            "preset": "docs",
            "should_compress": True,
            "reason": "Docs — moderate compression",
        }

    # SQL gets light compression (structure matters)
    if context == "sql":
        return {
            "context": context,
            "preset": "standard",
            "should_compress": True,
            "reason": "SQL — light compression, syntax preserved",
        }

    # Default prose gets standard compression
    return {
        "context": context,
        "preset": "standard",
        "should_compress": True,
        "reason": "Prose — standard compression",
    }
