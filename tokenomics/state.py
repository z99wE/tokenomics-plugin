"""State persistence for Tokenomics."""

from __future__ import annotations

import json
import os
from typing import Any


class StateManager:
    """Manages tokenomics state: enabled flag, cumulative stats, subagent count."""

    DEFAULT_STATE = {
        "enabled": False,
        "total_original_chars": 0,
        "total_compressed_chars": 0,
        "turns": 0,
        "subagents_propagated": 0,
    }

    def __init__(self, state_path: str | None = None):
        self.state_path = state_path or os.path.expanduser(
            "~/.hermes/plugins/tokenomics/state.json"
        )

    def load(self) -> dict[str, Any]:
        if not os.path.exists(self.state_path):
            return dict(self.DEFAULT_STATE)
        try:
            with open(self.state_path, "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return dict(self.DEFAULT_STATE)

    def save(self, state: dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

    def enable(self) -> dict[str, Any]:
        state = self.load()
        state["enabled"] = True
        self.save(state)
        return state

    def disable(self) -> dict[str, Any]:
        state = self.load()
        state["enabled"] = False
        self.save(state)
        return state

    def status(self) -> dict[str, Any]:
        state = self.load()
        saved_chars = state["total_original_chars"] - state["total_compressed_chars"]
        saved_tokens = saved_chars // 4
        return {
            "enabled": state["enabled"],
            "turns": state["turns"],
            "original_chars": state["total_original_chars"],
            "compressed_chars": state["total_compressed_chars"],
            "saved_chars": saved_chars,
            "estimated_tokens_saved": saved_tokens,
            "subagents_propagated": state.get("subagents_propagated", 0),
        }

    def record_turn(self, original_chars: int, compressed_chars: int) -> dict[str, Any]:
        state = self.load()
        state["total_original_chars"] = state.get("total_original_chars", 0) + original_chars
        state["total_compressed_chars"] = state.get("total_compressed_chars", 0) + compressed_chars
        state["turns"] = state.get("turns", 0) + 1
        self.save(state)
        return state

    def increment_subagents(self) -> dict[str, Any]:
        state = self.load()
        state["subagents_propagated"] = state.get("subagents_propagated", 0) + 1
        self.save(state)
        return state
