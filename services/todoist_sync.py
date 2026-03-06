"""Todoist Sync Service - Shell out to todoist CLI"""

import subprocess
import json

def get_today_tasks():
    """Get today's tasks from Todoist CLI"""
    tasks = []
    
    try:
        result = subprocess.run(
            ["todoist", "today"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Parse the output - format: ID [PROJECT] Task name (every X)
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("Usage"):
                    continue
                
                # Extract ID and content
                parts = line.split(None, 1)  # Split on first whitespace
                if len(parts) >= 2:
                    task_id = parts[0]
                    content = parts[1].strip()
                    
                    # Detect priority from content
                    priority = 1
                    if "[DEBITO]" in content:
                        priority = 4
                    elif "[CREDITO]" in content:
                        priority = 3
                    elif "[MENTAL]" in content:
                        priority = 2
                    
                    tasks.append({
                        "id": task_id,
                        "content": content,
                        "priority": priority,
                    })
                    
    except FileNotFoundError:
        # Todoist CLI not installed
        pass
    except Exception as e:
        print(f"Todoist error: {e}")
        pass
    
    return tasks

def get_tasks_by_project(project: str):
    """Get tasks by project"""
    tasks = []
    
    try:
        result = subprocess.run(
            ["todoist", "tasks", "--project", project],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                parts = line.split(None, 1)
                if len(parts) >= 2:
                    tasks.append({
                        "id": parts[0],
                        "content": parts[1],
                        "priority": 1,
                    })
    except:
        pass
    
    return tasks
