"""Outbox Router - View outbox files"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.outbox import get_outbox_items, read_outbox_file

router = APIRouter()

@router.get("/outbox", response_class=HTMLResponse)
async def outbox_page(request: Request):
    """Outbox viewer page"""
    items = get_outbox_items()
    
    return request.app.state.jinja.get_template("outbox.html").render(
        request=request,
        items=items,
        page_title="Outbox - Mission Control"
    )

@router.get("/outbox/partial", response_class=HTMLResponse)
async def outbox_partial(request: Request):
    """HTMX partial for outbox"""
    items = get_outbox_items()
    
    return request.app.state.jinja.get_template("partials/outbox.html").render(
        request=request,
        items=items
    )

@router.get("/api/outbox/{filename}")
async def api_outbox_file(filename: str):
    """API endpoint to read outbox file"""
    items = get_outbox_items()
    for item in items:
        if item["name"] == filename:
            content = read_outbox_file(item["path"])
            return {"name": filename, "content": content}
    return {"error": "File not found"}
