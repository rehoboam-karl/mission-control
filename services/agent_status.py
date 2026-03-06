"""Agent Status Service - Read agent list + session data → status per agent."""

import json
from datetime import datetime
from pathlib import Path

OPENCLAW_HOME = Path.home() / ".openclaw"
CONFIG_PATH = OPENCLAW_HOME / "openclaw.json"

def get_agents_status():
    """Read agent list + session data → status per agent."""
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    agents = config["agents"]["list"]
    results = []

    for agent in agents:
        agent_id = agent["id"]
        name = agent.get("name", agent_id)
        model = agent.get("model", config["agents"]["defaults"]["model"]["primary"])
        workspace = agent.get("workspace", "")

        # Read IDENTITY.md for emoji
        identity_path = Path(workspace) / "IDENTITY.md"
        emoji = "🤖"
        if identity_path.exists():
            for line in identity_path.read_text().splitlines():
                if "Emoji:" in line:
                    emoji = line.split("Emoji:")[-1].strip().split()[0]
                    break

        # Determine status from session timestamps
        sessions_path = OPENCLAW_HOME / "agents" / agent_id / "sessions" / "sessions.json"
        last_active = None
        session_count = 0
        if sessions_path.exists():
            try:
                sessions = json.loads(sessions_path.read_text())
                session_count = len(sessions) if isinstance(sessions, list) else 0
                # Find most recent activity
                for s in (sessions if isinstance(sessions, list) else []):
                    ts = s.get("lastActivityAt") or s.get("updatedAt") or s.get("createdAt")
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if last_active is None or dt > last_active:
                                last_active = dt
                        except:
                            pass
            except:
                pass

        # Check WORKING.md for active task
        working_path = Path(workspace) / "WORKING.md"
        has_active_task = working_path.exists() and working_path.stat().st_size > 50

        # Calculate status
        now = datetime.now(last_active.tzinfo if last_active and last_active.tzinfo else None)
        if last_active is None:
            status = "offline"
            status_color = "red"
            status_icon = "🔴"
            ago = "never"
        else:
            minutes_ago = (now - last_active).total_seconds() / 60
            if minutes_ago > 60:
                status = "offline"
                status_color = "red"
                status_icon = "🔴"
            elif has_active_task:
                status = "working"
                status_color = "blue"
                status_icon = "🔵"
            elif minutes_ago < 35:
                status = "online"
                status_color = "green"
                status_icon = "🟢"
            else:
                status = "idle"
                status_color = "yellow"
                status_icon = "🟡"

            if minutes_ago < 60:
                ago = f"{int(minutes_ago)}m ago"
            elif minutes_ago < 1440:
                ago = f"{int(minutes_ago/60)}h ago"
            else:
                ago = f"{int(minutes_ago/1440)}d ago"

        results.append({
            "id": agent_id,
            "name": name,
            "emoji": emoji,
            "model": model.split("/")[-1] if "/" in model else model,
            "status": status,
            "status_color": status_color,
            "status_icon": status_icon,
            "last_active": ago,
            "sessions": session_count,
            "has_active_task": has_active_task,
        })

    return results
