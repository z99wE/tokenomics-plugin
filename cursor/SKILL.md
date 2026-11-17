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

## Architecture

```mermaid
flowchart TD
    A([User Request]) --> B{Tokenomics<br/>Enabled?}
    B -->|No| R[Normal Output<br/>No Compression]
    B -->|Yes| D[Context Detection<br/>Code · Docs · Config · Secrets · SQL · Prose]

    D --> E{Security<br/>Sensitive?}
    E -->|Yes| F[Skip Compression<br/>Safety First]
    E -->|No| G[Safe to Compress]

    F --> D
    G --> H[Selective Domain Rules<br/>Never · Always · Force Preset]
    H --> I[Learned Compression<br/>Adapts to Revert Patterns]
    I --> J[Caveman-Inspired<br/>Prose Compression]
    J --> K[Ponytail-Inspired<br/>Code Minimization]
    K --> L[Token Savings<br/>Estimation]

    L --> M[Token Budget Check<br/>80% / 100% Alerts]
    M --> N[Gamification<br/>XP · Level · Streak · Achievements]
    N --> O[Subagent Propagation<br/>delegate_task Context]
    O --> P([Output + Savings Footer])

    classDef entry fill:#dbeafe,stroke:#1e40af,stroke-width:2px,color:#1e3a8a
    classDef gate fill:#fef3c7,stroke:#92400e,stroke-width:2px,color:#78350f
    classDef safety fill:#fee2e2,stroke:#991b1b,stroke-width:2px,color:#7f1d1d
    classDef compress fill:#dcfce7,stroke:#166534,stroke-width:2px,color:#14532d
    classDef feature fill:#ede9fe,stroke:#5b21b6,stroke-width:2px,color:#4c1d95
    classDef done fill:#d1fae5,stroke:#065f46,stroke-width:2px,color:#064e3b
    classDef skip fill:#fecaca,stroke:#b91c1c,stroke-width:2px,color:#7f1d1d

    class A,P entry
    class B,D,E gate
    class F safety
    class G,H,I,J,K,L compress
    class M,N,O feature
    class P done
    class F,R skip
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
