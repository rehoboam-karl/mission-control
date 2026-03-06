"""Outbox Service - Read shared outbox files"""

from pathlib import Path

OPENCLAW_HOME = Path.home() / ".openclaw"

def get_outbox_items():
    """Get items from outbox directory"""
    outbox_dir = OPENCLAW_HOME / "shared" / "outbox"
    items = []
    
    if outbox_dir.exists():
        for f in sorted(outbox_dir.rglob("*"), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file() and not f.name.startswith('.'):
                items.append({
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                    "type": f.suffix[1:] if f.suffix else "txt"
                })
    
    return items[:50]  # Limit to 50 most recent

def read_outbox_file(path: str) -> str:
    """Read content of an outbox file"""
    try:
        return Path(path).read_text()
    except:
        return ""
