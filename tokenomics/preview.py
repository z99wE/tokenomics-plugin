"""HTML preview widget for Tokenomics v1.0.0 — with gamification."""

from __future__ import annotations

import os
from typing import Any


def _achievement_html(aid: str, a: dict[str, Any]) -> str:
    unlocked = a.get("unlocked", False)
    icon = "🔓" if unlocked else "🔒"
    cls = "achievement" + (" unlocked" if unlocked else " locked")
    desc = a.get("description", "")
    return (
        f'<div class="{cls}">'
        f'<span class="achievement-icon">{icon}</span>'
        f'<div style="font-size:11px;font-weight:600">{a.get("name", aid)}</div>'
        f'<div style="font-size:9px;opacity:0.6;margin-top:2px">{desc[:35]}</div>'
        f"</div>"
    )


def write_preview(state: dict[str, Any], preview_path: str | None = None) -> str:
    """Write preview-pane HTML widget for tokenomics status with gamification."""
    path = preview_path or os.path.expanduser(
        "~/.hermes/plugins/tokenomics/preview.html"
    )

    enabled = state.get("enabled", False)
    saved_chars = state.get("total_original_chars", 0) - state.get("total_compressed_chars", 0)
    saved_tokens = saved_chars // 4
    turns = state.get("turns", 0)
    subagents = state.get("subagents_propagated", 0)
    level = state.get("level", 1)
    xp = state.get("xp", 0)
    streak = state.get("current_streak", 0)
    best_streak = state.get("best_streak", 0)

    achs = state.get("achievements", {})
    unlocked_count = sum(1 for a in achs.values() if a.get("unlocked"))
    total_achs = len(achs)

    status_color = "#10b981" if enabled else "#ef4444"
    status_text = "ACTIVE" if enabled else "DISABLED"

    # Level progress bar
    total_saved = state.get("total_tokens_saved", 0)
    level_progress = min(100, (total_saved % 10000) / 10000 * 100)

    achievement_items = "".join(_achievement_html(aid, a) for aid, a in achs.items())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tokenomics Status</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    padding: 20px;
    min-height: 420px;
  }}
  .card {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px;
    backdrop-filter: blur(12px);
  }}
  .header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }}
  .status-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 24px;
    font-size: 12px;
    font-weight: 700;
    background: rgba({status_color.lstrip('#')}, 0.15);
    color: {status_color};
    border: 1px solid {status_color};
  }}
  .status-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: {status_color};
    animation: {('pulse 2s infinite' if enabled else 'none')};
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  h1 {{
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
  }}
  .subtitle {{
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
  }}
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 24px;
  }}
  .stat {{
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 16px;
  }}
  .stat-label {{
    font-size: 11px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 8px;
    letter-spacing: 0.08em;
    font-weight: 600;
  }}
  .stat-value {{
    font-size: 28px;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    line-height: 1;
  }}
  .stat-value.green {{ color: #34d399; }}
  .stat-value.blue {{ color: #60a5fa; }}
  .stat-value.purple {{ color: #a78bfa; }}
  .stat-value.orange {{ color: #fbbf24; }}
  .level-bar {{
    margin-top: 28px;
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 20px;
  }}
  .level-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }}
  .level-text {{
    font-size: 13px;
    font-weight: 600;
    color: #f8fafc;
  }}
  .progress-track {{
    height: 8px;
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    overflow: hidden;
  }}
  .progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, #34d399, #a78bfa);
    width: {level_progress:.1f}%;
    border-radius: 4px;
    transition: width 0.5s ease;
  }}
  .achievements {{
    margin-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.08);
    padding-top: 20px;
  }}
  .achievements-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}
  .achievements-title {{
    font-size: 13px;
    font-weight: 600;
    color: #cbd5e1;
  }}
  .achievements-count {{
    font-size: 12px;
    color: #94a3b8;
  }}
  .achievements-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }}
  .achievement {{
    background: rgba(15, 23, 42, 0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    font-size: 10px;
    color: #94a3b8;
  }}
  .achievement.unlocked {{
    border-color: #34d399;
    color: #34d399;
    background: rgba(52, 211, 153, 0.1);
  }}
  .achievement-icon {{
    font-size: 18px;
    margin-bottom: 4px;
    display: block;
  }}
  .controls {{
    margin-top: 28px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }}
  .btn {{
    flex: 1;
    min-width: 110px;
    padding: 12px 18px;
    border: 1px solid #475569;
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.5);
    color: #f8fafc;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .btn:hover {{ border-color: #64748b; background: rgba(30, 41, 59, 0.8); }}
  .btn.primary {{
    background: {status_color};
    border-color: {status_color};
    color: #ffffff;
  }}
  .btn.primary:hover {{ opacity: 0.9; }}
  .btn.secondary {{ background: transparent; }}
  .footer {{
    margin-top: 24px;
    font-size: 10px;
    color: #64748b;
    text-align: center;
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 16px;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="status-badge">
        <div class="status-dot"></div>
        {status_text}
      </div>
      <div>
        <h1>Tokenomics v1.0.0</h1>
        <p class="subtitle">Caveman prose + Ponytail code • Gamified token savings</p>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat">
        <div class="stat-label">Tokens Saved</div>
        <div class="stat-value green">{saved_tokens}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Chars Compressed</div>
        <div class="stat-value blue">{saved_chars}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Turns</div>
        <div class="stat-value purple">{turns}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Subagents</div>
        <div class="stat-value orange">{subagents}</div>
      </div>
    </div>

    <div class="level-bar">
      <div class="level-header">
        <span class="level-text">Level {level}</span>
        <span class="level-text">{xp} XP</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill"></div>
      </div>
    </div>

    <div class="achievements">
      <div class="achievements-header">
        <span class="achievements-title">Achievements</span>
        <span class="achievements-count">{unlocked_count}/{total_achs}</span>
      </div>
      <div class="achievements-grid">
        {achievement_items}
      </div>
    </div>

    <div class="controls">
      <button class="btn {'primary' if not enabled else 'secondary'}" onclick="window.hermes.send('tokenomics.{'enable' if not enabled else 'disable'}')">
        {'Enable' if not enabled else 'Disable'}
      </button>
      <button class="btn secondary" onclick="location.reload()">Refresh</button>
      <button class="btn secondary" onclick="window.hermes.send('tokenomics.audit')">Audit</button>
    </div>

    <div class="footer">
      Tokenomics v1.0.0 • Enhanced Caveman + Ponytail • Streak: {streak} day(s)
    </div>
  </div>
  <script>
    setInterval(() => {{ location.reload(); }}, 5000);
  </script>
</body>
</html>"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(html)
    return path
