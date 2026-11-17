#!/usr/bin/env bash
# Tokenomics Install Script
# Cross-platform installer for Claude Code, Cursor, Antigravity, Codex, Hermes

set -euo pipefail

TOKENOMICS_VERSION="0.2.0"
TOKENOMICS_REPO="https://github.com/z99wE/tokenomics.git"
INSTALL_DIR="${HOME}/.tokenomics"

echo ""
echo "  ███╗   ███╗ █████╗ ██╗   ██╗████████╗"
echo "  ████╗ ████║██╔══██╗██║   ██║╚══██╔══╝"
echo "  ██╔████╔██║███████║██║   ██║   ██║"
echo "  ██║╚██╔╝██║██╔══██║██║   ██║   ██║"
echo "  ██║ ╚═╝ ██║██║  ██║╚██████╔╝   ██║"
echo "  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝"
echo ""
echo "  Tokenomics v${TOKENOMICS_VERSION} Installer"
echo "  Caveman + Ponytail = Maximum Efficiency"
echo ""

# Detect platform
detect_platform() {
    if command -v claude &>/dev/null; then
        echo "claude-code"
    elif command -v cursor &>/dev/null; then
        echo "cursor"
    elif command -v antigravity &>/dev/null; then
        echo "antigravity"
    elif command -v codex &>/dev/null; then
        echo "codex"
    elif command -v hermes &>/dev/null; then
        echo "hermes"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)
echo "Detected platform: ${PLATFORM}"

# Install via pip
echo ""
echo "[1/3] Installing tokenomics Python package..."
pip install tokenomics || {
    echo "pip install failed, trying pip3..."
    pip3 install tokenomics
}

# Copy skills to platform directories
echo ""
echo "[2/3] Installing agent skills..."

SKILL_SRC="$(dirname "$0")/../claude-code/SKILL.md"

case "${PLATFORM}" in
    claude-code)
        mkdir -p "${HOME}/.claude/skills/tokenomics"
        cp "${SKILL_SRC}" "${HOME}/.claude/skills/tokenomics/SKILL.md"
        echo "✓ Installed to ~/.claude/skills/tokenomics/"
        ;;
    cursor)
        mkdir -p "${HOME}/.cursor/skills/tokenomics"
        cp "${SKILL_SRC}" "${HOME}/.cursor/skills/tokenomics/SKILL.md"
        echo "✓ Installed to ~/.cursor/skills/tokenomics/"
        ;;
    antigravity)
        mkdir -p "${HOME}/.antigravity/skills/tokenomics"
        cp "${SKILL_SRC}" "${HOME}/.antigravity/skills/tokenomics/SKILL.md"
        echo "✓ Installed to ~/.antigravity/skills/tokenomics/"
        ;;
    codex)
        mkdir -p "${HOME}/.agents/skills/tokenomics"
        cp "${SKILL_SRC}" "${HOME}/.agents/skills/tokenomics/SKILL.md"
        mkdir -p "${HOME}/.codex/skills/tokenomics"
        cp "${SKILL_SRC}" "${HOME}/.codex/skills/tokenomics/SKILL.md"
        echo "✓ Installed to ~/.agents/skills/tokenomics/ and ~/.codex/skills/tokenomics/"
        ;;
    hermes)
        mkdir -p "${HOME}/.hermes/skills/tokenomics"
        cp "${SKILL_SRC}" "${HOME}/.hermes/skills/tokenomics/SKILL.md"
        echo "✓ Installed to ~/.hermes/skills/tokenomics/"
        echo ""
        echo "To install the Hermes plugin:"
        echo "  hermes skills tap add z99wE/tokenomics"
        echo "  hermes skills install tokenomics"
        echo "  hermes plugins enable tokenomics"
        ;;
    *)
        echo "Unknown platform. Copy SKILL.md manually to your agent's skills directory."
        ;;
esac

# Verify installation
echo ""
echo "[3/3] Verifying installation..."
if command -v tokenomics &>/dev/null; then
    echo "✓ tokenomics CLI available at $(which tokenomics)"
    tokenomics status
else
    echo "⚠ tokenomics CLI not on PATH. Try: pip install tokenomics"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Installation complete!"
  echo ""
  echo "  Usage:"
  echo "    tokenomics enable    # Turn on compression"
  echo "    tokenomics disable   # Turn off compression"
  echo "    tokenomics status    # View savings"
  echo "    tokenomics estimate <text>  # Preview savings"
  echo ""
  echo "  In chat, say:"
  echo "    'tokenomics enable' or 'caveman mode'"
  echo ""
  echo "  Learn more: https://github.com/z99wE/tokenomics"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
