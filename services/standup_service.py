"""Standup Service - Aggregate standup data across all agents"""

from datetime import date, timedelta
from pathlib import Path
from services.event_parser import get_recent_events

OPENCLAW_HOME = Path.home() / ".openclaw"

def get_standup_data():
    """Aggregate standup data across all agents."""
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    events = get_recent_events(limit=500)
    
    # Split by day
    def ts_to_date(ts_ms):
        from datetime import datetime
        return datetime.fromtimestamp(ts_ms / 1000).date().isoformat()
    
    today_events = [e for e in events if ts_to_date(e["timestamp"]) == today]
    yesterday_events = [e for e in events if ts_to_date(e["timestamp"]) == yesterday]
    
    # Aggregate by agent
    def aggregate_by_agent(event_list):
        agents = {}
        for e in event_list:
            aid = e.get("agent", "unknown")
            if aid not in agents:
                agents[aid] = {"ok": 0, "error": 0, "tokens": 0, "events": []}
            status = e.get("status", "ok")
            agents[aid][status] = agents[aid].get(status, 0) + 1
            agents[aid]["tokens"] += e.get("tokens", 0)
            agents[aid]["events"].append(e)
        return agents
    
    agents_today = aggregate_by_agent(today_events)
    agents_yesterday = aggregate_by_agent(yesterday_events)
    
    # 7-day trend
    trend = []
    for i in range(7):
        d = (date.today() - timedelta(days=6-i)).isoformat()
        day_events = [e for e in events if ts_to_date(e["timestamp"]) == d]
        trend.append({
            "date": d,
            "total": len(day_events),
            "ok": len([e for e in day_events if e.get("status") == "ok"]),
            "error": len([e for e in day_events if e.get("status") != "ok"]),
        })
    
    return {
        "today": agents_today,
        "yesterday": agents_yesterday,
        "trend": trend,
        "today_total": len(today_events),
        "yesterday_total": len(yesterday_events),
    }
