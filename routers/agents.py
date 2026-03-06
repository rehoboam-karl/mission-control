"""Agents Router - Agent status grid"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.agent_status import get_agents_status

router = APIRouter()

@router.get("/agents", response_class=HTMLResponse)
async def agents_page(request: Request):
    """Agent status page"""
    agents = get_agents_status()
    
    return request.app.state.jinja.get_template("agents.html").render(
        request=request,
        agents=agents,
        page_title="Agents - Mission Control"
    )

@router.get("/agents/partial", response_class=HTMLResponse)
async def agents_partial(request: Request):
    """HTMX partial for agent grid"""
    agents = get_agents_status()
    
    return request.app.state.jinja.get_template("partials/agent_grid.html").render(
        request=request,
        agents=agents
    )
