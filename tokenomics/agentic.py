"""Tokenomics Agentic Module v2.0 — Cross-agent learning and integration.

Makes Tokenomics agentic-era friendly:
- Cross-agent memory: shared learning across all agents and sessions
- Code-reviewer integration: pre-processes code before review
- Claude-coach integration: coaches on token-efficient patterns
- Self-improving: adapts compression strategy based on user behavior
- Context-aware: knows what kind of content it's compressing
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from .core import (
    ACHIEVEMENTS, Achievement, DomainRules, Gamification,
    LearnedCompression, LearnedPattern, compress_prose, estimate_tokens,
    get_preset, ponytail_rewrite, review_code,
)
from .context import compression_strategy_for, detect_context, is_security_sensitive
from .state import StateManager


@dataclass
class AgenticProfile:
    """Per-agent learning profile."""
    agent_id: str
    total_tokens_saved: int = 0
    total_turns: int = 0
    contexts_seen: dict[str, int] = field(default_factory=dict)
    preferred_presets: dict[str, int] = field(default_factory=dict)
    revert_patterns: dict[str, int] = field(default_factory=dict)
    last_active: float = 0.0

    def record_turn(self, context: str, preset: str, tokens_saved: int) -> None:
        self.total_turns += 1
        self.total_tokens_saved += tokens_saved
        self.contexts_seen[context] = self.contexts_seen.get(context, 0) + 1
        self.preferred_presets[preset] = self.preferred_presets.get(preset, 0) + 1
        self.last_active = time.time()

    def record_revert(self, pattern: str) -> None:
        self.revert_patterns[pattern] = self.revert_patterns.get(pattern, 0) + 1


class AgenticManager:
    """Manages cross-agent learning and agentic features."""

    def __init__(self, state_manager: Any):
        self.state = state_manager
        self.agents: dict[str, AgenticProfile] = {}
        self._load_agent_profiles()

    def _load_agent_profiles(self) -> None:
        state = self.state.load()
        agents_data = state.get("agentic_profiles", {})
        for aid, data in agents_data.items():
            self.agents[aid] = AgenticProfile(**data)

    def _save_agent_profiles(self) -> None:
        state = self.state.load()
        state["agentic_profiles"] = {
            aid: asdict(profile) for aid, profile in self.agents.items()
        }
        self.state.save(state)

    def get_or_create_agent(self, agent_id: str) -> AgenticProfile:
        if agent_id not in self.agents:
            self.agents[agent_id] = AgenticProfile(agent_id=agent_id)
        return self.agents[agent_id]

    def record_agent_turn(
        self, agent_id: str, context: str, preset: str, tokens_saved: int
    ) -> None:
        agent = self.get_or_create_agent(agent_id)
        agent.record_turn(context, preset, tokens_saved)
        self._save_agent_profiles()

    def record_agent_revert(self, agent_id: str, pattern: str) -> None:
        agent = self.get_or_create_agent(agent_id)
        agent.record_revert(pattern)
        self._save_agent_profiles()

    def get_agent_insights(self, agent_id: str) -> dict[str, Any]:
        agent = self.get_or_create_agent(agent_id)
        return {
            "agent_id": agent.agent_id,
            "total_tokens_saved": agent.total_tokens_saved,
            "total_turns": agent.total_turns,
            "contexts_seen": agent.contexts_seen,
            "preferred_presets": agent.preferred_presets,
            "revert_patterns": agent.revert_patterns,
            "last_active": agent.last_active,
        }

    def get_global_insights(self) -> dict[str, Any]:
        total_tokens = sum(a.total_tokens_saved for a in self.agents.values())
        total_turns = sum(a.total_turns for a in self.agents.values())
        all_contexts: dict[str, int] = {}
        for agent in self.agents.values():
            for ctx, count in agent.contexts_seen.items():
                all_contexts[ctx] = all_contexts.get(ctx, 0) + count
        return {
            "total_agents": len(self.agents),
            "total_tokens_saved": total_tokens,
            "total_turns": total_turns,
            "contexts_seen": all_contexts,
            "average_tokens_per_turn": total_tokens / max(total_turns, 1),
        }


# ---------------------------------------------------------------------------
# Integration with code-reviewer and claude-coach skills
# ---------------------------------------------------------------------------

class CodeReviewIntegration:
    """Integrates Tokenomics with code-reviewer skill.

    Pre-processes code before review to:
    1. Strip boilerplate so reviewer focuses on logic
    2. Flag over-engineered patterns
    3. Estimate token cost of the code
    """

    def __init__(self, state_manager: Any):
        self.state = state_manager

    def pre_review(self, code: str, agent_id: str = "default") -> dict[str, Any]:
        """Pre-process code before code review.

        Returns cleaned code + review hints + token savings estimate.
        """
        if not code:
            return {"ok": False, "error": "code is required"}

        # Detect context
        context = detect_context(code)
        strategy = compression_strategy_for(code)

        # Compress prose parts (comments, docstrings) but not code structure
        compressed = compress_prose(code, preset=get_preset("review"))
        orig_tokens = estimate_tokens(code)
        comp_tokens = estimate_tokens(compressed)

        # Detect over-engineering patterns
        over_engineered = []
        if len(code.split("\n")) > 50:
            over_engineered.append("File exceeds 50 lines")
        if re.search(r"class.*Factory|class.*Manager|class.*Service", code, re.IGNORECASE):
            over_engineered.append("Possible unnecessary abstraction layer")
        if re.search(r"import\*\s*from", code):
            over_engineered.append("Wildcard import detected")

        # Record agent turn via agentic manager
        agent = self.state.get_or_create_agent(agent_id) if hasattr(self.state, 'get_or_create_agent') else None
        if agent:
            agent.record_turn(context, "review", orig_tokens - comp_tokens)

        return {
            "ok": True,
            "context": context,
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "tokens_saved": max(0, orig_tokens - comp_tokens),
            "compressed_code": compressed,
            "over_engineered": over_engineered,
            "strategy": strategy,
        }


class ClaudeCoachIntegration:
    """Integrates Tokenomics with claude-coach skill.

    Coaches the agent on token-efficient patterns:
    - "You used 500 tokens to say what could be said in 50"
    - "Consider using stdlib instead of custom implementation"
    - "Your revert rate on abbreviation compression is 80% — stopping"
    """

    def __init__(self, state_manager: Any):
        self.state = state_manager

    def coach_on_compression(
        self, agent_id: str, original: str, compressed: str
    ) -> dict[str, Any]:
        """Coach the agent on token-efficient communication."""
        if not original or not compressed:
            return {"ok": False, "error": "original and compressed text required"}

        orig_tokens = estimate_tokens(original)
        comp_tokens = estimate_tokens(compressed)
        saved = max(0, orig_tokens - comp_tokens)
        savings_pct = round((saved / orig_tokens) * 100, 1) if orig_tokens else 0

        # Generate coaching tips
        tips: list[str] = []
        if savings_pct > 50:
            tips.append("Excellent compression — you cut token usage by more than half")
        elif savings_pct > 25:
            tips.append("Good compression — consider being more direct")
        elif savings_pct > 0:
            tips.append("Minimal savings — try cutting filler words first")
        else:
            tips.append("No savings — text is already concise")

        # Context-specific tips
        context = detect_context(original)
        if context == "code":
            tips.append("For code, prefer standard library over custom implementations")
        elif context == "docs":
            tips.append("For docs, use bullet points and short sentences")
        elif context == "prose":
            tips.append("For prose, drop filler words like 'just', 'really', 'basically'")

        # Record agent turn
        agent = self.state.get_or_create_agent(agent_id) if hasattr(self.state, 'get_or_create_agent') else None
        if agent:
            agent.record_turn(context, "coaching", saved)

        return {
            "ok": True,
            "context": context,
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "tokens_saved": saved,
            "savings_percentage": savings_pct,
            "tips": tips,
            "recommendation": self._get_primary_tip(tips),
        }

    def _get_primary_tip(self, tips: list[str]) -> str:
        return tips[0] if tips else "Keep it concise"

    def coach_on_pattern(
        self, agent_id: str, pattern: str, reverted: bool
    ) -> dict[str, Any]:
        """Coach the agent on a specific compression pattern."""
        agent = self.state.get_or_create_agent(agent_id) if hasattr(self.state, 'get_or_create_agent') else None
        if agent:
            agent.record_revert(pattern)

        if reverted:
            return {
                "ok": True,
                "pattern": pattern,
                "advice": f"Stop using '{pattern}' compression — you keep reverting it",
                "action": "disabled",
            }
        else:
            return {
                "ok": True,
                "pattern": pattern,
                "advice": f"Keep using '{pattern}' compression — it works well",
                "action": "keep",
            }


# ---------------------------------------------------------------------------
# Combined agentic compression (the main entry point)
# ---------------------------------------------------------------------------

class AgenticCompressor:
    """Main entry point for agentic compression.

    Combines context detection, learned compression, selective domains,
    and gamification into a single compression pipeline.
    """

    def __init__(self, state_manager: Any):
        self.state = state_manager
        self.agentic = AgenticManager(state_manager)
        self.code_review = CodeReviewIntegration(state_manager)
        self.claude_coach = ClaudeCoachIntegration(state_manager)

    def compress(
        self,
        text: str,
        agent_id: str = "default",
        force_preset: str | None = None,
    ) -> dict[str, Any]:
        """Compress text with full agentic context.

        Returns dict with compressed text, savings, context, and coaching.
        """
        if not text:
            return {"ok": False, "error": "text is required"}

        # Detect context
        context = detect_context(text)
        strategy = compression_strategy_for(text)

        # Use context as domain for domain rules
        domain = context

        # Check selective domain rules
        domain_rules = self.state.get_domain_rules()
        if domain in domain_rules.never_compress:
            return {
                "ok": True,
                "original": text,
                "compressed": text,
                "context": context,
                "strategy": strategy,
                "tokens_saved": 0,
                "reason": "Domain in never-compress list",
                "skipped": True,
            }

        # Security check — never compress secrets, auth, crypto
        if is_security_sensitive(text):
            return {
                "ok": True,
                "original": text,
                "compressed": text,
                "context": context,
                "strategy": strategy,
                "tokens_saved": 0,
                "reason": "Security-sensitive content — never compressed",
                "skipped": True,
            }

        # Determine preset
        preset_name = force_preset or strategy["preset"]
        domain_preset = self.state.get_domain_preset(domain)
        if domain_preset:
            preset_name = domain_preset
        preset = get_preset(preset_name)

        # Check learned compression
        pattern_key = f"{domain or 'default'}:{text[:50]}"
        learned = self.state  # StateManager has learned compression methods
        if not learned.should_compress_pattern(pattern_key, context or "default"):
            return {
                "ok": True,
                "original": text,
                "compressed": text,
                "context": context,
                "strategy": strategy,
                "tokens_saved": 0,
                "reason": "Learned pattern — user reverts this compression",
                "skipped": True,
            }

        # Apply compression
        compressed = compress_prose(text, preset=preset, domain=domain)
        orig_tokens = estimate_tokens(text)
        comp_tokens = estimate_tokens(compressed)
        saved = max(0, orig_tokens - comp_tokens)

        # Record agent turn
        self.agentic.record_agent_turn(agent_id, context, preset_name, saved)

        # Record learned pattern
        self.state.record_learned_pattern(pattern_key, saved == 0)

        # Check achievements
        newly_unlocked = self.state.check_achievements()

        return {
            "ok": True,
            "original": text,
            "compressed": compressed,
            "context": context,
            "preset": preset_name,
            "strategy": strategy,
            "original_tokens": orig_tokens,
            "compressed_tokens": comp_tokens,
            "tokens_saved": saved,
            "savings_percentage": round((saved / orig_tokens) * 100, 1) if orig_tokens else 0,
            "newly_unlocked": newly_unlocked,
            "skipped": False,
        }

    def get_agent_insights(self, agent_id: str) -> dict[str, Any]:
        return self.agentic.get_agent_insights(agent_id)

    def get_global_insights(self) -> dict[str, Any]:
        return self.agentic.get_global_insights()
