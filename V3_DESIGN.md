# Tokenomics v3.0.0 — Agentic-Era Design Document

**Repository:** https://github.com/z99wE/tokenomics  
**Version:** 3.0.0 (planned)  
**Status:** Design phase  
**License:** MIT

---

## Executive Summary

Tokenomics v1.0–2.0 explored **caveman-inspired prose compression** + **ponytail-inspired code minimization** into a single tool with token-savings estimation. It works, but it's fundamentally a *first implementation* — it doesn't add a unique capability that neither has alone.

**v3.0.0 changes that.** Tokenomics becomes an **agentic efficiency layer** that sits between the agent and its output, understanding *context*, *intent*, and *consequences* before compressing anything. It doesn't just shorten text — it understands *what* is being said, *why* it's being said, and *whether compressing it is safe*.

## The Core Differentiator

| | **Caveman-inspired** | **Ponytail-inspired** | **Tokenomics v3.0.0** |
|---|---------|----------|-------------------|
| **What it compresses** | Prose output | Code generation | **Both, with context awareness** |
| **Understands intent?** | No | No | **Yes** — classifies content before compressing |
| **Learns from feedback?** | No | No | **Yes** — tracks revert rates per pattern per context |
| **Safety-aware?** | Partial | Partial | **Yes** — never compresses secrets/auth/security code |
| **Cross-agent memory?** | No | No | **Yes** — shared learning state across all agents |
| **Integrates with other skills?** | No | No | **Yes** — code-reviewer, claude-coach |
| **Self-improving?** | No | No | **Yes** — adapts compression strategy based on user behavior |

**The unique value of Tokenomics:** It's not "compress text" + "minimize code." It's **context-aware, self-improving agentic efficiency** that knows *when* to compress, *when not to*, and *what* to compress based on content type, user history, and safety boundaries.

---

## Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER REQUEST                            │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  CONTEXT DETECTION LAYER                                    │
│  • code / docs / config / secrets / sql / prose            │
│  • security-sensitivity scan                               │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  STRATEGY SELECTION                                         │
│  • Domain preset (standard/docs/commit/review/chat/ultra)   │
│  • User preference history                                  │
│  • Learned patterns (revert rate < 50% = compress)         │
│  • Safety override (secrets/auth/crypto = never compress)  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  COMPRESSION ENGINE                                         │
│  • Caveman-inspired prose compression (drop filler/hedging/etc.)    │
│  • Ponytail-inspired code minimization (YAGNI-inspired ladder)               │
│  • Context-appropriate mix of both                         │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  TOKENOMICS LAYER                                           │
│  • Real token counting (tiktoken)                           │
│  • Savings tracking per turn / session / agent              │
│  • Gamification (levels, XP, streaks, achievements)         │
│  • Preview widget (HTML status dashboard)                   │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│  AGENTIC FEEDBACK LOOP                                      │
│  • User reverts → learned pattern updated                   │
│  • User accepts → pattern confidence increases              │
│  • Cross-agent propagation via delegate_task                │
│  • Coach integration (claude-coach skill)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Differentiators vs Caveman & Ponytail

### 1. Context-Aware Compression (Not One-Size-Fits-All)

Caveman treats all text the same: drop articles, filler, pleasantries. Ponytail treats all code the same: YAGNI ladder. Tokenomics **classifies content first**, then applies the right strategy:

| Content Type | Compression Strategy | Example |
|-------------|---------------------|---------|
| **Code** | Minimal — preserve structure, comments, imports | Only remove truly redundant patterns |
| **Docs** | Moderate — keep structure, cut filler | Remove "basically", "actually", etc. |
| **Commits** | Aggressive — conventional commit style | "Fix bug" not "Fix the bug in the login function" |
| **Secrets** | **Never compress** | API keys, tokens, passwords left untouched |
| **SQL** | Light — preserve query structure | Remove whitespace, keep semantics |
| **Prose** | Standard caveman | Drop articles, filler, hedging |

This means you never accidentally corrupt a config file or expose a secret by over-compressing.

### 2. Learned Compression (Self-Improving)

v3.0.0 tracks which compression patterns the user *reverts* vs *accepts*:

- If the user always un-compresses "basically → (removed)", Tokenomics stops dropping "basically" for that user
- If the user accepts "function → fn" 10 times and reverts 0 times, confidence increases
- Confidence < 50% = stop compressing that pattern
- Confidence > 50% = keep compressing

This means Tokenomics gets *better the more you use it*, personalized to your writing style.

### 3. Agentic-Era Features

**Cross-agent memory:** When you delegate a task to a subagent, Tokenomics context is applied. The subagent inherits your compression preferences, learned patterns, and safety rules.

**Safety-first by default:** Secrets, auth tokens, crypto keys, PII — never compressed, never modified. The safety gate is checked *before* any compression happens.

**Integration with other skills:**
- `code-reviewer` — Tokenomics pre-processes code before review, stripping boilerplate so the reviewer focuses on logic
- `claude-coach` — After compression, Tokenomics coaches: "You used 500 tokens to say what could be said in 50"

---

## File Structure Changes

```
tokenomics/
├── __init__.py              # Package init, exports all public API
├── _logo.py                 # ASCII logo
├── ascii_logo.txt           # ASCII art
├── cli.py                   # CLI: enable/disable/status/estimate/review/audit/domain/achievements
├── core.py                  # Caveman compression, ponytail ladder, token estimation
├── context.py               # Context detection (code/docs/config/secrets/sql/prose)
├── state.py                 # StateManager: persistence, gamification, domain rules
├── agentic.py               # AgenticCompressor: context detection + learned compression
├── hermes/__init__.py       # Hermes plugin: 8 tools + 6 hooks
├── hermes/plugin.yaml       # Plugin manifest
├── preview.py               # HTML preview widget
├── pyproject.toml           # Package config
├── scripts/install.sh       # Cross-platform installer
├── claude-code/SKILL.md     # Claude Code skill
├── cursor/SKILL.md          # Cursor skill
├── antigravity/SKILL.md     # Antigravity skill
├── codex/SKILL.md           # Codex skill
├── LICENSE
└── README.md
```

---

## CLI Commands

```
tokenomics <command> [options]

enable      Activate compression + savings display
disable     Deactivate — clean passthrough
status      Show cumulative savings, level, streak, achievements
estimate    Preview token savings for specific text
review      Tokenomics-style over-engineering review of code
audit       Full audit: savings, ratio, level, streak, recommendations
domain      Manage selective compression rules (never/always/preset/list)
achievements Check for newly unlocked achievements
ladder      Show decision ladder
logo        Show ASCII logo
context     Show detected context for a piece of text
coach       Get coaching on token-efficient communication
```

---

## Hermes Plugin: 8 Tools, 6 Hooks

**Tools:**
| Tool | Effect |
|------|--------|
| `tokenomics.enable` | Activate compression + savings display |
| `tokenomics.disable` | Deactivate — clean passthrough |
| `tokenomics.status` | Cumulative savings, level, streak, achievements |
| `tokenomics.estimate` | Preview before/after tokens for specific text |
|| `tokenomics.review` | Tokenomics-style over-engineering review |
| `tokenomics.audit` | Full audit with recommendations |
| `tokenomics.domain` | Manage selective compression rules |
| `tokenomics.achievements` | Check newly unlocked achievements |

**Hooks:**
| Hook | Effect |
|------|--------|
| `pre_llm_call` | Injects decision ladder into LLM context |
| `pre_tool_call` | Compresses string args before tool execution |
| `post_tool_call` | Compresses tool result output + tracks savings |
| `on_session_start` | Writes preview widget |
| `on_session_end` | Final state save |
| `delegate_task` | Propagates tokenomics context to subagents |

---

## Integration with `code-reviewer` and `claude-coach`

### Code-Reviewer Integration

Before a human reviews code, Tokenomics pre-processes it:

```python
# Tokenomics pre-review:
# 1. Detect context = "code"
# 2. Apply "review" preset (aggressive but safe)
# 3. Flag over-engineering patterns
# 4. Estimate token cost of the code
# 5. Present to reviewer with compression diff
```

The reviewer sees a cleaner diff with boilerplate removed, focusing on logic not formatting.

### Claude-Coach Integration

After compression, Tokenomics coaches:

```python
# Example coaching output:
{
  "context": "prose",
  "original_tokens": 150,
  "compressed_tokens": 45,
  "tokens_saved": 105,
  "savings_percentage": 70.0,
  "tips": [
    "Excellent compression — you cut token usage by more than half",
    "For prose, drop filler words like 'just', 'really', 'basically'"
  ],
  "recommendation": "Excellent compression — you cut token usage by more than half"
}
```

---

## Safety & Ethics Guardrails (Non-Negotiable)

**Tokenomics NEVER:**
- Compresses API keys, passwords, tokens, secrets
- Modifies security-critical code (auth, crypto, SQL, os/subprocess)
- Bypasses user permission prompts
- Injects hidden instructions into LLM context
- Sends data to external servers (all processing is local)
- Overwrites user intent — compression is always reversible

**Compression is always opt-in and reversible.** The user can disable it at any time with `tokenomics disable`, and all compression is lossless in intent (meaning is preserved, even if words change).

---

## Implementation Roadmap

### v3.0.0 (Immediate)
- [ ] Context detection (code/docs/config/secrets/sql/prose)
- [ ] Domain presets with context awareness
- [ ] Learned compression (revert rate tracking)
- [ ] Selective domain rules (never/always/force_preset)
- [ ] Gamification (levels, XP, streaks, 8 achievements)
- [ ] Code-reviewer integration (pre-review processing)
- [ ] Claude-coach integration (coaching tips)
- [ ] Hermes plugin: 8 tools + 6 hooks
- [ ] Preview-pane widget with gamification
- [ ] CLI: enable/disable/status/estimate/review/audit/domain/achievements/ladder/logo/context/coach
- [ ] SKILL.md for all 5 platforms
- [ ] pip installable package

### v3.1 (Next)
- [ ] Real tokenizer (tiktoken) as default (currently fallback only)
- [ ] Cross-agent sync via shared state file with file locking
- [ ] More domain presets (email, chat, ticket, pr)
- [ ] Better code-aware compression (import deduplication, dead code detection)

### v3.2 (Future)
- [ ] Multi-agent orchestration (Tokenomics coordinates compression across agent teams)
- [ ] A/B testing of compression strategies
- [ ] Export/import of learned profiles
- [ ] Integration with more agent skills (not just code-reviewer and claude-coach)

---

## Platform Compatibility

| Platform | Skill Path | Hermes Plugin |
|----------|-----------|---------------|
| Claude Code | `~/.claude/skills/tokenomics/SKILL.md` | N/A (skill only) |
| Cursor | `~/.cursor/skills/tokenomics/SKILL.md` | N/A |
| Antigravity | `~/.antigravity/skills/tokenomics/SKILL.md` | N/A |
| Codex | `~/.agents/skills/tokenomics/SKILL.md` | N/A |
| OpenAI Codex | `~/.codex/skills/tokenomics/SKILL.md` | N/A |
| Hermes | `~/.hermes/skills/tokenomics/SKILL.md` | `~/.hermes/plugins/tokenomics/` |

All platforms use the same open **SKILL.md** standard (agentskills.io). The Hermes plugin adds tool-level enforcement (`tokenomics.enable`, `tokenomics.disable`, etc.) and hook-based behavior (`pre_llm_call`, `pre_tool_call`, `post_tool_call`, `delegate_task`).

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## What This Is NOT

- **Not a prompt injection tool** — Tokenomics never adds hidden instructions to LLM context. It only compresses *output* text and applies *visible* decision guidance that the user can see and reject.
- **Not a safety bypass** — Tokenomics adds safety gates (never compress secrets/auth/crypto), it never removes them.
- **Not a replacement for human judgment** — Compression is always advisory. The user sees the original and compressed output and can choose either.
- **Not cloud-based** — All processing is local. No data leaves your machine.

---

## Links

- [GitHub Repository](https://github.com/z99wE/tokenomics)
- [Caveman (JuliusBrussee)](https://github.com/JuliusBrussee/caveman)
- [Ponytail (DietrichGebert)](https://github.com/DietrichGebert/ponytail)
- [Agent Skills Standard](https://agentskills.io)
