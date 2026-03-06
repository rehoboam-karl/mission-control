"""Shared Context Service - Read/write shared context files"""

import json
from pathlib import Path
from config import OPENCLAW_SHARED, WORKSPACE_BASE

def get_shared_contexts() -> list:
    """Get all shared context files"""
    contexts = []
    
    shared_dir = OPENCLAW_SHARED
    if shared_dir.exists():
        for f in shared_dir.glob("*.md"):
            contexts.append({
                'name': f.stem,
                'path': str(f),
                'content': f.read_text()[:500]  # Preview
            })
        
        for f in shared_dir.glob("*.json"):
            contexts.append({
                'name': f.stem,
                'path': str(f),
                'content': f.read_text()[:500]
            })
    
    return contexts

def get_context_file(name: str) -> dict:
    """Get specific context file"""
    shared_dir = OPENCLAW_SHARED
    
    for ext in ['.md', '.json', '.txt']:
        path = shared_dir / f"{name}{ext}"
        if path.exists():
            return {
                'name': name,
                'path': str(path),
                'content': path.read_text(),
                'type': ext[1:]
            }
    
    return None

def write_context_file(name: str, content: str, ext: str = '.md') -> bool:
    """Write context file"""
    shared_dir = OPENCLAW_SHARED
    shared_dir.mkdir(exist_ok=True)
    
    path = shared_dir / f"{name}{ext}"
    try:
        path.write_text(content)
        return True
    except Exception as e:
        print(f"Error writing context file: {e}")
        return False

def get_memory_files() -> list:
    """Get memory files from workspace"""
    memory_dir = WORKSPACE_BASE / "memory"
    files = []
    
    if memory_dir.exists():
        for f in sorted(memory_dir.glob("*.md")):
            files.append({
                'name': f.stem,
                'path': str(f),
                'modified': f.stat().st_mtime
            })
    
    return files
