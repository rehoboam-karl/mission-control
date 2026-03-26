"""Polymarket Bot Router"""

import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.polymarket_metrics import get_polymarket_metrics, get_traces_html, get_bot_status

router = APIRouter()

def format_timestamp(ts, start=0, end=None):
    """Format timestamp for Jinja2 template"""
    if not ts:
        return ''
    if end:
        return ts[start:end] if len(ts) > end else ts[start:]
    return ts[start:] if len(ts) > start else ts

@router.get("/polymarket/partial")
async def polymarket_partial(request: Request):
    """HTMX partial for Polymarket metrics"""
    data = get_polymarket_metrics()
    template = request.app.state.jinja.get_template("partials/polymarket_metrics.html")
    return HTMLResponse(template.render(data=data, format_time=format_timestamp))

@router.get("/polymarket/traces")
async def polymarket_traces(request: Request):
    """HTMX partial for traces/logs"""
    html = get_traces_html()
    return HTMLResponse(html)

@router.get("/polymarket")
async def polymarket_page(request: Request):
    """Standalone Polymarket metrics page"""
    data = get_polymarket_metrics()
    data['status'] = get_bot_status()
    template = request.app.state.jinja.get_template("polymarket.html")
    return HTMLResponse(template.render(data=data, format_time=format_timestamp))
