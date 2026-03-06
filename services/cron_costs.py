"""Cron Costs Service - Calculate costs per cron job"""

import json
from pathlib import Path
from datetime import datetime
from config import OPENCLAW_CRON

def load_cron_config() -> dict:
    """Load cron configuration"""
    if OPENCLAW_CRON.exists():
        try:
            return json.loads(OPENCLAW_CRON.read_text())
        except:
            pass
    return {'jobs': []}

def get_cron_jobs() -> list:
    """Get all configured cron jobs"""
    config = load_cron_config()
    jobs = []
    
    for job in config.get('jobs', []):
        jobs.append({
            'name': job.get('name', 'unknown'),
            'schedule': job.get('schedule', {}),
            'enabled': job.get('enabled', True),
            'last_run': job.get('last_run'),
            'next_run': job.get('next_run'),
            'status': 'active' if job.get('enabled') else 'disabled'
        })
    
    return jobs

def calculate_job_cost(job_name: str, duration_ms: int = 0) -> float:
    """Calculate cost of a job execution"""
    # Model cost assumptions (per 1M tokens)
    COSTS = {
        'input': 0.15,   # $0.15 per 1M input
        'output': 0.60,  # $0.60 per 1M output
    }
    
    # Rough estimate: 1000 tokens per minute of work
    estimated_tokens = (duration_ms / 60000) * 1000
    cost = (estimated_tokens / 1_000_000) * (COSTS['input'] + COSTS['output'])
    
    return round(cost, 4)

def get_cron_stats() -> dict:
    """Get cron job statistics"""
    jobs = get_cron_jobs()
    
    return {
        'total_jobs': len(jobs),
        'active_jobs': len([j for j in jobs if j.get('status') == 'active']),
        'disabled_jobs': len([j for j in jobs if j.get('status') == 'disabled']),
        'jobs': jobs
    }
