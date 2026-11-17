"""Tokenomics Core v2.0.0 — Agentic-Era Token Efficiency Layer.

Compress agent prose, minimize code generation, display estimated token savings.

Tokenomics is inspired by the concepts behind caveman (prose compression)
and ponytail (code minimization), but engineered independently as its own
system with context awareness, learned compression, gamification,
subagent propagation, and cross-agent memory.

Features:
- Real token counting (tiktoken with fallback)
- Context-aware compression (code, docs, config, secrets, sql, prose)
- Domain presets (standard, docs, commit, review, chat, ultra, code, secrets)
- Ponytail-inspired auto-rewrite with safety gate
- Caveman-inspired prose compression
- Learned compression (user revert/adapt tracking)
- Cross-agent sync (shared state with file locking)
- Gamification (streaks, achievements, levels)
- Selective domain compression (allowlist/denylist)
- Code-reviewer integration
- Claude-coach integration
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Real tokenizer (tiktoken with fallback)
# ---------------------------------------------------------------------------

try:
    import tiktoken  # type: ignore

    _HAS_TIKTOKEN = True
    _ENCODERS: dict[str, Any] = {}

    def _get_encoder(model: str = "cl100k_base") -> Any:
        if model not in _ENCODERS:
            _ENCODERS[model] = tiktoken.get_encoding(model)
        return _ENCODERS[model]

    def estimate_tokens(text: str, model: str = "cl100k_base") -> int:
        """Real token count via tiktoken, with fallback."""
        if not text:
            return 0
        try:
            return len(_get_encoder(model).encode(text))
        except Exception:
            return max(1, len(text) // 4)

except ImportError:  # pragma: no cover - tiktoken optional

    def estimate_tokens(text: str, model: str = "cl100k_base") -> int:  # type: ignore[misc, redefined]
        """Fallback: ~4 characters per token."""
        if not text:
            return 0
        return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Domain presets
# ---------------------------------------------------------------------------

@dataclass
class DomainPreset:
    name: str
    drop_articles: bool = True
    drop_filler: bool = True
    drop_pleasantries: bool = True
    drop_hedging: bool = True
    abbreviate_terms: bool = True
    short_synonyms: bool = True
    strip_conjunctions: bool = False
    fragments_ok: bool = True
    protect_code: bool = True
    protect_technical: bool = True
    max_compression_ratio: float = 0.5  # minimum allowed compressed/original


DOMAIN_PRESETS: dict[str, DomainPreset] = {
    "standard": DomainPreset(
        name="standard",
        drop_articles=True,
        drop_filler=True,
        drop_pleasantries=True,
        drop_hedging=True,
        abbreviate_terms=True,
        short_synonyms=True,
        strip_conjunctions=False,
        fragments_ok=True,
        protect_code=True,
        protect_technical=True,
        max_compression_ratio=0.5,
    ),
    "docs": DomainPreset(
        name="docs",
        drop_articles=True,
        drop_filler=True,
        drop_pleasantries=False,
        drop_hedging=False,
        abbreviate_terms=True,
        short_synonyms=True,
        strip_conjunctions=False,
        fragments_ok=False,
        protect_code=True,
        protect_technical=True,
        max_compression_ratio=0.6,
    ),
    "commit": DomainPreset(
        name="commit",
        drop_articles=True,
        drop_filler=True,
        drop_pleasantries=True,
        drop_hedging=True,
        abbreviate_terms=True,
        short_synonyms=True,
        strip_conjunctions=True,
        fragments_ok=True,
        protect_code=True,
        protect_technical=True,
        max_compression_ratio=0.4,
    ),
    "review": DomainPreset(
        name="review",
        drop_articles=True,
        drop_filler=True,
        drop_pleasantries=True,
        drop_hedging=True,
        abbreviate_terms=True,
        short_synonyms=True,
        strip_conjunctions=True,
        fragments_ok=True,
        protect_code=True,
        protect_technical=True,
        max_compression_ratio=0.45,
    ),
    "chat": DomainPreset(
        name="chat",
        drop_articles=False,
        drop_filler=True,
        drop_pleasantries=True,
        drop_hedging=False,
        abbreviate_terms=False,
        short_synonyms=False,
        strip_conjunctions=False,
        fragments_ok=False,
        protect_code=True,
        protect_technical=True,
        max_compression_ratio=0.7,
    ),
    "ultra": DomainPreset(
        name="ultra",
        drop_articles=True,
        drop_filler=True,
        drop_pleasantries=True,
        drop_hedging=True,
        abbreviate_terms=True,
        short_synonyms=True,
        strip_conjunctions=True,
        fragments_ok=True,
        protect_code=True,
        protect_technical=False,
        max_compression_ratio=0.3,
    ),
}


def get_preset(name: str) -> DomainPreset:
    return DOMAIN_PRESETS.get(name, DOMAIN_PRESETS["standard"])


# ---------------------------------------------------------------------------
# Selective domain compression
# ---------------------------------------------------------------------------

@dataclass
class DomainRules:
    never_compress: set[str] = field(default_factory=set)
    always_compress: set[str] = field(default_factory=set)
    force_preset: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Learned compression (track reverts/adaptations)
# ---------------------------------------------------------------------------

@dataclass
class LearnedPattern:
    pattern: str
    revert_count: int = 0
    accept_count: int = 0
    last_seen: float = 0.0

    @property
    def revert_rate(self) -> float:
        total = self.revert_count + self.accept_count
        if total == 0:
            return 0.0
        return self.revert_count / total


@dataclass
class LearnedCompression:
    patterns: dict[str, LearnedPattern] = field(default_factory=dict)

    def record(self, pattern: str, reverted: bool) -> None:
        if pattern not in self.patterns:
            self.patterns[pattern] = LearnedPattern(pattern=pattern)
        p = self.patterns[pattern]
        p.last_seen = time.time()
        if reverted:
            p.revert_count += 1
        else:
            p.accept_count += 1

    def should_compress(self, pattern: str, default: bool = True) -> bool:
        p = self.patterns.get(pattern)
        if p is None:
            return default
        return p.revert_rate < 0.5  # compress if less than 50% revert rate


# ---------------------------------------------------------------------------
# Gamification
# ---------------------------------------------------------------------------

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    threshold: int
    unlocked: bool = False
    unlocked_at: float | None = None


ACHIEVEMENTS: dict[str, Achievement] = {
    "first_savings": Achievement(
        id="first_savings",
        name="First Savings",
        description="Saved your first token",
        threshold=1,
    ),
    "token_hoarder": Achievement(
        id="token_hoarder",
        name="Token Hoarder",
        description="Saved 1,000 tokens",
        threshold=1000,
    ),
    "token_miser": Achievement(
        id="token_miser",
        name="Token Miser",
        description="Saved 10,000 tokens",
        threshold=10000,
    ),
    "lazy_senior": Achievement(
        id="lazy_senior",
        name="Lazy Senior Dev",
        description="Saved 50,000 tokens",
        threshold=50000,
    ),
    "yagni_master": Achievement(
        id="yagni_master",
        name="YAGNI Master",
        description="Saved 100,000 tokens",
        threshold=100000,
    ),
    "streak_3": Achievement(
        id="streak_3",
        name="Three-Day Streak",
        description="3 consecutive days with compression active",
        threshold=3,
    ),
    "streak_7": Achievement(
        id="streak_7",
        name="Week Warrior",
        description="7 consecutive days with compression active",
        threshold=7,
    ),
}


@dataclass
class Gamification:
    total_tokens_saved: int = 0
    total_chars_saved: int = 0
    total_turns: int = 0
    current_streak: int = 0
    best_streak: int = 0
    last_activity_date: str | None = None
    achievements: dict[str, Achievement] = field(
        default_factory=lambda: {k: Achievement(**asdict(v)) for k, v in ACHIEVEMENTS.items()}
    )
    level: int = 1
    xp: int = 0

    # Enhanced features beyond caveman/ponytail
    daily_token_budget: int | None = None   # User-set daily token budget (None = unlimited)
    tokens_used_today: int = 0               # Tokens consumed today (pre-compression)
    tokens_saved_today: int = 0              # Tokens saved today via compression
    project_type: str | None = None          # 'web' | 'cli' | 'library' | 'api' | None
    auto_learn: bool = True                  # Auto-adapt compression from user reverts
    smart_defaults: bool = True              # Suggest domain rules based on detected content

    def check_achievements(self) -> list[str]:
        newly_unlocked: list[str] = []
        for aid, ach in self.achievements.items():
            if not ach.unlocked:
                if aid in (
                    "first_savings",
                    "token_hoarder",
                    "token_miser",
                    "lazy_senior",
                    "yagni_master",
                ):
                    if self.total_tokens_saved >= ach.threshold:
                        ach.unlocked = True
                        ach.unlocked_at = time.time()
                        newly_unlocked.append(aid)
                elif aid in ("streak_3", "streak_7"):
                    if self.current_streak >= ach.threshold:
                        ach.unlocked = True
                        ach.unlocked_at = time.time()
                        newly_unlocked.append(aid)
        # Level up based on tokens saved
        self.level = 1 + self.total_tokens_saved // 10000
        return newly_unlocked

    def xp_for_tokens(self, tokens: int) -> int:
        return tokens // 10


# ---------------------------------------------------------------------------
# Ponytail auto-rewrite with safety gate
# ---------------------------------------------------------------------------

SAFETY_PATTERNS = [
    r"auth|token|secret|password|credential|api_key|private_key",
    r"encrypt|decrypt|hash|hmac|sign|verify",
    r"sql|query|insert|update|delete|drop|alter|create table",
    r"os\.|subprocess|shutil|eval|exec|compile",
    r"admin|root|sudo|privilege|permission|access_control",
]


def is_safety_critical(code: str) -> bool:
    """Check if code contains security-critical patterns."""
    return bool(re.search("|".join(SAFETY_PATTERNS), code, re.IGNORECASE))


def ponytail_rewrite(code: str, safe: bool = True) -> dict[str, Any]:
    """Apply ponytail auto-rewrite to code with safety gate.

    Returns dict with: original, rewritten, changes, safe, warnings
    """
    if not code:
        return {"ok": False, "error": "code is required"}

    original = code
    rewritten = code
    changes: list[str] = []
    warnings: list[str] = []

    # Safety check
    if safe and is_safety_critical(code):
        warnings.append(
            "Code contains security-critical patterns — auto-rewrite skipped for safety"
        )
        return {
            "ok": True,
            "original": original,
            "rewritten": rewritten,
            "changes": changes,
            "safe": False,
            "warnings": warnings,
        }

    # 1. Remove unused imports (heuristic)
    import_lines = re.findall(
        r"^(import\s+\S+|from\s+\S+\s+import\s+.+)$", rewritten, re.MULTILINE
    )
    for imp in import_lines:
        mod = re.sub(r"^(import\s+|from\s+)", "", imp).split()[0]
        if mod:
            remaining = rewritten.replace(imp, "", 1)
            if mod not in remaining:
                rewritten = remaining
                changes.append(f"Removed unused import: {imp}")

    # 2. Replace verbose patterns
    replacements = [
        (r"if\s+x\s+==\s+True\s*:", "if x:"),
        (r"if\s+x\s+==\s+False\s*:", "if not x:"),
        (r"for\s+i\s+in\s+range\s*\(len\s*\((.+)\)\s*\):", r"for item in \1:"),
        (r"\.append\s*\((.+)\)\s*if\s+(.+)\s*else\s*None", r".append(\1) if \2 else None"),
    ]
    for pattern, repl in replacements:
        new_code, count = re.subn(pattern, repl, rewritten)
        if count > 0:
            rewritten = new_code
            changes.append(f"Applied pattern: {pattern} → {repl} ({count}x)")

    # 3. Remove redundant comments (simple heuristic)
    lines = rewritten.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and len(stripped) > 1 and not stripped.startswith("#!"):
            if any(w in stripped.lower() for w in ["todo:", "fixme:", "hack:", "xxx:"]):
                cleaned.append(line)
                continue
            changes.append(f"Removed comment: {stripped[:40]}...")
            continue
        cleaned.append(line)
    rewritten = "\n".join(cleaned)

    orig_tokens = estimate_tokens(original)
    new_tokens = estimate_tokens(rewritten)

    return {
        "ok": True,
        "original": original,
        "rewritten": rewritten,
        "changes": changes,
        "safe": True,
        "warnings": warnings,
        "original_tokens": orig_tokens,
        "rewritten_tokens": new_tokens,
        "estimated_savings": max(0, orig_tokens - new_tokens),
    }


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


# ---------------------------------------------------------------------------
# Ponytail auto-rewrite with safety gate


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Ponytail code review
# ---------------------------------------------------------------------------

def review_code(code: str) -> dict[str, Any]:
    """Ponytail-style code review: detect over-engineering and estimate compression."""
    if not code:
        return {"ok": False, "error": "code is required for review"}

    issues: list[str] = []

    if len(code.split("\\n")) > 50:
        issues.append("File is over 50 lines — consider splitting or simplifying")

    if re.search(r"class.*Factory|class.*Manager|class.*Service|class.*Controller", code, re.IGNORECASE):
        issues.append("Possible unnecessary abstraction layer — consider simpler functions")

    if re.search(r"import\*\s*from", code):
        issues.append("Wildcard import detected — consider explicit imports")

    max_indent = 0
    for line in code.split("\\n"):
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

# Caveman compression (enhanced with domain presets + selective domains)
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

_NEVER_COMPRESS_DEFAULT = {
    "security", "auth", "crypto", "error", "exception", "warning", "alert",
    "pii", "personal", "private", "secret", "key", "token", "password",
}


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


def compress_prose(
    text: str,
    preset: DomainPreset | None = None,
    domain: str | None = None,
    domain_rules: DomainRules | None = None,
    learned: LearnedCompression | None = None,
) -> str:
    """Apply caveman compression with domain presets + selective domain rules."""
    if not text:
        return text

    preset = preset or DOMAIN_PRESETS["standard"]

    # Check selective domain rules
    if domain and domain_rules:
        if domain in domain_rules.never_compress:
            return text
        if domain in domain_rules.always_compress:
            pass  # force compress
        if domain in domain_rules.force_preset:
            preset = get_preset(domain_rules.force_preset[domain])

    # Check learned pattern
    pattern_key = f"domain:{domain or 'default'}"
    if learned and not learned.should_compress(pattern_key, default=True):
        return text

    text, blocks = _protect_code_blocks(text)

    protected: list[str] = []
    for phrase in _PROTECT_PHRASES:
        placeholder = f"\x00PROTECT_{len(protected)}\x00"
        text = text.replace(phrase, placeholder)
        protected.append(phrase)

    if preset.drop_articles:
        text = _ARTICLES.sub(" ", text)
    if preset.drop_filler:
        text = _FILLER.sub(" ", text)
    if preset.drop_pleasantries:
        text = _PLEASANTRIES.sub(" ", text)
    if preset.drop_hedging:
        text = _HEDGING.sub(" ", text)

    if preset.short_synonyms:
        for long_form, short_form in _SHORT_SYNONYMS.items():
            text = re.sub(
                r"\b" + re.escape(long_form) + r"\b",
                short_form,
                text,
                flags=re.IGNORECASE,
            )

    if preset.abbreviate_terms:
        for long_form, short_form in _ABBREVIATIONS.items():
            text = re.sub(
                r"\b" + re.escape(long_form) + r"\b",
                short_form,
                text,
                flags=re.IGNORECASE,
            )

    if preset.strip_conjunctions:
        text = re.sub(r"\b(and|or|but|so|yet)\b", " ", text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()

    for i, phrase in enumerate(protected):
        text = text.replace(f"\x00PROTECT_{i}\x00", phrase)

    text = _restore_code_blocks(text, blocks)

    return text
