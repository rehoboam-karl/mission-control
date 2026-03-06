"""Event Parser Service - Parse cron JSONL logs into events."""

import json
from pathlib import Path
from datetime import datetime, timedelta

OPENCLAW_HOME = Path.home() / ".openclaw"

def get_recent_events(limit=50, hours=None):
    """Parse cron run logs into events."""
    events = []

    # Parse cron JSONL logs
    cron_dir = OPENCLAW_HOME / "cron"
    if cron_dir.exists():
        for jsonl_file in cron_dir.rglob("*.jsonl"):
            try:
                with open(jsonl_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            if entry.get("action") == "finished":
                                # Calculate ago
                                ts = entry.get("ts", 0)
                                if ts:
                                    try:
                                        dt = datetime.fromtimestamp(ts / 1000)
                                        now = datetime.now()
                                        minutes_ago = (now - dt).total_seconds() / 60
                                        if minutes_ago < 60:
                                            ago = f"{int(minutes_ago)}m ago"
                                        elif minutes_ago < 1440:
                                            ago = f"{int(minutes_ago/60)}h ago"
                                        else:
                                            ago = f"{int(minutes_ago/1440)}d ago"
                                    except:
                                        ago = "unknown"
                                else:
                                    ago = "unknown"
                                
                                events.append({
                                    "timestamp": ts,
                                    "type": "cron",
                                    "agent": entry.get("agentId", "main"),
                                    "name": entry.get("jobName", entry.get("jobId", "?")),
                                    "status": entry.get("status", "?"),
                                    "summary": entry.get("summary", "")[:100],
                                    "model": entry.get("model", "?"),
                                    "tokens": entry.get("usage", {}).get("total_tokens", 0),
                                    "duration_ms": entry.get("durationMs", 0),
                                    "icon": "✅" if entry.get("status") == "ok" else "❌",
                                    "ago": ago,
                                })
                        except json.JSONDecodeError:
                            pass
            except Exception:
                pass

    # Sort by timestamp descending
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Filter by hours if specified
    if hours:
        cutoff = datetime.now() - timedelta(hours=hours)
        events = [e for e in events if e.get("timestamp") and 
                  datetime.fromtimestamp(e["timestamp"] / 1000) > cutoff]
    
    return events[:limit]
