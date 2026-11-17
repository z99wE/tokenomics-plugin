"""Tokenomics v2.0.0 — Enhanced Caveman + Ponytail Suite.

Compress agent prose, minimize code generation, display estimated token savings.
Cross-platform: works with Hermes, Claude Code, Cursor, Antigravity, Codex, and more.

Agentic features:
- Real token counting (tiktoken with fallback)
- Context-aware compression (code, docs, config, secrets, sql, prose)
- Domain presets (standard, docs, commit, review, chat, ultra, code, secrets)
- Ponytail auto-rewrite with safety gate
- Caveman pre-generation
- Learned compression (user revert/adapt tracking)
- Cross-agent sync (shared state with file locking)
- Gamification (levels, XP, streaks, achievements)
- Selective domain compression (allowlist/denylist)
- Code-reviewer integration
- Claude-coach integration
"""

from __future__ import annotations

from .agentic import AgenticCompressor, CodeReviewIntegration, ClaudeCoachIntegration
from .context import compression_strategy_for, detect_context, is_security_sensitive
from .core import (
    compress_prose,
    estimate_tokens,
    ponytail_ladder,
    ponytail_rewrite,
    review_code,
)
from .preview import write_preview
from .state import StateManager

__version__ = "2.0.0"
__author__ = "Tokenomics Contributors"
__license__ = "MIT"

# Display ASCII logo on import
try:
    from . import _logo  # noqa: F401
except Exception:
    pass

__all__ = [
    "compress_prose",
    "estimate_tokens",
    "ponytail_ladder",
    "ponytail_rewrite",
    "review_code",
    "detect_context",
    "compression_strategy_for",
    "is_security_sensitive",
    "StateManager",
    "AgenticCompressor",
    "CodeReviewIntegration",
    "ClaudeCoachIntegration",
    "write_preview",
    "__version__",
]
