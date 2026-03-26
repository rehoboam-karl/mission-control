"""Agent Status Service - Read agent list + session data → status per agent."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

OPENCLAW_HOME = Path.home() / ".openclaw"
CONFIG_PATH = OPENCLAW_HOME / "openclaw.json"


def _get_agent_tokens(agent_id: str) -> Tuple[int, int, float]:
    """Get total tokens and message count for an agent from session data"""
    agent_dir = OPENCLAW_HOME / "agents" / agent_id
    
    total_tokens = 0
    message_count = 0
    
    sessions_dir = agent_dir / "sessions"
    if sessions_dir.exists():
        try:
            all_sessions = [f for f in sessions_dir.glob("*.jsonl") if not f.name.endswith('.lock')]
            
            for session_file in all_sessions:
                with open(session_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            # Count messages
                            msg_type = entry.get('customType') or entry.get('role')
                            if msg_type in ['user', 'assistant', 'model-snapshot']:
                                message_count += 1
                            
                            # Try to get tokens from usage field
                            usage = entry.get('usage', {})
                            if usage:
                                total_tokens += usage.get('input_tokens', 0)
                                total_tokens += usage.get('output_tokens', 0)
                            
                            # Also check inside message object
                            msg_obj = entry.get('message', {})
                            if isinstance(msg_obj, dict):
                                content = msg_obj.get('content', '')
                                if isinstance(content, str):
                                    total_tokens += len(content) // 4
                                elif isinstance(content, list):
                                    text_parts = [p.get("text", "") for p in content if p.get("type") == "text"]
                                    total_tokens += sum(len(t) // 4 for t in text_parts)
                                    
                        except:
                            continue
            
        except Exception as e:
            print(f"Could not read tokens for {agent_id}: {e}")
    
    estimated_cost = (total_tokens / 1_000_000) * 0.03
    return total_tokens, message_count, round(estimated_cost, 4)

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
        
        # Get token usage
        tokens_used, message_count, estimated_cost = _get_agent_tokens(agent_id)
        
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
            "tokens_used": tokens_used,
            "message_count": message_count,
            "estimated_cost": estimated_cost,
            "workspace": workspace,
        })

    return results
