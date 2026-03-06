"""Mission Control v4 - Configuration"""

from pathlib import Path

# Base paths
HOME = Path.home()
OPENCLAW_HOME = HOME / ".openclaw"
WORKSPACE_BASE = HOME / ".openclaw" / "workspace-karl-dev"

# Data paths
OPENCLAW_SESSIONS = OPENCLAW_HOME / "sessions"
OPENCLAW_CRON = OPENCLAW_HOME / "cron-jobs.json"
OPENCLAW_MEMORY = WORKSPACE_BASE / "memory"
OPENCLAW_SHARED = OPENCLAW_HOME / "shared"

# Mission Control paths
MC_DATA = Path(__file__).parent / "data"
MC_DB = MC_DATA / "mission_control.db"
MC_TEMPLATES = Path(__file__).parent / "templates"
MC_STATIC = Path(__file__).parent / "static"

# Ensure data dir exists
MC_DATA.mkdir(exist_ok=True)

# Agent configuration
AGENT_WORKSPACE = WORKSPACE_BASE
AGENT_MEMORY = WORKSPACE_BASE / "memory"

# Polling intervals (seconds)
POLL_INTERVAL_EVENTS = 10
POLL_INTERVAL_AGENTS = 30
POLL_INTERVAL_TASKS = 60
