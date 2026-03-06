"""Agent Status Service - Parse heartbeat/session data"""

import json
import os
from pathlib import Path
from datetime import datetime
from config import OPENCLAW_SESSIONS, AGENT_WORKSPACE

def get_agent_workspaces() -> list:
    """Find all agent workspace directories"""
    workspaces = []
    
    # Look for AGENTS.md files in workspaces
    for item in Path(AGENT_WORKSPACE).iterdir():
        if item.is_file() and item.name == "AGENTS.md":
            workspaces.append(item.parent)
    
    return workspaces

def parse_agent_from_workspace(workspace_path: Path) -> dict:
    """Parse agent info from AGENTS.md"""
    agents = []
    
    # Try to read AGENTS.md
    agents_md = workspace_path / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text()
        
        # Simple parsing - extract agent names
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('-'):
                # Likely an agent entry
                parts = line.strip('-: ').split()
                if parts:
                    name = parts[0].replace('-', '_')
                    agents.append({
                        'name': name,
                        'workspace': str(workspace_path),
                        'status': 'active' if is_agent_active(workspace_path) else 'idle'
                    })
    
    return agents

def is_agent_active(workspace_path: Path) -> bool:
    """Check if agent has recent activity"""
    sessions_dir = OPENCLAW_SESSIONS
    
    if not sessions_dir.exists():
        return False
    
    # Check for recent session files
    try:
        files = list(sessions_dir.glob("*.jsonl"))
        if files:
            # Sort by modification time
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            recent = files[0]
            
            # Check if modified in last 5 minutes
            import time
            age = time.time() - recent.stat().st_mtime
            return age < 300
    except:
        pass
    
    return False

def get_all_agent_status() -> list:
    """Get status of all agents"""
    agents = []
    
    # Read from sessions directory
    sessions_dir = OPENCLAW_SESSIONS
    if sessions_dir.exists():
        for session_file in sessions_dir.glob("*.jsonl"):
            name = session_file.stem
            agents.append({
                'name': name,
                'session_file': str(session_file),
                'status': 'active',
                'last_seen': datetime.now().isoformat()
            })
    
    # Add known agents from workspace
    for ws in get_agent_workspaces():
        workspace_agents = parse_agent_from_workspace(ws)
        for wa in workspace_agents:
            if not any(a['name'] == wa['name'] for a in agents):
                agents.append(wa)
    
    return agents
