"""Dashboard Router - Main dashboard"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.agent_status import get_all_agent_status
from services.event_parser import get_recent_events
from services.cron_costs import get_cron_stats

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    agents = get_all_agent_status()
    events = get_recent_events(hours=24)
    cron_stats = get_cron_stats()
    
    return request.app.state.jinja.get_template("dashboard.html").render(
        request=request,
        agents=agents,
        events=events[:20],
        cron_stats=cron_stats,
        page_title="Mission Control v4"
    )
