#!/usr/bin/env python3
"""
Get activity feed from OpenClaw session history and file changes.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess

def get_session_activities(sessions_dir):
    """Read OpenClaw session transcripts and extract activities."""
    activities = []
    
    sessions_path = Path(sessions_dir)
    if not sessions_path.exists():
        return activities
    
    for session_file in sessions_path.glob("**/*.jsonl"):
        try:
            with open(session_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    
                    # Extract relevant activity
                    timestamp = entry.get('ts')
                    role = entry.get('role')
                    
                    if role == 'assistant':
                        # Check for tool calls
                        content = entry.get('content', [])
                        for item in content:
                            if item.get('type') == 'tool_use':
                                activities.append({
                                    'timestamp': timestamp,
                                    'type': 'tool_call',
                                    'action': item.get('name'),
                                    'details': item.get('input', {}),
                                    'session': session_file.stem
                                })
        except Exception as e:
            print(f"Error reading {session_file}: {e}", file=sys.stderr)
            continue
    
    return activities

def get_file_changes(workspace_dir, days=7):
    """Get recent file changes from git if available."""
    changes = []
    
    try:
        # Check if we're in a git repo
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return changes
        
        # Get git log for last N days
        since = f"{days}.days.ago"
        result = subprocess.run(
            ['git', 'log', '--since', since, '--name-status', '--pretty=format:%ct|%s'],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            current_commit = None
            
            for line in lines:
                if '|' in line:
                    # Commit line
                    timestamp, message = line.split('|', 1)
                    current_commit = {
                        'timestamp': int(timestamp),
                        'message': message,
                        'files': []
                    }
                elif line.strip() and current_commit:
                    # File change line
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status, filepath = parts[0], parts[1]
                        current_commit['files'].append({
                            'status': status,
                            'path': filepath
                        })
                elif not line.strip() and current_commit:
                    # End of commit
                    changes.append({
                        'timestamp': current_commit['timestamp'],
                        'type': 'file_change',
                        'action': 'git_commit',
                        'details': current_commit
                    })
                    current_commit = None
            
            # Add last commit if exists
            if current_commit:
                changes.append({
                    'timestamp': current_commit['timestamp'],
                    'type': 'file_change',
                    'action': 'git_commit',
                    'details': current_commit
                })
                
    except Exception as e:
        print(f"Error getting git changes: {e}", file=sys.stderr)
    
    return changes

def group_by_day(activities):
    """Group activities by day."""
    grouped = defaultdict(list)
    
    for activity in activities:
        timestamp = activity.get('timestamp')
        if timestamp:
            # Convert timestamp to date
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.fromtimestamp(timestamp / 1000 if timestamp > 10000000000 else timestamp)
            
            date_key = dt.strftime('%Y-%m-%d')
            grouped[date_key].append({
                **activity,
                'formatted_time': dt.strftime('%H:%M:%S')
            })
    
    # Sort by date descending
    return dict(sorted(grouped.items(), reverse=True))

def main():
    # Paths
    openclaw_dir = Path.home() / '.openclaw'
    sessions_dir = openclaw_dir / 'sessions'
    workspace_dir = openclaw_dir / 'workspace'
    
    # Get activities
    print("Collecting activities...", file=sys.stderr)
    session_activities = get_session_activities(sessions_dir)
    file_changes = get_file_changes(workspace_dir)
    
    # Combine and sort
    all_activities = session_activities + file_changes
    all_activities.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # Group by day
    grouped = group_by_day(all_activities)
    
    # Output JSON
    print(json.dumps(grouped, indent=2))

if __name__ == '__main__':
    main()
