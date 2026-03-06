"""Mission Control v4 - Main Entry Point"""

import os
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from db import init_db
from routers import dashboard, agents, events, crons, standup, shared_context, api

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    # Startup
    await init_db()
    print("✅ Mission Control v4 started")
    yield
    # Shutdown
    print("👋 Mission Control v4 stopped")

# Create FastAPI app
app = FastAPI(
    title="Mission Control v4",
    description="Dashboard for OpenClaw agent management",
    version="4.0.0",
    lifespan=lifespan
)

# Setup templates
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates"),
    auto_reload=True
)
app.state.jinja = templates

# Mount static files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(dashboard.router)
app.include_router(agents.router)
app.include_router(events.router)
app.include_router(crons.router)
app.include_router(standup.router)
app.include_router(shared_context.router)
app.include_router(api.router)

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
