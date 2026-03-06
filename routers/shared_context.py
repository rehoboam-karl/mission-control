"""Shared Context Router - Context editor"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from services.shared_context import get_context_file, write_context_file

router = APIRouter()

@router.get("/shared", response_class=HTMLResponse)
async def shared_page(request: Request):
    """Shared context page"""
    # Read key files
    files = {}
    
    from pathlib import Path
    SHARED_DIR = Path.home() / ".openclaw" / "shared" / "context"
    
    for f in ["THESIS.md", "FEEDBACK-LOG.md", "SIGNALS.md"]:
        path = SHARED_DIR / f
        if path.exists():
            files[f] = {
                "name": f,
                "content": path.read_text()[:500]
            }
    
    return request.app.state.jinja.get_template("shared.html").render(
        request=request,
        files=files,
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

@router.post("/api/shared/quick-feedback")
async def quick_feedback(feedback: str = Form(...)):
    """Quick feedback - append to FEEDBACK-LOG.md"""
    from datetime import datetime
    from pathlib import Path
    
    SHARED_DIR = Path.home() / ".openclaw" / "shared" / "context"
    path = SHARED_DIR / "FEEDBACK-LOG.md"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"\n- [{timestamp}] {feedback}\n"
    
    try:
        with open(path, "a") as f:
            f.write(entry)
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}
