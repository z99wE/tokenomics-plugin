---
name: tokenomics
description: "Merged caveman + ponytail: compress agent prose, minimize code generation, track token savings. Cursor-compatible SKILL.md skill."
license: MIT
metadata:
  version: 0.2.0
  derived_from: "https://github.com/z99wE/tokenomics"
  original_license: MIT
  platforms:
    - cursor
---

# Tokenomics for Cursor

**Small mouth, big brain. Minimum code, maximum impact.**

Tokenomics merges **caveman** (prose compression) + **ponytail** (code minimization) into one Cursor skill with token-savings estimation.

## Mermaid Architecture

```mermaid
flowchart TD
    A[User Request] --> B{Tokenomics<br/>Enabled?}
    B -->|No| C[Normal Output<br/>No Compression]
    B -->|Yes| D[Caveman Compression<br/>Drop filler, articles, hedging]
    D --> E[Ponytail Ladder<br/>YAGNI → Stdlib → Native → Dep → One line → Minimum]
    E --> F[Token Savings Estimation]
    F --> G[Preview Widget<br/>Live status dashboard]
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style D fill:#bfb,stroke:#333
    style E fill:#bfb,stroke:#333
    style F fill:#fbf,stroke:#333
    style G fill:#ffb,stroke:#333
```

## Triggers

Say any of these in Cursor:
- `tokenomics enable` / `tokenomics disable`
- `caveman mode` / `ponytail mode`
- `less tokens` / `minimal code`

## Ponytail Ladder

```mermaid
graph LR
    1[1. Does this need to exist?] --> 2[2. Already in codebase?]
    2 --> 3[3. Stdlib does it?]
    3 --> 4[4. Native feature?]
    4 --> 5[5. Installed dependency?]
    5 --> 6[6. Can it be one line?]
    6 --> 7[7. Minimum code]
    style 7 fill:#9f9,stroke:#333
```

## Installation

Copy this `SKILL.md` to `~/.cursor/skills/tokenomics/`.

Or install via pip:
```bash
pip install tokenomics
```

## License

MIT License.
