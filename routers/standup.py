"""Standup Router - Daily standup view"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.standup_service import get_standup_data

router = APIRouter()

@router.get("/standup", response_class=HTMLResponse)
async def standup_page(request: Request):
    """Daily standup view"""
    standup = get_standup_data()
    
    return request.app.state.jinja.get_template("standup.html").render(
        request=request,
        standup=standup,
        page_title="Daily Standup - Mission Control"
    )

@router.get("/standup/partial", response_class=HTMLResponse)
async def standup_partial(request: Request):
    """HTMX partial for standup"""
    standup = get_standup_data()
    
    return request.app.state.jinja.get_template("partials/standup.html").render(
        request=request,
        standup=standup
    )
