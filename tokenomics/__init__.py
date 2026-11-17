"""Tokenomics - Caveman + Ponytail = Maximum Efficiency.

Compress agent prose, minimize code generation, display estimated token savings.
Cross-platform: works with Hermes, Claude Code, Cursor, Antigravity, Codex, and more.
"""

from __future__ import annotations

from .core import compress_prose, estimate_tokens, ponytail_ladder, review_code
from .state import StateManager
from .preview import write_preview

__version__ = "0.2.0"
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
    "review_code",
    "StateManager",
    "write_preview",
    "__version__",
]
