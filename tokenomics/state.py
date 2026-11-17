"""Tokenomics State Manager v1.0.0 — Gamification, learning, cross-agent sync."""

from __future__ import annotations

import fcntl
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

from .core import (
    ACHIEVEMENTS,
    Achievement,
    DomainPreset,
    DomainRules,
    Gamification,
    LearnedCompression,
    LearnedPattern,
    get_preset,
)

STATE_PATH = os.path.expanduser("~/.hermes/plugins/tokenomics/state.json")
LOCK_PATH = os.path.expanduser("~/.hermes/plugins/tokenomics/state.lock")


class StateManager:
    """Manages tokenomics state: enabled flag, cumulative stats, gamification,
    learned compression patterns, cross-agent sync with file locking."""

    DEFAULT_STATE = {
        "enabled": False,
        "total_original_chars": 0,
        "total_compressed_chars": 0,
        "turns": 0,
        "subagents_propagated": 0,
        "total_tokens_saved": 0,
        "total_chars_saved": 0,
        "current_streak": 0,
        "best_streak": 0,
        "last_activity_date": None,
        "level": 1,
        "xp": 0,
        "achievements": {k: asdict(v) for k, v in ACHIEVEMENTS.items()},
        "learned_patterns": {},
        "domain_rules": {
            "never_compress": [],
            "always_compress": [],
            "force_preset": {},
        },
        "domain_presets": {},
        # Enhanced features beyond caveman/ponytail
        "daily_token_budget": None,
        "tokens_used_today": 0,
        "tokens_saved_today": 0,
        "project_type": None,
        "auto_learn": True,
        "smart_defaults": True,
        "budget_alerts_enabled": True,
    }

    def __init__(self, state_path: str | None = None):
        self.state_path = state_path or STATE_PATH
        self.lock_path = LOCK_PATH
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

    def _acquire_lock(self) -> Any:
        f = open(self.lock_path, "w")
        fcntl.flock(f, fcntl.LOCK_EX)
        return f

    def _release_lock(self, f: Any) -> None:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()

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
        lock = self._acquire_lock()
        try:
            with open(self.state_path, "w") as sf:
                json.dump(state, sf, indent=2)
        finally:
            self._release_lock(lock)

    # ------------------------------------------------------------------
    # Enable / disable
    # ------------------------------------------------------------------

    def enable(self) -> dict[str, Any]:
        state = self.load()
        state["enabled"] = True
        self._update_streak(state)
        self.save(state)
        return state

    def disable(self) -> dict[str, Any]:
        state = self.load()
        state["enabled"] = False
        self.save(state)
        return state

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        state = self.load()
        saved_chars = state["total_original_chars"] - state["total_compressed_chars"]
        saved_tokens = saved_chars // 4
        return {
            "enabled": state["enabled"],
            "turns": state["turns"],
            "subagents_propagated": state.get("subagents_propagated", 0),
            "original_chars": state["total_original_chars"],
            "compressed_chars": state["total_compressed_chars"],
            "saved_chars": saved_chars,
            "estimated_tokens_saved": saved_tokens,
            "level": state.get("level", 1),
            "xp": state.get("xp", 0),
            "current_streak": state.get("current_streak", 0),
            "best_streak": state.get("best_streak", 0),
            "achievements_unlocked": sum(
                1 for a in state.get("achievements", {}).values() if a.get("unlocked")
            ),
            "total_achievements": len(state.get("achievements", {})),
        }

    # ------------------------------------------------------------------
    # Turn tracking
    # ------------------------------------------------------------------

    def record_turn(self, original_chars: int, compressed_chars: int) -> dict[str, Any]:
        state = self.load()
        state["total_original_chars"] = state.get("total_original_chars", 0) + original_chars
        state["total_compressed_chars"] = state.get("total_compressed_chars", 0) + compressed_chars
        state["turns"] = state.get("turns", 0) + 1

        saved_chars = original_chars - compressed_chars
        state["total_chars_saved"] = state.get("total_chars_saved", 0) + saved_chars
        state["total_tokens_saved"] = state.get("total_tokens_saved", 0) + (saved_chars // 4)
        state["xp"] = state.get("xp", 0) + (saved_chars // 40)

        self._update_streak(state)
        state["level"] = 1 + state.get("total_tokens_saved", 0) // 10000

        self.save(state)
        return state

    def _update_streak(self, state: dict[str, Any]) -> None:
        today = time.strftime("%Y-%m-%d")
        last = state.get("last_activity_date")
        if last == today:
            return  # already counted today
        if last is None:
            state["current_streak"] = 1
        else:
            try:
                last_date = datetime.strptime(last, "%Y-%m-%d").date()
                today_date = datetime.strptime(today, "%Y-%m-%d").date()
                delta = (today_date - last_date).days
                if delta == 1:
                    state["current_streak"] = state.get("current_streak", 0) + 1
                elif delta > 1:
                    state["current_streak"] = 1
            except ValueError:
                state["current_streak"] = 1
        state["best_streak"] = max(state.get("best_streak", 0), state["current_streak"])
        state["last_activity_date"] = today

    # ------------------------------------------------------------------
    # Subagent propagation
    # ------------------------------------------------------------------

    def increment_subagents(self) -> dict[str, Any]:
        state = self.load()
        state["subagents_propagated"] = state.get("subagents_propagated", 0) + 1
        self.save(state)
        return state

    # ------------------------------------------------------------------
    # Learned compression
    # ------------------------------------------------------------------

    def record_learned_pattern(self, pattern: str, reverted: bool) -> None:
        state = self.load()
        patterns = state.get("learned_patterns", {})
        if pattern not in patterns:
            patterns[pattern] = {
                "pattern": pattern,
                "revert_count": 0,
                "accept_count": 0,
                "last_seen": time.time(),
            }
        p = patterns[pattern]
        p["last_seen"] = time.time()
        if reverted:
            p["revert_count"] = p.get("revert_count", 0) + 1
        else:
            p["accept_count"] = p.get("accept_count", 0) + 1
        state["learned_patterns"] = patterns
        self.save(state)

    def should_compress_pattern(self, pattern: str, default: bool = True) -> bool:
        state = self.load()
        patterns = state.get("learned_patterns", {})
        p = patterns.get(pattern)
        if p is None:
            return default
        total = p.get("revert_count", 0) + p.get("accept_count", 0)
        if total == 0:
            return default
        return p.get("revert_count", 0) / total < 0.5

    # ------------------------------------------------------------------
    # Domain rules (selective compression)
    # ------------------------------------------------------------------

    def set_domain_rule(self, domain: str, rule_type: str, value: str | bool) -> None:
        state = self.load()
        rules = state.get("domain_rules", {"never_compress": [], "always_compress": [], "force_preset": {}})

        if rule_type == "never_compress":
            nc = set(rules.get("never_compress", []))
            if value is True:
                nc.add(domain)
            else:
                nc.discard(domain)
            rules["never_compress"] = sorted(nc)
        elif rule_type == "always_compress":
            ac = set(rules.get("always_compress", []))
            if value is True:
                ac.add(domain)
            else:
                ac.discard(domain)
            rules["always_compress"] = sorted(ac)
        elif rule_type == "force_preset":
            rules.setdefault("force_preset", {})[domain] = value

        state["domain_rules"] = rules
        self.save(state)

    def get_domain_rules(self) -> DomainRules:
        state = self.load()
        rules = state.get("domain_rules", {"never_compress": [], "always_compress": [], "force_preset": {}})
        return DomainRules(
            never_compress=set(rules.get("never_compress", [])),
            always_compress=set(rules.get("always_compress", [])),
            force_preset=dict(rules.get("force_preset", {})),
        )

    # ------------------------------------------------------------------
    # Domain presets
    # ------------------------------------------------------------------

    def set_domain_preset(self, domain: str, preset_name: str) -> None:
        state = self.load()
        presets = state.get("domain_presets", {})
        presets[domain] = preset_name
        state["domain_presets"] = presets
        self.save(state)

    def get_domain_preset(self, domain: str | None) -> str | None:
        if not domain:
            return None
        state = self.load()
        return state.get("domain_presets", {}).get(domain)

    # ------------------------------------------------------------------
    # Enhanced features: token budget, project type, smart defaults
    # ------------------------------------------------------------------

    def set_token_budget(self, daily_limit: int) -> None:
        """Set daily token budget. None = unlimited."""
        state = self.load()
        state["daily_token_budget"] = daily_limit
        state["tokens_used_today"] = 0
        state["tokens_saved_today"] = 0
        self.save(state)

    def get_token_budget(self) -> int | None:
        state = self.load()
        return state.get("daily_token_budget")

    def record_tokens_used(self, count: int) -> dict:
        """Record tokens consumed and check budget. Returns budget status."""
        state = self.load()
        today = datetime.now().strftime("%Y-%m-%d")
        last_date = state.get("last_activity_date")

        # Reset daily counters if new day
        if last_date != today:
            state["tokens_used_today"] = count
            state["tokens_saved_today"] = 0
        else:
            state["tokens_used_today"] = state.get("tokens_used_today", 0) + count

        state["last_activity_date"] = today
        budget = state.get("daily_token_budget")
        saved_today = state.get("tokens_saved_today", 0)
        used_today = state["tokens_used_today"]

        alert = None
        if budget and used_today >= budget:
            alert = f"🛑 Token budget reached: {used_today}/{budget}"
        elif budget and used_today >= budget * 0.8:
            alert = f"⚠️ Token budget alert: {used_today}/{budget} used ({used_today/budget*100:.0f}%)"

        self.save(state)
        return {"budget": budget, "used_today": used_today, "saved_today": saved_today, "alert": alert}

    def set_project_type(self, project_type: str) -> None:
        """Set project type for smart defaults: web, cli, library, api, or none."""
        state = self.load()
        state["project_type"] = project_type
        self.save(state)

    def get_project_type(self) -> str | None:
        state = self.load()
        return state.get("project_type")

    def set_auto_learn(self, enabled: bool) -> None:
        state = self.load()
        state["auto_learn"] = enabled
        self.save(state)

    def set_smart_defaults(self, enabled: bool) -> None:
        state = self.load()
        state["smart_defaults"] = enabled
        self.save(state)

    def set_budget_alerts(self, enabled: bool) -> None:
        state = self.load()
        state["budget_alerts_enabled"] = enabled
        self.save(state)

    # ------------------------------------------------------------------
    # Achievements / gamification
    # ------------------------------------------------------------------

    def check_achievements(self) -> list[str]:
        state = self.load()
        newly_unlocked: list[str] = []

        achs = state.get("achievements", {})
        for aid, ach in achs.items():
            if not ach.get("unlocked", False):
                threshold = ach.get("threshold", 0)
                if aid in (
                    "first_savings",
                    "token_hoarder",
                    "token_miser",
                    "lazy_senior",
                    "yagni_master",
                ):
                    if state.get("total_tokens_saved", 0) >= threshold:
                        ach["unlocked"] = True
                        ach["unlocked_at"] = time.time()
                        newly_unlocked.append(aid)
                elif aid in ("streak_3", "streak_7"):
                    if state.get("current_streak", 0) >= threshold:
                        ach["unlocked"] = True
                        ach["unlocked_at"] = time.time()
                        newly_unlocked.append(aid)

        state["achievements"] = achs
        state["level"] = 1 + state.get("total_tokens_saved", 0) // 10000
        self.save(state)
        return newly_unlocked

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        self.save(dict(self.DEFAULT_STATE))
