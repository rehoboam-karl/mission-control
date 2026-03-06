"""Tasks Router - Todoist integration"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    """Tasks page"""
    # TODO: Integrate with Todoist CLI
    tasks = []
    
    return request.app.state.jinja.get_template("tasks.html").render(
        request=request,
        tasks=tasks,
        page_title="Tasks - Mission Control"
    )

@router.get("/tasks/partial", response_class=HTMLResponse)
async def tasks_partial(request: Request):
    """HTMX partial for task list"""
    # TODO: Fetch from Todoist
    tasks = []
    
    return request.app.state.jinja.get_template("partials/task_list.html").render(
        request=request,
        tasks=tasks
    )
