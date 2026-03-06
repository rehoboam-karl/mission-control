"""Relationships Service - Read relationships.db"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

RELATIONSHIPS_DB = Path.home() / ".openclaw" / "workspace" / "data" / "relationships.db"

def get_people():
    """Get all people from relationships database"""
    people = []
    
    if not RELATIONSHIPS_DB.exists():
        return people
    
    try:
        conn = sqlite3.connect(RELATIONSHIPS_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, company, role, group_tag, last_contact, health_score
            FROM people
            ORDER BY name
        """)
        
        for row in cursor.fetchall():
            last_contact = row['last_contact']
            days_ago = None
            if last_contact:
                try:
                    dt = datetime.strptime(last_contact, '%Y-%m-%d')
                    days_ago = (datetime.now() - dt).days
                except:
                    pass
            
            people.append({
                'id': row['id'],
                'name': row['name'],
                'company': row['company'],
                'role': row['role'],
                'group': row['group_tag'],
                'last_contact': last_contact,
                'days_ago': days_ago,
                'health': row['health_score'],
            })
        
        conn.close()
    except Exception as e:
        print(f"Error reading relationships: {e}")
    
    return people

def get_relationships():
    """Get relationships data for graph visualization"""
    people = get_people()
    
    # Build nodes and links for graph
    nodes = []
    links = []
    
    # Group by group_tag
    groups = {}
    for p in people:
        group = p.get('group') or 'Ungrouped'
        if group not in groups:
            groups[group] = []
        groups[group].append(p)
    
    # Create nodes
    for p in people:
        days = p.get('days_ago')
        if days is None:
            color = '#6b7280'  # gray - unknown
        elif days < 14:
            color = '#22c55e'  # green - healthy
        elif days < 30:
            color = '#f59e0b'  # yellow - warming
        elif days < 60:
            color = '#ef4444'  # red - cold
        else:
            color = '#7f1d1d'  # dark red - very cold
        
        nodes.append({
            'id': p['id'],
            'name': p['name'],
            'company': p['company'],
            'group': p['group'],
            'days_ago': days,
            'color': color
        })
    
    return {
        'nodes': nodes,
        'groups': groups,
        'stats': {
            'total': len(people),
            'healthy': len([p for p in people if p.get('days_ago', 999) < 14]),
            'warming': len([p for p in people if 14 <= p.get('days_ago', 999) < 30]),
            'cold': len([p for p in people if p.get('days_ago', 999) >= 30]),
        }
    }
