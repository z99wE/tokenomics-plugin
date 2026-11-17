"""ASCII Logo for Tokenomics v2.3.0.

Loads the brand art from ascii_art.txt so the same 3D logo is used
everywhere: CLI, Hermes plugin preview, SKILL.md files, and README.
"""

from __future__ import annotations

import os
from pathlib import Path

_LOGO_PATH = Path(__file__).parent / "ascii_art.txt"

try:
    LOGO: str = _LOGO_PATH.read_text(encoding="utf-8")
except OSError:
    LOGO: str = (
        "Tokenomics v2.3.0\n"
        "Agentic Efficiency Layer for AI Agents\n"
        "Compress prose. Minimize code. Save tokens.\n"
    )

TAGLINE: str = "Small mouth, big brain. Minimum code, maximum impact."


def get_logo() -> str:
    """Return the Tokenomics ASCII logo."""
    return LOGO


def get_tagline() -> str:
    """Return the Tokenomics tagline."""
    return TAGLINE
