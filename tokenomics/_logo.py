"""Tokenomics brand assets.

Loads the PNG logo from ``assets/logo.png`` and exposes helpers so the CLI,
Hermes plugin preview, and SKILL.md files can all reference the same brand
artwork instead of ASCII text.
"""

from __future__ import annotations

from pathlib import Path

_LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

LOGO_PATH: str = str(_LOGO_PATH)
TAGLINE: str = "Small mouth, big brain. Minimum code, maximum impact."
SUBTITLE: str = "Agentic Efficiency Layer for AI Agents"
DESCRIPTION: str = (
    "Tokenomics is an agentic efficiency layer that sits between your AI "
    "agent and its output. It compresses agent prose, minimizes code "
    "generation, tracks token savings, and learns from your behavior — all "
    "while keeping safety and authorization at the forefront."
)


def logo_path() -> str:
    """Return the absolute path to the Tokenomics PNG logo."""
    return str(_LOGO_PATH)


def tagline() -> str:
    """Return the Tokenomics tagline."""
    return TAGLINE


def subtitle() -> str:
    """Return the Tokenomics subtitle."""
    return SUBTITLE


def description() -> str:
    """Return the Tokenomics long description."""
    return DESCRIPTION


def markdown_image() -> str:
    """Return a markdown image tag for the logo."""
    return f"![Tokenomics]({_LOGO_PATH.name})"


def html_image() -> str:
    """Return an HTML img tag for the logo."""
    return f'<img src="{_LOGO_PATH.name}" alt="Tokenomics" width="1200"/>'
