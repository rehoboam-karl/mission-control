"""Relationships Router - Relationship graph"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from services.relationships import get_relationships

router = APIRouter()

@router.get("/relationships", response_class=HTMLResponse)
async def relationships_page(request: Request):
    """Relationship graph page"""
    data = get_relationships()
    
    return request.app.state.jinja.get_template("relationships.html").render(
        request=request,
        relationships=data,
        page_title="Relationships - Mission Control"
    )
