"""HTML preview widget for Tokenomics status."""

from __future__ import annotations

import os
from typing import Any


def write_preview(state: dict[str, Any], preview_path: str | None = None) -> str:
    """Write preview-pane HTML widget for tokenomics status."""
    path = preview_path or os.path.expanduser(
        "~/.hermes/plugins/tokenomics/preview.html"
    )

    enabled = state.get("enabled", False)
    saved_chars = state.get("total_original_chars", 0) - state.get("total_compressed_chars", 0)
    saved_tokens = saved_chars // 4
    turns = state.get("turns", 0)
    subagents = state.get("subagents_propagated", 0)

    status_color = "#10b981" if enabled else "#ef4444"
    status_text = "ACTIVE" if enabled else "DISABLED"

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
    min-height: 300px;
  }}
  .card {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(10px);
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
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    background: rgba({status_color.lstrip('#')}, 0.15);
    color: {status_color};
    border: 1px solid {status_color};
  }}
  .status-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {status_color};
    animation: {('pulse 2s infinite' if enabled else 'none')};
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}
  h1 {{ font-size: 18px; font-weight: 600; margin-bottom: 4px; }}
  .subtitle {{ font-size: 12px; color: #94a3b8; }}
  .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 24px; }}
  .stat {{ background: rgba(15, 23, 42, 0.5); border-radius: 8px; padding: 16px; }}
  .stat-label {{ font-size: 10px; text-transform: uppercase; color: #94a3b8; margin-bottom: 6px; letter-spacing: 0.05em; }}
  .stat-value {{ font-size: 24px; font-weight: 700; font-variant-numeric: tabular-nums; }}
  .stat-value.green {{ color: #34d399; }}
  .stat-value.blue {{ color: #60a5fa; }}
  .stat-value.purple {{ color: #a78bfa; }}
  .stat-value.orange {{ color: #fbbf24; }}
  .controls {{ margin-top: 24px; display: flex; gap: 10px; }}
  .btn {{
    flex: 1;
    padding: 10px 16px;
    border: 1px solid #475569;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.5);
    color: #f8fafc;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .btn:hover {{ border-color: #64748b; background: rgba(30, 41, 59, 0.8); }}
  .btn.primary {{ background: {status_color}; border-color: {status_color}; }}
  .btn.primary:hover {{ opacity: 0.9; }}
  .footer {{ margin-top: 20px; font-size: 10px; color: #64748b; text-align: center; }}
</style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="status-badge">
        <div class="status-dot"></div>
        {status_text}
      </div>
      <h1>Tokenomics</h1>
    </div>
    <p class="subtitle">Caveman prose compression + Ponytail code minimization + token savings tracking</p>
    <div class="stats">
      <div class="stat">
        <div class="stat-label">Tokens Saved (Session)</div>
        <div class="stat-value green">{saved_tokens}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Chars Compressed</div>
        <div class="stat-value blue">{saved_chars}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Turns Processed</div>
        <div class="stat-value purple">{turns}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Subagents</div>
        <div class="stat-value orange">{subagents}</div>
      </div>
    </div>
    <div class="controls">
      <button class="btn {'primary' if not enabled else ''}" onclick="window.hermes.send('tokenomics.{'enable' if not enabled else 'disable'}')">
        {'Enable' if not enabled else 'Disable'}
      </button>
      <button class="btn" onclick="location.reload()">Refresh</button>
    </div>
    <div class="footer">
      Tokenomics v0.2.0 • Merged Caveman + Ponytail • Hermes Plugin
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
