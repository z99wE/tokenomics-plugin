"""Hermes plugin entry point for Tokenomics.

Registers tools and hooks for caveman prose compression, ponytail code
minimization, and token-savings estimation with preview-pane widget.
"""

from __future__ import annotations

import sys
from typing import Any

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))

# Add parent to path so we can import the tokenomics package
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), ".."))

from tokenomics.core import compress_prose, estimate_tokens, ponytail_ladder, review_code
from tokenomics.state import StateManager
from tokenomics.preview import write_preview

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
    original_tokens = estimate_tokens(text)
    compressed = compress_prose(text)
    compressed_tokens = estimate_tokens(compressed)
    saved = original_tokens - compressed_tokens
    return {
        "ok": True,
        "data": {
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "estimated_saved": max(0, saved),
            "compression_ratio": round(compressed_tokens / original_tokens, 2) if original_tokens else 1.0,
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
            "preview_path": "~/.hermes/plugins/tokenomics/preview.html",
            "recommendations": [
                "Run tokenomics.review on large diffs before merging",
                "Enable tokenomics at session start for maximum savings",
                "Preview widget at ~/.hermes/plugins/tokenomics/preview.html",
            ],
        },
    }


def _run_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "tokenomics.enable": _handle_enable,
        "tokenomics.disable": _handle_disable,
        "tokenomics.status": _handle_status,
        "tokenomics.estimate": _handle_estimate,
        "tokenomics.review": _handle_review,
        "tokenomics.audit": _handle_audit,
    }
    if name in handlers:
        return handlers[name](args)
    return {"ok": False, "error": f"unknown tool: {name}"}


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------

def _hook_pre_llm_call(**kwargs: Any) -> dict[str, Any]:
    context = kwargs.get("context", "")
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return {"context": context}

    ponytail_note = (
        "\n[TOKENOMICS / PONYTAIL] Lazy-senior-dev mode active. Before writing any code, "
        "climb the ladder and stop at the first rung that holds:\n"
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
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return kwargs

    tool_name = kwargs.get("tool_name", "")
    args = kwargs.get("args", {}) or {}

    compressed_args = {}
    for key, value in args.items():
        if isinstance(value, str):
            compressed_args[key] = compress_prose(value)
        else:
            compressed_args[key] = value

    if compressed_args != args:
        kwargs["args"] = compressed_args

    return kwargs


def _hook_post_tool_call(**kwargs: Any) -> dict[str, Any]:
    state = STATE_MANAGER.load()
    if not state.get("enabled", False):
        return kwargs

    result = kwargs.get("result", {})
    if isinstance(result, dict) and "data" in result and isinstance(result["data"], dict):
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
    state = STATE_MANAGER.load()
    write_preview(state)
    return {"context": kwargs.get("context", "")}


def _hook_on_session_end(**kwargs: Any) -> dict[str, Any]:
    state = STATE_MANAGER.load()
    STATE_MANAGER.save(state)
    write_preview(state)
    return {"context": kwargs.get("context", "")}


def _hook_delegate_task(**kwargs: Any) -> dict[str, Any]:
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
        description="Show Tokenomics status: enabled state, chars compressed, estimated tokens saved.",
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
        description="Full tokenomics audit: savings summary, compression ratio, recommendations.",
        emoji="📋",
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
