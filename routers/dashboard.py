"""Dashboard Router - Main dashboard"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.agent_status import get_agents_status
from services.event_parser import get_recent_events
from services.cron_costs import get_cron_stats
from services.todoist_sync import get_today_tasks

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    agents = get_agents_status()
    events = get_recent_events(hours=24)
    cron_stats = get_cron_stats()
    tasks = get_today_tasks()
    
    # Count statuses
    active_agents = len([a for a in agents if a.get('status') == 'active'])
    
    return request.app.state.jinja.get_template("dashboard.html").render(
        request=request,
        agents=agents,
        active_agents=active_agents,
        events=events[:20],
        cron_stats=cron_stats,
        tasks=tasks,
        agent_count=len(agents),
        cron_count=cron_stats.get('total_jobs', 0),
        page_title="Mission Control — Rehoboam"
    )
