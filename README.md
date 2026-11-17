![Tokenomics](assets/logo.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Tests: 135 passing](https://img.shields.io/badge/Tests-135%20passing-brightgreen.svg)](https://github.com/z99wE/tokenomics)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-supported-green.svg)](https://claude.ai/code)
[![Cursor](https://img.shields.io/badge/Cursor-supported-green.svg)](https://cursor.sh)
[![Antigravity](https://img.shields.io/badge/Antigravity-supported-green.svg)](https://antigravity.sh)
[![Codex](https://img.shields.io/badge/Codex-supported-green.svg)](https://openai.com/codex)
[![Hermes](https://img.shields.io/badge/Hermes-supported-green.svg)](https://hermes-agent.nousresearch.com)

---

# Tokenomics

**Tokenomics is an agentic efficiency layer** that sits between your AI agent and its output. It compresses agent prose, minimizes code generation, tracks token savings, and learns from your behavior — all while keeping safety and authorization at the forefront.

Tokenomics is **inspired by** the concepts behind [caveman](https://github.com/JuliusBrussee/caveman) (prose compression) and [ponytail](https://github.com/DietrichGebert/ponytail) (code minimization), but it is **engineered independently** as its own system with context awareness, learned compression, gamification, subagent propagation, token budgeting, and cross-agent memory.

---

## What Makes Tokenomics Different

| Capability | Caveman | Ponytail | Tokenomics v2.3 |
|------------|---------|----------|-----------------|
| Compresses prose | ✅ | ❌ | ✅ |
| Minimizes code | ❌ | ✅ | ✅ |
| Context-aware (code vs docs vs secrets) | ❌ | ❌ | **✅** |
| Learned compression (adapts to your reverts) | ❌ | ❌ | **✅** |
| Selective domain rules | ❌ | ❌ | **✅** |
| Token budget with 80%/100% alerts | ❌ | ❌ | **✅** |
| Project-type smart defaults | ❌ | ❌ | **✅** |
| Gamification (levels, XP, streaks) | ❌ | ❌ | **✅** |
| Subagent propagation | ❌ | ❌ | **✅** |
| Preview widget | ❌ | ❌ | **✅** |
| No injection hook | N/A | N/A | **✅** |
| 135 test cases | ❌ | ❌ | **✅** |

Tokenomics is not a wrapper around either tool. It is a **separate engineering project** that draws inspiration from their concepts and builds its own architecture on top.

---

## Mermaid Architecture

```mermaid
flowchart TD
    subgraph Start ["Start"]
        A([User Request]) --> B{Tokenomics<br/>Enabled?}
    end

    subgraph Safety ["Safety Gate"]
        D[Context<br/>Detection] --> E[Security<br/>Sensitive?]
        E -->|Yes| F[Skip<br/>Compression]
        E -->|No| G[Safe to<br/>Compress]
    end

    subgraph Compress ["Compression Pipeline"]
        G --> H[Selective<br/>Domain Rules]
        H --> I[Learned<br/>Compression]
        I --> J[Prose<br/>Compression]
        J --> K[Code<br/>Minimization]
        K --> L[Token<br/>Savings]
    end

    subgraph Features ["Features"]
        L --> M[Budget<br/>Check]
        M --> N[Gamification<br/>XP / Streaks]
        N --> O[Preview<br/>Widget]
        O --> P[Subagent<br/>Propagation]
    end

    subgraph Final ["End"]
        P --> Q[Output with<br/>Savings Footer]
    end

    B -->|No| R[Normal<br/>Output]
    B -->|Yes| D
    F --> D

    classDef start fill:#f9f,stroke:#333,stroke-width:2px
    classDef safety fill:#bbf,stroke:#333,stroke-width:2px
    classDef compress fill:#bfb,stroke:#333,stroke-width:2px
    classDef features fill:#ffd700,stroke:#333,stroke-width:2px
    classDef completed fill:#9f9,stroke:#333,stroke-width:2px
    classDef skip fill:#f96,stroke:#333,stroke-width:2px

    class A,B start
    class D,E,F safety
    class H,I,J,K,L compress
    class M,N,O,P features
    class Q completed
    class F skip
```

---

## Ponytail-Inspired Decision Ladder

```mermaid
graph LR
    subgraph YAGNI ["YAGNI Ladder"]
        1[1. Need<br/>it?] --> 2[2. In<br/>codebase?]
        2 --> 3[3. Stdlib?]
        3 --> 4[4. Native?]
        4 --> 5[5. Dep?]
        5 --> 6[6. One<br/>line?]
        6 --> 7[7. Min<br/>code]
    end

    style 1 fill:#ffcccc,stroke:#333,stroke-width:2px
    style 2 fill:#ffcccc,stroke:#333,stroke-width:2px
    style 3 fill:#ffcccc,stroke:#333,stroke-width:2px
    style 4 fill:#ffcccc,stroke:#333,stroke-width:2px
    style 5 fill:#ffcccc,stroke:#333,stroke-width:2px
    style 6 fill:#ffcccc,stroke:#333,stroke-width:2px
    style 7 fill:#ccffcc,stroke:#333,stroke-width:2px
```

---

## Subagent Propagation

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant S as Subagent

    autonumber

    U->>A: delegate_task<br/>with task
    Note over A: Tokenomics applies<br/>context + decision guidance
    A->>S: task with tokenomics<br/>rules applied
    S->>S: Compresses prose<br/>Applies YAGNI ladder<br/>Reports savings
    S->>A: Compressed output<br/>+ savings footer
    A->>U: Aggregated result
```

---

## Context-Aware Compression

Tokenomics doesn't blindly compress everything. It first **detects what kind of content** it's looking at:

| Content Type | Strategy | Example |
|-------------|----------|---------|
| **Code** | Minimal — preserve structure, imports, comments | Only remove truly redundant patterns |
| **Docs** | Moderate — keep structure, cut filler | Remove "basically", "actually", etc. |
| **Commits** | Aggressive — conventional commit style | "Fix bug" not "Fix the bug in the login function" |
| **Secrets / Auth** | **Never compress** | API keys, passwords, tokens left untouched |
| **SQL** | Light — preserve query structure | Remove whitespace, keep semantics |
| **Prose** | Standard — drop articles, filler, hedging | Remove "just", "really", "basically" |

Security-sensitive content (API keys, passwords, crypto keys) is **never** compressed or modified.

---

## Core Features

### Caveman-Inspired Prose Compression
Drops articles (a/an/the), filler words (just/really/basically), pleasantries (sure/certainly), and hedging (maybe/I think). Keeps code blocks, technical terms, API names, and error strings exact.

### Ponytail-Inspired Code Minimization
Before writing code, climbs the YAGNI ladder:
1. Does this need to exist? → Skip it
2. Already in codebase? → Reuse it
3. Stdlib does it? → Use it
4. Native platform feature? → Use it
5. Installed dependency? → Use it
6. Can it be one line? → Write one line
7. Only then: minimum code that works

### Token Savings Estimation
Real token counting via tiktoken (cl100k_base) with character-count fallback. Every compressed output shows estimated tokens saved.

### Token Budget with Alerts
Set a daily token budget and get notified at 80% and 100% usage:
```bash
tokenomics budget set 5000      # Set daily limit
tokenomics budget record 4200   # Record tokens used
# ⚠️ Token budget alert: 4200/5000 used (84%)
```

### Gamification
Levels, XP, streaks, and achievements (First Savings, Token Hoarder, Token Miser, Lazy Senior Dev, YAGNI Master, Three-Day Streak, Week Warrior) give you feedback on your token efficiency.

### Selective Domain Compression
Never compress security/auth/crypto content. Always compress docs/changelog. Force specific presets per domain. Learned compression adapts based on what you revert vs accept.

### Auto-Learn
Tokenomics tracks which compression patterns you revert vs accept, and automatically adapts future compression decisions.

### Project-Type Smart Defaults
Set your project type (web/cli/library/api) for smart default domain rules.

---

## Subagent Propagation

When you delegate a task to a subagent, Tokenomics context is automatically applied — the compression rules, learned patterns, and safety guidelines all carry over.

---

## Hermes Plugin: 11 Tools, 5 Hooks

**Tools:**
| Tool | What it does |
|------|-----------|
| `tokenomics.enable` | Activate compression + savings display |
| `tokenomics.disable` | Deactivate — no compression, no footer |
| `tokenomics.status` | Cumulative savings, level, streak, achievements |
| `tokenomics.estimate` | Preview savings for specific text |
| `tokenomics.review` | Ponytail-inspired over-engineering review |
| `tokenomics.audit` | Full audit with recommendations |
| `tokenomics.domain` | Manage selective compression rules |
| `tokenomics.achievements` | Check newly unlocked achievements |
| `tokenomics.budget` | Daily token budget + 80%/100% alerts |
| `tokenomics.project` | Project type for smart defaults |
| `tokenomics.learn` | Auto-learn from user revert patterns |

**Hooks:**
| Hook | What it does |
|------|-----------|
| `pre_tool_call` | Compresses string arguments before tool execution |
| `post_tool_call` | Compresses tool result output + tracks savings |
| `on_session_start` | Writes preview widget |
| `on_session_end` | Final state save + preview refresh |
| `delegate_task` | Propagates tokenomics context to subagents |

> **No injection hook.** The `pre_llm_call` hook was removed in v2.1.0. Tokenomics never prepends hidden instructions to your LLM prompts.

---

## CLI Reference

```
tokenomics <command> [options]

Commands:
  enable      Activate compression + savings display
  disable     Deactivate — no compression, no footer
  status      Show cumulative savings and compression ratio
  estimate    Preview token savings for specific text
  review      Ponytail-style over-engineering review of code
  audit       Full audit: savings, ratio, recommendations
  ladder      Show ponytail YAGNI decision ladder
  logo        Show ASCII logo
  domain      Manage selective compression rules
  achievements Check for newly unlocked achievements
  budget      Daily token budget + alerts
  record      Record tokens consumed and check budget
  project     Set project type for smart defaults
  learn       Toggle auto-learn from user reverts
  defaults    Toggle smart default suggestions
```

**Examples:**
```bash
tokenomics enable
tokenomics estimate "This is a really simple test."
tokenomics review --code "class UserFactoryManagerServiceController: ..."
tokenomics budget set 5000
tokenomics budget record 4200
tokenomics project web
tokenomics learn true
tokenomics disable
```

---

## Installation

### Option 1: pip (recommended)
```bash
pip install tokenomics
tokenomics enable
```

### Option 2: With real tokenizer
```bash
pip install "tokenomics[tiktoken]"
tokenomics enable
```

### Option 3: From source
```bash
git clone https://github.com/z99wE/tokenomics.git
cd tokenomics
pip install -e .
tokenomics enable
```

### Option 4: Manual skill copy
Copy `SKILL.md` to your agent's skills directory:

| Platform | Path |
|----------|------|
| Claude Code | `~/.claude/skills/tokenomics/SKILL.md` |
| Cursor | `~/.cursor/skills/tokenomics/SKILL.md` |
| Antigravity | `~/.antigravity/skills/tokenomics/SKILL.md` |
| Codex | `~/.agents/skills/tokenomics/SKILL.md` |
| OpenAI Codex | `~/.codex/skills/tokenomics/SKILL.md` |
| Hermes | `~/.hermes/skills/tokenomics/SKILL.md` + plugin install |

All platforms use the same open **SKILL.md** standard (agentskills.io).

---

## Testing

Tokenomics has **135 test cases** covering core compression, state management, Hermes plugin handlers/hooks, and CLI commands:

```bash
python -m unittest tokenomics.tests.test_core tokenomics.tests.test_hermes tokenomics.tests.test_cli -v
```

All 135 tests pass. The project uses **ruff** for linting:

```bash
ruff check .
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Inspiration & Attribution

Tokenomics is **inspired by** the concepts behind:
- **[caveman](https://github.com/JuliusBrussee/caveman)** — prose compression
- **[ponytail](https://github.com/DietrichGebert/ponytail)** — code minimization

Tokenomics is **engineered independently** as its own project. It reimplements these concepts with its own architecture, context detection, learned compression, gamification, token budgeting, and agentic features. All code in this repository is original work by the Tokenomics contributors.

---

## Links

- [GitHub Repository](https://github.com/z99wE/tokenomics)
- [caveman](https://github.com/JuliusBrussee/caveman) — inspiration for prose compression
- [ponytail](https://github.com/DietrichGebert/ponytail) — inspiration for code minimization
- [Agent Skills Standard](https://agentskills.io)
- [dsh-plugin.org](https://dsh-plugin.org) — DeepSeek Harness Plugin hub

---

## DSH Plugin Submission (DeepSeek Harness)

Tokenomics is also published as a **DSH Plugin** for the DeepSeek Harness ecosystem.

### Submission Details

| Field | Value |
|-------|-------|
| **Repository** | https://github.com/z99wE/tokenomics |
| **Author** | Souvik Chakraborty |
| **License** | MIT |
| **Category** | Tools & Capabilities |
| **Profile** | web |
| **Entry Point** | `apply.js` (exports `apply(ctx)`) |
| **Package** | `tokenomics-dsh-plugin` |

### Install Command

```bash
# From NPM (when published):
dsh plugin --profile web add tokenomics-dsh-plugin

# From source (works now):
dsh plugin --profile web add github:z99wE/tokenomics
```

### Pre-submission Checklist

- [x] Repository is public
- [x] GitHub topic `dsh-plugin` added
- [x] README includes install command
- [x] Plugin exports `apply(ctx)` module (`apply.js`)
- [x] Repository root includes `package.json`
- [x] Open-source license declared (MIT)
- [ ] Publish to NPM (optional — for Plugin Hub listing)
- [ ] Add `dsh-plugin` topic on GitHub

### DSH Plugin FAQ

**Does submitting cost money?**
No. Submitting a DSH Plugin is completely free.

**How long does review take?**
Depends on whether the repository meets the requirements. Publish a public repo, add the `dsh-plugin` topic, write a solid README, and the plugin is usually listed within one refresh cycle.

**Why hasn't my plugin been listed?**
Common reasons: repo not public, `dsh-plugin` topic missing, no `package.json` at root, no install command in README, or no `apply(ctx)` export.

**Is my plugin marked "unconfirmed"?**
Newly listed plugins start as `unconfirmed` and become verified after manual review. Polish your README with install and usage notes to speed it up.

**Can I submit a non-open-source plugin?**
No. The hub only lists plugins from public repositories with source access.
