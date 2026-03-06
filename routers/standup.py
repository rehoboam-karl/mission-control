"""Standup Router - Daily standup view"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.agent_status import get_all_agent_status
from services.event_parser import get_recent_events
from datetime import datetime

router = APIRouter()

@router.get("/standup", response_class=HTMLResponse)
async def standup_page(request: Request):
    """Daily standup view"""
    agents = get_all_agent_status()
    today_events = get_recent_events(hours=24)
    
    # Group events by type
    event_summary = {
        'total': len(today_events),
        'errors': len([e for e in today_events if e.get('level') == 'error']),
        'warnings': len([e for e in today_events if e.get('level') == 'warning']),
    }
    
    return request.app.state.jinja.get_template("standup.html").render(
        request=request,
        agents=agents,
        event_summary=event_summary,
        today_date=datetime.now().strftime("%Y-%m-%d"),
        page_title="Daily Standup - Mission Control"
    )
