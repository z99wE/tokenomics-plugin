"""Tokenomics CLI v2.0.0 — Cross-platform command-line interface.

Inspired by caveman and ponytail, engineered independently as its own system.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from ._logo import logo_path, tagline
from .core import compress_prose, estimate_tokens, ponytail_ladder, review_code
from .preview import write_preview
from .state import StateManager


def _print_logo() -> None:
    print(f"Tokenomics logo: {logo_path()}")
    print(tagline())
    print()


def cmd_enable(args: argparse.Namespace) -> int:
    state = StateManager().enable()
    write_preview(state)
    print("✓ Tokenomics enabled — prose compression + decision guidance active.")
    print("  Token savings shown on every output.")
    return 0


def cmd_disable(args: argparse.Namespace) -> int:
    state = StateManager().disable()
    write_preview(state)
    print("✓ Tokenomics disabled — no compression, no token-savings display.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    status = StateManager().status()
    print("╔═══════════════════════════════════════╗")
    print("║        Tokenomics Status              ║")
    print("╠═══════════════════════════════════════╣")
    print(f"║ Enabled:     {'YES' if status['enabled'] else 'NO':>27} ║")
    print(f"║ Level:       {status['level']:>27} ║")
    print(f"║ XP:          {status['xp']:>27} ║")
    print(f"║ Streak:      {status['current_streak']:>27} day(s) ║")
    print(f"║ Best streak: {status['best_streak']:>27} day(s) ║")
    print(f"║ Subagents:   {status['subagents_propagated']:>27} ║")
    print("║───────────────────────────────────────║")
    print(f"║ Achievements:{status['achievements_unlocked']:>3}/{status['total_achievements']:<23}║")
    print("║───────────────────────────────────────║")
    print(f"║ Original:    {status['original_chars']:>27} chars ║")
    print(f"║ Compressed:  {status['compressed_chars']:>26} chars ║")
    print(f"║ Saved:       {status['saved_chars']:>27} chars ║")
    print(f"║ Tokens saved:{status['estimated_tokens_saved']:>26} ║")
    print("╚═══════════════════════════════════════╝")
    return 0


def cmd_estimate(args: argparse.Namespace) -> int:
    text = args.text
    if not text:
        print("Error: text argument is required for estimate")
        return 1
    orig = estimate_tokens(text)
    compressed = compress_prose(text)
    comp_tok = estimate_tokens(compressed)
    saved = orig - comp_tok
    print(f"Original:  {orig} tokens")
    print(f"Compressed:{comp_tok} tokens")
    print(f"Saved:     {saved} tokens ({round((saved / orig) * 100) if orig else 0}% reduction)")
    print()
    print("Compressed preview:")
    print(compressed[:200])
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    if not args.code:
        print("Error: --code is required for review")
        return 1
    result = review_code(args.code)
    if not result["ok"]:
        print(f"Error: {result['error']}")
        return 1
    print("╔═══════════════════════════════════════╗")
    print("║      Ponytail Code Review             ║")
    print("╠═══════════════════════════════════════╣")
    if result["issues"]:
        print("║ Issues found:                         ║")
        for issue in result["issues"]:
            print(f"║   • {issue:<43}║")
    else:
        print("║ No issues detected — code is minimal. ║")
    print(f"║ Original:   {result['original_tokens']:>5} tokens   ║")
    print(f"║ Compressed: {result['compressed_tokens']:>5} tokens   ║")
    print(f"║ Savings:    {result['estimated_savings']:>5} tokens   ║")
    print("║───────────────────────────────────────║")
    print(f"║ {result['recommendation']:<43}║")
    print("╚═══════════════════════════════════════╝")
    print()
    print("Compressed preview:")
    print(result["compressed_preview"])
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    status = StateManager().status()
    saved_chars = status["original_chars"] - status["compressed_chars"]
    saved_tokens = saved_chars // 4
    ratio = (
        status["compressed_chars"] / status["original_chars"]
        if status["original_chars"] > 0
        else 1.0
    )
    print("╔═══════════════════════════════════════╗")
    print("║        Tokenomics Audit               ║")
    print("╠═══════════════════════════════════════╣")
    print(f"║ Enabled:     {'YES' if status['enabled'] else 'NO':>27} ║")
    print(f"║ Level:       {status['level']:>27} ║")
    print(f"║ XP:          {status['xp']:>27} ║")
    print(f"║ Streak:      {status['current_streak']:>27} day(s) ║")
    print(f"║ Turns:       {status['turns']:>27} ║")
    print(f"║ Subagents:   {status['subagents_propagated']:>27} ║")
    print("║───────────────────────────────────────║")
    print(f"║ Original:    {status['original_chars']:>27} chars ║")
    print(f"║ Compressed:  {status['compressed_chars']:>26} chars ║")
    print(f"║ Saved:       {saved_chars:>27} chars ║")
    print(f"║ Tokens saved:{saved_tokens:>26} ║")
    print(f"║ Ratio:       {ratio:.2f}                              ║")
    print("║───────────────────────────────────────║")
    print("║ Recommendations:                      ║")
    print("║   1. Enable tokenomics at session start║")
    print("║   2. Run tokenomics-review on large    ║")
    print("║      diffs before merging              ║")
    print("║   3. Preview widget at preview.html    ║")
    print("╚═══════════════════════════════════════╝")
    return 0


def cmd_ladder(args: argparse.Namespace) -> int:
    print(ponytail_ladder())
    return 0


def cmd_logo(args: argparse.Namespace) -> int:
    print(f"Logo: {logo_path()}")
    return 0


def cmd_domain(args: argparse.Namespace) -> int:
    """Manage domain rules and presets."""
    sm = StateManager()
    if args.domain_action == "never":
        sm.set_domain_rule(args.domain_name, "never_compress", True)
        print(f"✓ {args.domain_name} added to never-compress list")
    elif args.domain_action == "always":
        sm.set_domain_rule(args.domain_name, "always_compress", True)
        print(f"✓ {args.domain_name} added to always-compress list")
    elif args.domain_action == "preset":
        sm.set_domain_preset(args.domain_name, args.preset_name)
        print(f"✓ {args.domain_name} → preset {args.preset_name}")
    elif args.domain_action == "list":
        rules = sm.get_domain_rules()
        print("Never compress:", ", ".join(list(rules.never_compress)) or "none")
        print("Always compress:", ", ".join(list(rules.always_compress)) or "none")
        print("Force presets:", rules.force_preset or "none")
    return 0


def cmd_achievements(args: argparse.Namespace) -> int:
    newly = StateManager().check_achievements()
    if newly:
        print("🎉 New achievements unlocked:")
        for aid in newly:
            print(f"  • {aid}")
    else:
        print("No new achievements this session.")
    return 0


def cmd_budget(args: argparse.Namespace) -> int:
    """Set or check daily token budget."""
    sm = StateManager()
    if args.budget_action == "set":
        sm.set_token_budget(args.limit)
        print(f"✓ Daily token budget set to {args.limit} tokens")
    elif args.budget_action == "check":
        budget = sm.get_token_budget()
        if budget is None:
            print("No daily token budget set.")
        else:
            print(f"Daily token budget: {budget} tokens")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    """Record tokens consumed and check budget."""
    sm = StateManager()
    result = sm.record_tokens_used(args.tokens)
    if result["alert"]:
        print(result["alert"])
    print(f"Used today: {result['used_today']} tokens")
    if result["saved_today"]:
        print(f"Saved today: {result['saved_today']} tokens")
    return 0


def cmd_project(args: argparse.Namespace) -> int:
    """Set project type for smart defaults."""
    sm = StateManager()
    sm.set_project_type(args.type)
    print(f"✓ Project type set to: {args.type}")
    print("  Smart defaults will now suggest domain rules for this project type.")
    return 0


def cmd_learn(args: argparse.Namespace) -> int:
    """Toggle auto-learn from user reverts."""
    sm = StateManager()
    sm.set_auto_learn(args.enable)
    print(f"✓ Auto-learn {'enabled' if args.enable else 'disabled'}")
    return 0


def cmd_defaults(args: argparse.Namespace) -> int:
    """Toggle smart default suggestions."""
    sm = StateManager()
    sm.set_smart_defaults(args.enable)
    print(f"✓ Smart defaults {'enabled' if args.enable else 'disabled'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tokenomics",
        description="Tokenomics v2.0.0: Agentic Efficiency Layer — Beyond Caveman + Ponytail",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("enable", help="Enable tokenomics compression")
    subparsers.add_parser("disable", help="Disable tokenomics compression")
    subparsers.add_parser("status", help="Show tokenomics status")
    subparsers.add_parser("ladder", help="Show Tokenomics decision ladder")
    subparsers.add_parser("logo", help="Show ASCII logo")
    subparsers.add_parser("achievements", help="Check for new achievements")

    p_estimate = subparsers.add_parser("estimate", help="Estimate token savings for text")
    p_estimate.add_argument("text", nargs="?", help="Text to estimate")
    p_estimate.add_argument("--text", dest="text_flag", help="Text to estimate (alternative)")

    p_review = subparsers.add_parser("review", help="Ponytail code review")
    p_review.add_argument("--code", help="Code to review for over-engineering")

    subparsers.add_parser("audit", help="Full tokenomics audit")

    p_domain = subparsers.add_parser("domain", help="Manage domain rules")
    p_domain.add_argument("domain_action", choices=["never", "always", "preset", "list"])
    p_domain.add_argument("domain_name", nargs="?", help="Domain name")
    p_domain.add_argument("--preset", dest="preset_name", help="Preset name for preset action")

    # Enhanced features: budget, project type, smart defaults
    p_budget = subparsers.add_parser("budget", help="Set or check daily token budget")
    p_budget.add_argument("budget_action", choices=["set", "check"])
    p_budget.add_argument("limit", nargs="?", type=int, help="Daily token limit")

    p_record = subparsers.add_parser("record", help="Record tokens consumed and check budget")
    p_record.add_argument("tokens", type=int, help="Token count to record")

    p_project = subparsers.add_parser("project", help="Set project type for smart defaults")
    p_project.add_argument("type", choices=["web", "cli", "library", "api", "none"])

    p_learn = subparsers.add_parser("learn", help="Toggle auto-learn from user reverts")
    p_learn.add_argument("--enable", action="store_true")

    p_defaults = subparsers.add_parser("defaults", help="Toggle smart default suggestions")
    p_defaults.add_argument("--enable", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    _print_logo()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Handle --text alternative for estimate
    if args.command == "estimate" and not args.text and hasattr(args, "text_flag"):
        args.text = args.text_flag

    handlers: dict[str, Any] = {
        "enable": cmd_enable,
        "disable": cmd_disable,
        "status": cmd_status,
        "estimate": cmd_estimate,
        "review": cmd_review,
        "audit": cmd_audit,
        "ladder": cmd_ladder,
        "logo": cmd_logo,
        "domain": cmd_domain,
        "achievements": cmd_achievements,
        "budget": cmd_budget,
        "record": cmd_record,
        "project": cmd_project,
        "learn": cmd_learn,
        "defaults": cmd_defaults,
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
