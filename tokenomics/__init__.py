"""Tokenomics v2.0.0 — Agentic-Era Token Efficiency Layer.

Compress agent prose, minimize code generation, display estimated token savings.
Cross-platform: works with Hermes, Claude Code, Cursor, Antigravity, Codex, and more.

Inspired by the concepts behind caveman (prose compression) and ponytail
(code minimization), but engineered independently as its own system with
context awareness, learned compression, gamification, subagent propagation,
and cross-agent memory.
"""

from __future__ import annotations

import os
import sys
from typing import Any

# Make the tokenomics package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tokenomics.core import (
    compress_prose,
    estimate_tokens,
    get_preset,
    review_code,
)
from tokenomics.preview import write_preview
from tokenomics.state import StateManager

STATE_MANAGER = StateManager()


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def _handle_enable(args: dict[str, Any]) -> dict[str, Any]:
    state = STATE_MANAGER.enable()
    write_preview(state)
    return {
        "ok": True,
        "data": {
            "enabled": True,
            "message": "Tokenomics enabled — prose compression + ponytail guidance active. Token savings shown on output.",
        },
    }


def _handle_disable(args: dict[str, Any]) -> dict[str, Any]:
    state = STATE_MANAGER.disable()
    write_preview(state)
    return {
        "ok": True,
        "data": {
            "enabled": False,
            "message": "Tokenomics disabled — no compression, no token-savings display.",
        },
    }


def _handle_status(args: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "data": STATE_MANAGER.status()}


def _handle_estimate(args: dict[str, Any]) -> dict[str, Any]:
    text = str(args.get("text", ""))
    orig = estimate_tokens(text)
    compressed = compress_prose(text)
    comp_tok = estimate_tokens(compressed)
    saved = orig - comp_tok
    return {
        "ok": True,
        "data": {
            "original_tokens": orig,
            "compressed_tokens": comp_tok,
            "estimated_saved": max(0, saved),
            "compression_ratio": round(comp_tok / orig, 2) if orig else 1.0,
            "preview": compressed[:200],
        },
    }


def _handle_review(args: dict[str, Any]) -> dict[str, Any]:
    code = str(args.get("code", ""))
    return review_code(code)


def _handle_audit(args: dict[str, Any]) -> dict[str, Any]:
    status = STATE_MANAGER.status()
    saved_chars = status["original_chars"] - status["compressed_chars"]
    saved_tokens = saved_chars // 4
    ratio = (
        status["compressed_chars"] / status["original_chars"]
        if status["original_chars"] > 0
        else 1.0
    )
    return {
        "ok": True,
        "data": {
            "enabled": status["enabled"],
            "turns": status["turns"],
            "subagents_propagated": status.get("subagents_propagated", 0),
            "original_chars": status["original_chars"],
            "compressed_chars": status["compressed_chars"],
            "saved_chars": saved_chars,
            "estimated_tokens_saved": saved_tokens,
            "compression_ratio": round(ratio, 2),
            "level": status["level"],
            "xp": status["xp"],
            "current_streak": status["current_streak"],
            "achievements_unlocked": status["achievements_unlocked"],
            "preview_path": "~/.hermes/plugins/tokenomics/preview.html",
            "recommendations": [
                "Enable tokenomics at session start for maximum savings",
                "Run tokenomics.review on large diffs before merging",
                "Preview widget at ~/.hermes/plugins/tokenomics/preview.html",
                "Use tokenomics.domain to set selective compression rules",
            ],
        },
    }


def _handle_domain(args: dict[str, Any]) -> dict[str, Any]:
    action = str(args.get("action", ""))
    domain = str(args.get("domain", ""))
    preset = str(args.get("preset", ""))
    sm = STATE_MANAGER

    if action == "never":
        sm.set_domain_rule(domain, "never_compress", True)
        return {"ok": True, "data": {"message": f"{domain} added to never-compress list"}}
    if action == "always":
        sm.set_domain_rule(domain, "always_compress", True)
        return {"ok": True, "data": {"message": f"{domain} added to always-compress list"}}
    if action == "preset":
        sm.set_domain_preset(domain, preset)
        return {"ok": True, "data": {"message": f"{domain} → preset {preset}"}}
    if action == "list":
        return {"ok": True, "data": sm.get_domain_rules()}
    return {"ok": False, "error": f"unknown domain action: {action}"}


def _handle_achievements(args: dict[str, Any]) -> dict[str, Any]:
    newly = STATE_MANAGER.check_achievements()
    return {"ok": True, "data": {"newly_unlocked": newly}}


def _run_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "tokenomics.enable": _handle_enable,
        "tokenomics.disable": _handle_disable,
        "tokenomics.status": _handle_status,
        "tokenomics.estimate": _handle_estimate,
        "tokenomics.review": _handle_review,
        "tokenomics.audit": _handle_audit,
        "tokenomics.domain": _handle_domain,
        "tokenomics.achievements": _handle_achievements,
    }
    if name in handlers:
        return handlers[name](args)
    return {"ok": False, "error": f"unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------

def _hook_pre_llm_call(**kwargs: Any) -> dict[str, Any]:
    """Inject ponytail YAGNI guidance into the LLM context before code generation."""
    context = kwargs.get("context", "")
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return {"context": context}

    ponytail_note = (
        "\n[TOKENOMICS / PONYTAIL] Lazy-senior-dev mode active. "
        "Before writing any code, climb the ladder and stop at the first rung that holds:\n"
        "1. Does this need to exist? (YAGNI — skip it)\n"
        "2. Already in this codebase? (reuse it)\n"
        "3. Stdlib does it? (use it)\n"
        "4. Native platform feature? (use it)\n"
        "5. Installed dependency solves it? (use it)\n"
        "6. Can it be one line? (write one line)\n"
        "7. Only then: minimum code that works\n"
        "Never cut validation, error handling, security, or accessibility.\n"
    )
    return {"context": context + ponytail_note}


def _hook_pre_tool_call(**kwargs: Any) -> dict[str, Any]:
    """Compress string arguments before tool execution when enabled."""
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return kwargs

    tool_name = kwargs.get("tool_name", "")
    args = kwargs.get("args", {}) or {}

    domain = tool_name.split(".")[0] if "." in tool_name else tool_name
    preset_name = STATE_MANAGER.get_domain_preset(domain)
    preset = get_preset(preset_name) if preset_name else None

    # Check selective domain rules
    rules = STATE_MANAGER.get_domain_rules()
    if domain in rules.get("never_compress", []):
        return kwargs

    compressed_args = {}
    for key, value in args.items():
        if isinstance(value, str):
            compressed_args[key] = compress_prose(value, preset=preset, domain=domain)
        else:
            compressed_args[key] = value

    if compressed_args != args:
        kwargs["args"] = compressed_args

    return kwargs


def _hook_post_tool_call(**kwargs: Any) -> dict[str, Any]:
    """Compress tool result output and track savings."""
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return kwargs

    result = kwargs.get("result", {})
    if not isinstance(result, dict) or "data" not in result or not isinstance(result["data"], dict):
        return kwargs

    data = result["data"]
    turn_original = 0
    turn_compressed = 0

    for key in ("message", "text", "content", "output", "stdout", "stderr", "description"):
        if key in data and isinstance(data[key], str):
            original = data[key]
            turn_original += len(original)
            compressed = compress_prose(original)
            turn_compressed += len(compressed)
            if compressed != original:
                data[key] = compressed

    if turn_original > 0:
        STATE_MANAGER.record_turn(turn_original, turn_compressed)
        write_preview(STATE_MANAGER.load())
        result["data"] = data
        kwargs["result"] = result

    return kwargs


def _hook_on_session_start(**kwargs: Any) -> dict[str, Any]:
    """Write preview widget on session start."""
    state = STATE_MANAGER.load()
    write_preview(state)
    return {"context": kwargs.get("context", "")}


def _hook_on_session_end(**kwargs: Any) -> dict[str, Any]:
    """Final state save on session end."""
    state = STATE_MANAGER.load()
    STATE_MANAGER.save(state)
    write_preview(state)
    return {"context": kwargs.get("context", "")}


def _hook_delegate_task(**kwargs: Any) -> dict[str, Any]:
    """Propagate tokenomics state to delegate_task subagents."""
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return kwargs

    context = kwargs.get("context", "") or ""
    message = kwargs.get("message", "") or ""

    tokenomics_note = (
        "\n\n[TOKENOMICS PROPAGATED] This subagent inherits tokenomics mode: "
        "caveman prose compression + ponytail code minimization active. "
        "Apply YAGNI ladder before writing code. Compress output prose. "
        "Report token savings on completion.\n"
    )

    if "message" in kwargs:
        kwargs["message"] = message + tokenomics_note
    if "context" in kwargs:
        kwargs["context"] = context + tokenomics_note

    STATE_MANAGER.increment_subagents()
    write_preview(STATE_MANAGER.load())

    return kwargs


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register(ctx):
    ctx.register_tool(
        name="tokenomics.enable",
        toolset="tokenomics",
        schema={"type": "object", "properties": {}, "required": []},
        handler=_run_tool,
        description="Enable Tokenomics (caveman + ponytail). Shows estimated token savings on output.",
        emoji="📉",
    )
    ctx.register_tool(
        name="tokenomics.disable",
        toolset="tokenomics",
        schema={"type": "object", "properties": {}, "required": []},
        handler=_run_tool,
        description="Disable Tokenomics. Stops compression and savings display.",
        emoji="📈",
    )
    ctx.register_tool(
        name="tokenomics.status",
        toolset="tokenomics",
        schema={"type": "object", "properties": {}, "required": []},
        handler=_run_tool,
        description="Show Tokenomics status: enabled state, chars compressed, estimated tokens saved, level, streak, achievements.",
        emoji="📊",
    )
    ctx.register_tool(
        name="tokenomics.estimate",
        toolset="tokenomics",
        schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to estimate token savings for",
                },
            },
            "required": ["text"],
        },
        handler=_run_tool,
        description="Estimate token savings for a given text if caveman compression were applied.",
        emoji="🔢",
    )
    ctx.register_tool(
        name="tokenomics.review",
        toolset="tokenomics",
        schema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Code to review for over-engineering",
                },
            },
            "required": ["code"],
        },
        handler=_run_tool,
        description="Ponytail-style code review: check for over-engineering and estimate code compression.",
        emoji="🔍",
    )
    ctx.register_tool(
        name="tokenomics.audit",
        toolset="tokenomics",
        schema={"type": "object", "properties": {}, "required": []},
        handler=_run_tool,
        description="Full tokenomics audit: savings summary, compression ratio, level, streak, achievements, recommendations.",
        emoji="📋",
    )
    ctx.register_tool(
        name="tokenomics.domain",
        toolset="tokenomics",
        schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["never", "always", "preset", "list"],
                    "description": "Domain rule action",
                },
                "domain": {
                    "type": "string",
                    "description": "Domain name (e.g., security, auth, crypto, docs)",
                },
                "preset": {
                    "type": "string",
                    "description": "Preset name for preset action (standard, docs, commit, review, chat, ultra)",
                },
            },
            "required": ["action"],
        },
        handler=_run_tool,
        description="Manage selective compression domain rules and presets.",
        emoji="🎯",
    )
    ctx.register_tool(
        name="tokenomics.achievements",
        toolset="tokenomics",
        schema={"type": "object", "properties": {}, "required": []},
        handler=_run_tool,
        description="Check for newly unlocked gamification achievements.",
        emoji="🏆",
    )

    ctx.register_hook("pre_llm_call", _hook_pre_llm_call)
    ctx.register_hook("pre_tool_call", _hook_pre_tool_call)
    ctx.register_hook("post_tool_call", _hook_post_tool_call)
    ctx.register_hook("on_session_start", _hook_on_session_start)
    ctx.register_hook("on_session_end", _hook_on_session_end)
    ctx.register_hook("delegate_task", _hook_delegate_task)

    # Write preview widget on registration
    state = STATE_MANAGER.load()
    write_preview(state)
