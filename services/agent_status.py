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
            try:
                content = identity_path.read_text()
                for line in content.splitlines():
                    if "Emoji:" in line:
                        # Extract emoji after "Emoji:" - handle markdown like **Emoji:** 💻
                        emoji_part = line.split("Emoji:")[-1]
                        # Remove markdown bold markers (**) and get the first character/emoji
                        emoji = emoji_part.replace("**", "").strip()
                        # Get just the first character (the emoji)
                        if emoji:
                            emoji = emoji[0]
                        else:
                            emoji = "🤖"
                        break
            except:
                pass

        # Determine status from session timestamps
        sessions_path = OPENCLAW_HOME / "agents" / agent_id / "sessions" / "sessions.json"
        last_active = None
        session_count = 0
        
        if sessions_path.exists():
            try:
                sessions_data = json.loads(sessions_path.read_text())
                
                # sessions.json is a dict, not a list
                if isinstance(sessions_data, dict):
                    session_count = len(sessions_data)
                    # Find most recent activity
                    for session_key, session_info in sessions_data.items():
                        # Try various timestamp fields
                        for ts_field in ["updatedAt", "lastActivityAt", "createdAt"]:
                            ts = session_info.get(ts_field)
                            if ts:
                                try:
                                    # Handle milliseconds timestamp
                                    if isinstance(ts, (int, float)) and ts > 1e12:
                                        ts = ts / 1000
                                    dt = datetime.fromtimestamp(ts)
                                    if last_active is None or dt > last_active:
                                        last_active = dt
                                except:
                                    pass
            except Exception as e:
                print(f"Error reading sessions for {agent_id}: {e}")

        # Check WORKING.md for active task
        working_path = Path(workspace) / "WORKING.md"
        has_active_task = working_path.exists() and working_path.stat().st_size > 50

        # Calculate status
        now = datetime.now()
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
