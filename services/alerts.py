"""Alerts Service - Get overdue commitments, upcoming, and cooling relationships"""

import subprocess
import json
from pathlib import Path

OPENCLAW_HOME = Path.home() / ".openclaw"

def get_alerts():
    """Get alerts: overdue commitments, upcoming, and cooling relationships"""
    alerts = []
    
    # Try to read from relationships data if available
    relationships_db = OPENCLAW_HOME / "workspace" / "data" / "relationships.db"
    
    # Check for commitments file
    commitments_file = OPENCLAW_HOME / "shared" / "context" / "COMMITMENTS.md"
    if commitments_file.exists():
        content = commitments_file.read_text()
        lines = content.split('\n')
        for line in lines:
            if line.strip().startsWith('-') or line.strip().startsWith('*'):
                # Check for overdue items
                if 'overdue' in line.lower() or '[overdue]' in line.lower():
                    alerts.append({
                        "type": "overdue",
                        "icon": "🚨",
                        "text": line.strip()[2:80],
                        "priority": "high"
                    })
                # Check for upcoming (next 48h)
                elif 'soon' in line.lower() or '[soon]' in line.lower():
                    alerts.append({
                        "type": "upcoming",
                        "icon": "⏰",
                        "text": line.strip()[2:80],
                        "priority": "medium"
                    })
    
    # Check for relationship cooling (contacts not contacted in 21+ days)
    # This would require a more complex relationship DB - using placeholder for now
    cooling_file = OPENCLAW_HOME / "shared" / "context" / "RELATIONSHIPS.md"
    if cooling_file.exists():
        content = cooling_file.read_text()
        # Count lines with "cooling" or "cold" status
        if "cooling" in content.lower() or "cold" in content.lower():
            alerts.append({
                "type": "cooling",
                "icon": "🥶",
                "text": "Relationships in cooling period",
                "priority": "low"
            })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    return {
        "alerts": alerts,
        "overdue": len([a for a in alerts if a["priority"] == "high"]),
        "upcoming": len([a for a in alerts if a["priority"] == "medium"]),
        "cooling": len([a for a in alerts if a["priority"] == "low"])
    }
