"""Core Tokenomics logic: caveman compression, ponytail ladder, token estimation."""

from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Caveman compression rules
# ---------------------------------------------------------------------------

_ARTICLES = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)
_FILLER = re.compile(
    r"\b(just|really|basically|actually|simply|quite|rather|very|pretty|totally|"
    r"completely|absolutely|literally|figuratively|honestly|seriously)\b",
    re.IGNORECASE,
)
_PLEASANTRIES = re.compile(
    r"\b(sure|certainly|of course|happy to|glad to|you're welcome|no problem|"
    r"my pleasure|not at all|don't mention it|anytime)\b",
    re.IGNORECASE,
)
_HEDGING = re.compile(
    r"\b(maybe|possibly|perhaps|I think|I believe|it seems|it appears|likely|"
    r"probably|I guess|I suppose|sort of|kind of|maybe)\b",
    re.IGNORECASE,
)

_SHORT_SYNONYMS = {
    "implement": "build",
    "implementation": "build",
    "utilize": "use",
    "utilisation": "use",
    "facilitate": "help",
    "demonstrate": "show",
    "commence": "start",
    "terminate": "end",
    "approximately": "approx",
    "additional": "extra",
    "substantial": "big",
    "significant": "big",
    "numerous": "many",
    "sufficient": "enough",
    "require": "need",
    "requirement": "need",
    "modify": "change",
    "modification": "change",
    "configure": "set",
    "configuration": "config",
    "parameter": "param",
    "argument": "arg",
    "variable": "var",
    "function": "fn",
    "procedure": "proc",
    "method": "meth",
    "component": "comp",
    "element": "el",
    "reference": "ref",
}

_ABBREVIATIONS = {
    "database": "DB",
    "authentication": "auth",
    "authorization": "auth",
    "configuration": "config",
    "configure": "cfg",
    "request": "req",
    "response": "res",
    "function": "fn",
    "implementation": "impl",
    "approximately": "approx",
    "application": "app",
    "environment": "env",
    "variable": "var",
    "parameter": "param",
    "argument": "arg",
    "reference": "ref",
    "temporary": "tmp",
    "development": "dev",
    "production": "prod",
    "staging": "stag",
}

_TECHNICAL_TERMS = {
    "api", "http", "https", "json", "xml", "yaml", "toml", "csv", "sql",
    "rest", "graphql", "grpc", "websocket", "tcp", "udp", "ip", "dns",
    "ssl", "tls", "oauth", "jwt", "uuid", "uri", "url", "cdn", "s3",
    "ec2", "lambda", "k8s", "docker", "ci", "cd", "devops", "sre",
    "ui", "ux", "api-key", "api_key", "access-token", "refresh-token",
    "cli", "gui", "ide", "sdk", "api-gateway", "load-balancer",
}

_PROTECT_PHRASES = [
    "API key", "access token", "refresh token", "load balancer",
    "API gateway", "CI/CD", "DevOps", "UI/UX", "standard library",
]


def _is_technical(word: str) -> bool:
    return word.lower() in _TECHNICAL_TERMS


def _protect_code_blocks(text: str) -> tuple[str, list[str]]:
    """Extract code blocks so they aren't compressed."""
    blocks: list[str] = []
    pattern = re.compile(r"```[\s\S]*?```|`[^`]+`")

    def repl(m: re.Match[str]) -> str:
        blocks.append(m.group(0))
        return f"\n\x00CODE_BLOCK_{len(blocks) - 1}\x00\n"

    return pattern.sub(repl, text), blocks


def _restore_code_blocks(text: str, blocks: list[str]) -> str:
    for i, block in enumerate(blocks):
        text = text.replace(f"\n\x00CODE_BLOCK_{i}\x00\n", f"\n{block}\n")
    return text


def compress_prose(text: str) -> str:
    """Apply caveman compression to prose while protecting code/tech terms."""
    if not text:
        return text

    text, blocks = _protect_code_blocks(text)

    protected: list[str] = []
    for phrase in _PROTECT_PHRASES:
        placeholder = f"\x00PROTECT_{len(protected)}\x00"
        text = text.replace(phrase, placeholder)
        protected.append(phrase)

    text = _ARTICLES.sub(" ", text)
    text = _FILLER.sub(" ", text)
    text = _PLEASANTRIES.sub(" ", text)
    text = _HEDGING.sub(" ", text)

    for long_form, short_form in _SHORT_SYNONYMS.items():
        text = re.sub(
            r"\b" + re.escape(long_form) + r"\b",
            short_form,
            text,
            flags=re.IGNORECASE,
        )

    for long_form, short_form in _ABBREVIATIONS.items():
        text = re.sub(
            r"\b" + re.escape(long_form) + r"\b",
            short_form,
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(r"\s+", " ", text).strip()

    for i, phrase in enumerate(protected):
        text = text.replace(f"\x00PROTECT_{i}\x00", phrase)

    text = _restore_code_blocks(text, blocks)

    return text


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token."""
    if not text:
        return 0
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Ponytail ladder
# ---------------------------------------------------------------------------

PONYTAIL_LADDER = [
    "Does this need to exist? (YAGNI — skip it)",
    "Already in this codebase? (reuse it)",
    "Stdlib does it? (use it)",
    "Native platform feature? (use it)",
    "Installed dependency solves it? (use it)",
    "Can it be one line? (write one line)",
    "Only then: minimum code that works",
]


def ponytail_ladder() -> str:
    """Return the ponytail YAGNI decision ladder as formatted text."""
    lines = ["[TOKENOMICS / PONYTAIL] Lazy-senior-dev mode active."]
    lines.append("Before writing any code, climb the ladder and stop at the first rung that holds:")
    for i, rung in enumerate(PONYTAIL_LADDER, 1):
        lines.append(f"{i}. {rung}")
    lines.append("Never cut validation, error handling, security, or accessibility.")
    return "\n".join(lines)


def review_code(code: str) -> dict[str, Any]:
    """Ponytail-style code review: detect over-engineering and estimate compression."""
    if not code:
        return {"ok": False, "error": "code is required for review"}

    issues: list[str] = []

    if len(code.split("\n")) > 50:
        issues.append("File is over 50 lines — consider splitting or simplifying")

    if re.search(r"class.*Factory|class.*Manager|class.*Service|class.*Controller", code, re.IGNORECASE):
        issues.append("Possible unnecessary abstraction layer — consider simpler functions")

    if re.search(r"import.*\*\s*from", code):
        issues.append("Wildcard import detected — consider explicit imports")

    max_indent = 0
    for line in code.split("\n"):
        indent = len(line) - len(line.lstrip())
        max_indent = max(max_indent, indent)
    if max_indent > 16:
        issues.append(f"Deep nesting ({max_indent // 4} levels) — consider extracting functions")

    compressed = compress_prose(code)
    orig_tokens = estimate_tokens(code)
    comp_tokens = estimate_tokens(compressed)

    return {
        "ok": True,
        "issues": issues,
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "estimated_savings": max(0, orig_tokens - comp_tokens),
        "recommendation": "Apply ponytail ladder: YAGNI → reuse → stdlib → native → dep → one line → minimum",
        "compressed_preview": compressed[:300],
    }
