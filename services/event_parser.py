"""Event Parser Service - Parse JSONL cron logs + gateway logs"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from config import OPENCLAW_HOME

def get_gateway_log_path() -> Path:
    """Get gateway log path"""
    return OPENCLAW_HOME / "logs" / "gateway.log"

def get_cron_log_path() -> Path:
    """Get cron log path"""
    return OPENCLAW_HOME / "logs" / "cron.log"

def parse_gateway_logs(limit: int = 100) -> list:
    """Parse gateway logs for events"""
    events = []
    log_path = get_gateway_log_path()
    
    if not log_path.exists():
        return events
    
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        for line in reversed(lines[-limit:]):
            try:
                data = json.loads(line)
                events.append({
                    'timestamp': data.get('timestamp', ''),
                    'type': data.get('type', 'log'),
                    'message': data.get('message', ''),
                    'level': data.get('level', 'info')
                })
            except json.JSONDecodeError:
                # Plain text log line
                if line.strip():
                    events.append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'log',
                        'message': line.strip(),
                        'level': 'info'
                    })
    except Exception as e:
        events.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'message': f'Failed to read logs: {e}',
            'level': 'error'
        })
    
    return events

def parse_cron_events(limit: int = 50) -> list:
    """Parse cron execution events"""
    events = []
    log_path = get_cron_log_path()
    
    if not log_path.exists():
        return events
    
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()
        
        for line in reversed(lines[-limit:]):
            try:
                data = json.loads(line)
                events.append({
                    'timestamp': data.get('timestamp', ''),
                    'job': data.get('job', 'unknown'),
                    'status': data.get('status', 'unknown'),
                    'duration': data.get('duration', 0),
                    'error': data.get('error', '')
                })
            except:
                pass
    
    except Exception as e:
        pass
    
    return events

def get_recent_events(hours: int = 24, event_type: str = None) -> list:
    """Get recent events from all sources"""
    all_events = []
    
    # Gateway logs
    all_events.extend(parse_gateway_logs(limit=200))
    
    # Cron logs
    cron_events = parse_cron_events(limit=100)
    for e in cron_events:
        e['source'] = 'cron'
        all_events.append(e)
    
    # Filter by type if specified
    if event_type:
        all_events = [e for e in all_events if e.get('type') == event_type]
    
    # Sort by timestamp descending
    all_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Limit to hours
    cutoff = datetime.now() - timedelta(hours=hours)
    filtered = []
    for e in all_events:
        ts = e.get('timestamp', '')
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if dt.replace(tzinfo=None) > cutoff:
                    filtered.append(e)
            except:
                filtered.append(e)
    
    return filtered[:100]
