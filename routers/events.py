"""Events Router - Live event feed"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from services.event_parser import get_recent_events

router = APIRouter()

@router.get("/events", response_class=HTMLResponse)
async def events_page(request: Request, hours: int = Query(24)):
    """Events page with filters"""
    events = get_recent_events(hours=hours)
    
    return request.app.state.jinja.get_template("events.html").render(
        request=request,
        events=events,
        hours=hours,
        page_title="Events - Mission Control"
    )

@router.get("/events/partial", response_class=HTMLResponse)
async def events_partial(request: Request, hours: int = Query(24)):
    """HTMX partial for event feed"""
    events = get_recent_events(hours=hours)[:20]
    
    return request.app.state.jinja.get_template("partials/event_feed.html").render(
        request=request,
        events=events
    )
