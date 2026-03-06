#!/usr/bin/env python3
"""
Get scheduled cron jobs from OpenClaw.
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytz

def parse_cron_schedule(schedule):
    """Parse OpenClaw cron schedule to get next run times."""
    kind = schedule.get('kind')
    
    if kind == 'at':
        # One-shot at specific time
        at_time = schedule.get('at')
        if at_time:
            return [datetime.fromisoformat(at_time.replace('Z', '+00:00'))]
    
    elif kind == 'every':
        # Recurring interval
        every_ms = schedule.get('everyMs')
        anchor_ms = schedule.get('anchorMs', datetime.now().timestamp() * 1000)
        
        if every_ms:
            # Calculate next 7 occurrences
            now = datetime.now(pytz.timezone('America/Sao_Paulo'))
            anchor = datetime.fromtimestamp(anchor_ms / 1000, tz=pytz.timezone('America/Sao_Paulo'))
            interval = timedelta(milliseconds=every_ms)
            
            next_runs = []
            current = anchor
            while current < now:
                current += interval
            
            for i in range(7):
                next_runs.append(current)
                current += interval
            
            return next_runs
    
    elif kind == 'cron':
        # Cron expression - would need croniter library
        # For now, return empty
        pass
    
    return []

def get_cron_jobs():
    """Read OpenClaw cron jobs."""
    cron_store = Path.home() / '.openclaw' / 'cron-jobs.json'
    
    if not cron_store.exists():
        return []
    
    try:
        with open(cron_store, 'r') as f:
            data = json.load(f)
            jobs = data.get('jobs', [])
            
            result = []
            for job in jobs:
                if not job.get('enabled', True):
                    continue
                
                schedule = job.get('schedule', {})
                next_runs = parse_cron_schedule(schedule)
                
                result.append({
                    'id': job.get('id'),
                    'name': job.get('name', 'Unnamed Job'),
                    'schedule': schedule,
                    'next_runs': [dt.isoformat() for dt in next_runs],
                    'payload': job.get('payload', {})
                })
            
            return result
    
    except Exception as e:
        print(f"Error reading cron jobs: {e}", file=sys.stderr)
        return []

def format_for_calendar(jobs):
    """Format cron jobs for weekly calendar view."""
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    
    # Get next Sunday as start of week
    days_until_sunday = (6 - now.weekday()) % 7
    if days_until_sunday == 0 and now.weekday() != 6:
        days_until_sunday = 7
    week_start = (now + timedelta(days=days_until_sunday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    
    # Filter jobs for this week
    calendar_events = []
    for job in jobs:
        for run_time_str in job.get('next_runs', []):
            run_time = datetime.fromisoformat(run_time_str)
            if run_time.tzinfo is None:
                run_time = tz.localize(run_time)
            
            if week_start <= run_time < week_end:
                # Only include events during work hours (9-18h)
                if 9 <= run_time.hour < 18:
                    calendar_events.append({
                        'id': job['id'],
                        'title': job['name'],
                        'start': run_time.isoformat(),
                        'day': run_time.strftime('%A'),
                        'time': run_time.strftime('%H:%M'),
                        'payload': job['payload']
                    })
    
    return {
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'events': sorted(calendar_events, key=lambda x: x['start'])
    }

def main():
    jobs = get_cron_jobs()
    calendar = format_for_calendar(jobs)
    print(json.dumps(calendar, indent=2))

if __name__ == '__main__':
    main()
