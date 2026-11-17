---
name: tokenomics
description: "Tokenomics v2.3.0 agentic-efficiency suite: compress agent prose, minimize code generation, track token savings, token budget, gamification, subagent propagation. Cursor-compatible SKILL.md skill. Inspired by caveman and ponytail, engineered independently."
license: MIT
metadata:
  version: 2.3.0
  derived_from: "https://github.com/z99wE/tokenomics"
  original_license: MIT
  platforms:
    - cursor
---

# Tokenomics for Cursor

**Small mouth, big brain. Minimum code, maximum impact.**

Tokenomics is inspired by the concepts behind caveman (prose compression)
and ponytail (code minimization), engineered independently as its own Cursor
skill.

## What It Does

| Layer | What it compresses | Typical savings |
|-------|-------------------|-----------------|
| Caveman-inspired | Agent's **prose output** — drops articles, filler, pleasantries, hedging | ~65% fewer output tokens |
| Ponytail-inspired | Agent's **code output** — YAGNI decision ladder before any code | ~54% less code |

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

## Triggers

Say any of these in Cursor:

| Trigger | Effect |
|---------|--------|
| `tokenomics enable` | Activate compression + savings display |
| `tokenomics disable` | Deactivate — no compression, no footer |
| `tokenomics status` | View cumulative savings, level, streak |
| `tokenomics estimate <text>` | Preview savings for specific text |
| `tokenomics review <code>` | Ponytail-inspired over-engineering review |
| `tokenomics audit` | Full savings summary + recommendations |
| `tokenomics budget set <N>` | Set daily token budget |
| `tokenomics project web\|cli\|library\|api` | Set project type for smart defaults |
| `tokenomics learn true\|false` | Toggle auto-learn from user reverts |

## Installation

Copy this `SKILL.md` to `~/.cursor/skills/tokenomics/`.

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
