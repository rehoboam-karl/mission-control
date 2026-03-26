"""API Router - JSON endpoints for HTMX"""

import json
import subprocess
from datetime import datetime
from fastapi import APIRouter, Request
from services.agent_status import get_agents_status
from services.event_parser import get_recent_events
from services.cron_costs import get_cron_stats
from services.todoist_sync import get_today_tasks
from services.alerts import get_alerts
from services.polymarket_metrics import get_polymarket_metrics
from pathlib import Path

router = APIRouter()

OPENCLAW_HOME = Path.home() / ".openclaw"
CONFIG_PATH = OPENCLAW_HOME / "openclaw.json"

@router.get("/api/agents")
async def api_agents():
    """JSON endpoint for agent status"""
    return {"agents": get_agents_status()}

@router.get("/api/events")
async def api_events(hours: int = 24):
    """JSON endpoint for events"""
    return {"events": get_recent_events(hours=hours)}

@router.get("/api/cron")
async def api_cron():
    """JSON endpoint for cron stats"""
    return get_cron_stats()

@router.get("/api/tasks")
async def api_tasks():
    """JSON endpoint for tasks"""
    return {"tasks": get_today_tasks()}

@router.get("/api/alerts")
async def api_alerts():
    """JSON endpoint for alerts"""
    return get_alerts()

@router.get("/api/health")
async def api_health():
    """Health check endpoint"""
    return {"status": "ok", "service": "mission-control-v4"}

@router.get("/api/ping")
async def api_ping():
    """Simple ping endpoint"""
    return {"pong": True}

@router.get("/api/polymarket")
async def api_polymarket():
    """JSON endpoint for Polymarket bot metrics"""
    return get_polymarket_metrics()


# ================== Agent Actions ==================

@router.post("/api/agents/{agent_id}/message")
async def send_agent_message(agent_id: str, request: Request):
    """Send message to an agent"""
    try:
        body = await request.json()
        message = body.get("message", "")
        
        if not message:
            return {"success": False, "error": "Message is required"}
        
        # Use sessions_send via subprocess
        result = subprocess.run(
            ["openclaw", "sessions", "send", "-s", agent_id, message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {"success": True}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/api/agents/{agent_id}/logs")
async def get_agent_logs(agent_id: str, limit: int = 50):
    """Get logs for an agent"""
    try:
        agent_dir = OPENCLAW_HOME / "agents" / agent_id / "sessions"
        if not agent_dir.exists():
            return {"logs": [], "error": "No sessions directory"}
        
        logs = []
        session_files = sorted(agent_dir.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        
        for session_file in session_files:
            with open(session_file, 'r') as f:
                lines = f.readlines()[-limit:]
                for line in lines:
                    try:
                        entry = json.loads(line)
                        log_entry = {
                            "timestamp": entry.get("timestamp", ""),
                            "type": entry.get("customType") or entry.get("role", "unknown"),
                        }
                        if "content" in entry:
                            content = entry.get("content", "")
                            if isinstance(content, str):
                                log_entry["content"] = content[:200] + "..." if len(content) > 200 else content
                        logs.append(log_entry)
                    except:
                        continue
        
        return {"logs": logs, "agent_id": agent_id, "count": len(logs)}
    except Exception as e:
        return {"logs": [], "error": str(e)}


@router.get("/api/agents/{agent_id}/workspace")
async def get_agent_workspace(agent_id: str):
    """List files in agent workspace"""
    try:
        # Get workspace from config
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        
        agents = config.get("agents", {}).get("list", [])
        workspace = ""
        for a in agents:
            if a.get("id") == agent_id:
                workspace = a.get("workspace", "")
                break
        
        if not workspace:
            return {"files": [], "error": "Workspace not found"}
        
        workspace = Path(workspace.replace("~", str(Path.home())))
        if not workspace.exists():
            return {"files": [], "error": "Workspace directory not found"}
        
        files = []
        for f in workspace.iterdir():
            if f.name.startswith('.'):
                continue
            stat = f.stat()
            files.append({
                "name": f.name,
                "type": "dir" if f.is_dir() else "file",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        files.sort(key=lambda x: (x["type"] == "file", x["name"]))
        
        return {"workspace": str(workspace), "files": files, "agent_id": agent_id}
    except Exception as e:
        return {"files": [], "error": str(e)}
