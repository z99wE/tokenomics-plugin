"""Tokenomics CLI - Cross-platform command-line interface."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from .core import compress_prose, estimate_tokens, ponytail_ladder, review_code
from .state import StateManager
from .preview import write_preview


def _print_logo() -> None:
    from ._logo import LOGO, TAGLINE
    print(LOGO)
    print()


def cmd_enable(args: argparse.Namespace) -> int:
    state = StateManager().enable()
    from .preview import write_preview
    write_preview(state)
    print("✓ Tokenomics enabled — prose compression + ponytail guidance active.")
    print("  Token savings shown on every output.")
    return 0


def cmd_disable(args: argparse.Namespace) -> int:
    state = StateManager().disable()
    from .preview import write_preview
    write_preview(state)
    print("✓ Tokenomics disabled — no compression, no token-savings display.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    status = StateManager().status()
    print("╔═══════════════════════════════════════╗")
    print("║        Tokenomics Status              ║")
    print("╠═══════════════════════════════════════╣")
    print(f"║ Enabled:     {'YES' if status['enabled'] else 'NO':>27} ║")
    print(f"║ Turns:       {status['turns']:>27} ║")
    print(f"║ Subagents:   {status['subagents_propagated']:>27} ║")
    print(f"║───────────────────────────────────────║")
    print(f"║ Original:    {status['original_chars']:>27} chars ║")
    print(f"║ Compressed:  {status['compressed_chars']:>26} chars ║")
    print(f"║ Saved:       {status['saved_chars']:>27} chars ║")
    print(f"║ Tokens saved:{status['estimated_tokens_saved']:>26} ║")
    print("╚═══════════════════════════════════════╝")
    return 0


def cmd_estimate(args: argparse.Namespace) -> int:
    text = args.text
    if not text:
        print("Error: --text is required for estimate")
        return 1
    orig = estimate_tokens(text)
    compressed = compress_prose(text)
    comp_tok = estimate_tokens(compressed)
    saved = orig - comp_tok
    print(f"Original:  {orig} tokens")
    print(f"Compressed:{comp_tok} tokens")
    print(f"Saved:     {saved} tokens ({orig - saved if saved > 0 else 0}% reduction)")
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
    print(f"║───────────────────────────────────────║")
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
    print(f"║ Turns:       {status['turns']:>27} ║")
    print(f"║ Subagents:   {status['subagents_propagated']:>27} ║")
    print(f"║───────────────────────────────────────║")
    print(f"║ Original:    {status['original_chars']:>27} chars ║")
    print(f"║ Compressed:  {status['compressed_chars']:>26} chars ║")
    print(f"║ Saved:       {saved_chars:>27} chars ║")
    print(f"║ Tokens saved:{saved_tokens:>26} ║")
    print(f"║ Ratio:       {ratio:.2f}                              ║")
    print("║───────────────────────────────────────║")
    print("║ Recommendations:                      ║")
    print("║   1. Enable tokenomics at session start║")
    print("║   2. Run /tokenomics-review on large   ║")
    print("║      diffs before merging              ║")
    print("║   3. Preview widget at preview.html    ║")
    print("╚═══════════════════════════════════════╝")
    return 0


def cmd_ladder(args: argparse.Namespace) -> int:
    print(ponytail_ladder())
    return 0


def cmd_logo(args: argparse.Namespace) -> int:
    _print_logo()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tokenomics",
        description="Tokenomics: Caveman + Ponytail = Maximum Efficiency",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("enable", help="Enable tokenomics compression")
    subparsers.add_parser("disable", help="Disable tokenomics compression")
    subparsers.add_parser("status", help="Show tokenomics status")
    subparsers.add_parser("ladder", help="Show ponytail YAGNI decision ladder")
    subparsers.add_parser("logo", help="Show ASCII logo")

    p_estimate = subparsers.add_parser("estimate", help="Estimate token savings for text")
    p_estimate.add_argument("text", nargs="?", help="Text to estimate")
    p_estimate.add_argument("--text", dest="text_flag", help="Text to estimate (alternative)")

    p_review = subparsers.add_parser("review", help="Ponytail code review")
    p_review.add_argument("--code", help="Code to review for over-engineering")

    subparsers.add_parser("audit", help="Full tokenomics audit")

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
    }

    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
