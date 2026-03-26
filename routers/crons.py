"""Crons Router - Cron dashboard"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.cron_costs import get_cron_stats

router = APIRouter()

@router.get("/crons", response_class=HTMLResponse)
async def crons_page(request: Request):
    """Cron management page"""
    stats = get_cron_stats()
    
    return request.app.state.jinja.get_template("crons.html").render(
        request=request,
        cron_stats=stats,
        page_title="Cron Jobs - Mission Control"
    )

@router.get("/crons/partial", response_class=HTMLResponse)
async def crons_partial(request: Request):
    """HTMX partial for cron table"""
    stats = get_cron_stats()
    
    return request.app.state.jinja.get_template("partials/cron_table.html").render(
        request=request,
        cron_stats=stats
    )

@router.get("/api/crons")
async def crons_api():
    """JSON endpoint for cron data."""
    from services.cron_costs import get_cron_data
    try:
        crons = get_cron_data()
        return {"crons": crons}
    except Exception as e:
        return {"crons": [], "error": str(e)}
