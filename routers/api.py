"""API Router - JSON endpoints for HTMX"""

from fastapi import APIRouter
from services.agent_status import get_all_agent_status
from services.event_parser import get_recent_events
from services.cron_costs import get_cron_stats

router = APIRouter()

@router.get("/api/agents")
async def api_agents():
    """JSON endpoint for agent status"""
    return {"agents": get_all_agent_status()}

@router.get("/api/events")
async def api_events(hours: int = 24):
    """JSON endpoint for events"""
    return {"events": get_recent_events(hours=hours)}

@router.get("/api/cron")
async def api_cron():
    """JSON endpoint for cron stats"""
    return get_cron_stats()

@router.get("/api/health")
async def api_health():
    """Health check endpoint"""
    return {"status": "ok", "service": "mission-control-v4"}
