"""Shared Context Router - Context editor"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from services.shared_context import get_shared_contexts, get_context_file, write_context_file

router = APIRouter()

@router.get("/shared", response_class=HTMLResponse)
async def shared_page(request: Request):
    """Shared context page"""
    contexts = get_shared_contexts()
    
    return request.app.state.jinja.get_template("shared.html").render(
        request=request,
        contexts=contexts,
        page_title="Shared Context - Mission Control"
    )

@router.get("/shared/{name}", response_class=HTMLResponse)
async def shared_edit(request: Request, name: str):
    """Edit specific context"""
    context = get_context_file(name)
    
    return request.app.state.jinja.get_template("partials/context_editor.html").render(
        request=request,
        context=context
    )

@router.post("/shared/{name}")
async def shared_save(name: str, content: str = Form(...), ext: str = Form('.md')):
    """Save context file"""
    success = write_context_file(name, content, ext)
    
    if success:
        return RedirectResponse(url="/shared", status_code=303)
    return {"error": "Failed to save"}
