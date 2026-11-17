---
name: tokenomics
description: "Tokenomics v2.3.0 agentic-efficiency suite: compress agent prose, minimize code generation, track token savings, token budget, gamification, subagent propagation. Works with Claude Code, Cursor, Antigravity, Codex, Hermes, and other SKILL.md-compatible agents. Inspired by caveman and ponytail, engineered independently."
license: MIT
metadata:
  version: 2.3.0
  derived_from: "https://github.com/z99wE/tokenomics"
  original_license: MIT
  components:
    caveman_inspired: "prose compression — drops articles, filler, pleasantries, hedging (~65% fewer output tokens)"
    ponytail_inspired: "code minimization — YAGNI decision ladder before any code (~54% less code)"
    tokenomics: "estimated token savings displayed on every output when active"
    budget: "daily token budget with 80%/100% alerts"
    gamification: "levels, XP, streaks, achievements"
    subagent_propagation: "context applied to delegate_task subagents"
  platforms:
    - claude-code
    - cursor
    - antigravity
    - codex
    - hermes
    - openai-codex
---

# Tokenomics for Claude Code

**Small mouth, big brain. Minimum code, maximum impact.**

Tokenomics is inspired by the concepts behind caveman (prose compression)
and ponytail (code minimization), engineered independently as its own
system for Claude Code.

## What It Does

| Layer | What it compresses | Typical savings |
|-------|-------------------|-----------------|
| Caveman-inspired | Agent's **prose output** — drops articles, filler, pleasantries, hedging | ~65% fewer output tokens |
| Ponytail-inspired | Agent's **code output** — YAGNI decision ladder before any code | ~54% less code |

They don't overlap. Caveman-inspired leaves code byte-for-byte exact. Ponytail-inspired stays out of the prose. Use them together for compound savings.

## Mermaid Architecture

```mermaid
flowchart TD
    A[User Request] --> B{Tokenomics<br/>Enabled?}
    B -->|No| C[Normal Output<br/>No Compression]
    B -->|Yes| D[Context Detection<br/>Code / Docs / Config / Secrets / SQL / Prose]
    D -->|Security Sensitive| E[Skip Compression<br/>Safety First]
    D -->|Safe to Compress| F[Selective Domain Rules<br/>Never / Always / Force Preset]
    F --> G[Learned Compression<br/>Adapts to Your Revert Patterns]
    G --> H[Caveman-Inspired Prose Compression]
    H --> I[Ponytail-Inspired Code Minimization]
    I --> J[Token Savings Estimation]
    J --> K[Token Budget Check<br/>80% / 100% Alerts]
    K --> L[Gamification<br/>XP / Level / Streak / Achievements]
    L --> M[Subagent Propagation<br/>delegate_task Context]
    M --> N[Output with Savings Footer]
```

## Ponytail-Inspired Decision Ladder

Before writing any code, climb this ladder and stop at the first rung that holds:

1. Does this need to exist? (YAGNI — skip it)
2. Already in this codebase? (reuse it)
3. Stdlib does it? (use it)
4. Native platform feature? (use it)
5. Installed dependency solves it? (use it)
6. Can it be one line? (write one line)
7. Only then: minimum code that works

Never cut validation, error handling, security, or accessibility.

## Triggers

Say any of these in Claude Code:

| Trigger | Effect |
|---------|--------|
| `tokenomics enable` | Activate compression + savings display |
| `tokenomics disable` | Deactivate — no compression, no footer |
| `tokenomics status` | View cumulative savings, level, streak |
| `tokenomics estimate <text>` | Preview savings for specific text |
| `tokenomics review <code>` | Ponytail-inspired over-engineering review |
| `tokenomics audit` | Full savings summary + recommendations |
| `tokenomics budget set <N>` | Set daily token budget |
| `tokenomics budget check` | Check current budget usage |
| `tokenomics project web\|cli\|library\|api` | Set project type for smart defaults |
| `tokenomics learn true\|false` | Toggle auto-learn from user reverts |

## Installation

Copy this `SKILL.md` to `~/.claude/skills/tokenomics/`.

Or install via pip:

```bash
pip install tokenomics
tokenomics enable
```

## License

MIT License.

## Inspiration

Tokenomics is **inspired by** caveman (prose compression) and ponytail (code minimization), but engineered independently as its own project.

- GitHub: https://github.com/z99wE/tokenomics
- caveman: https://github.com/JuliusBrussee/caveman
- ponytail: https://github.com/DietrichGebert/ponytail
