"""Cron Costs Service - Get cron jobs from openclaw CLI"""

import json
import subprocess
from pathlib import Path

# Preços por milhão de tokens
MODEL_COSTS = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "MiniMax-M2.5": {"input": 15.0, "output": 60.0},
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
}

def get_cron_jobs():
    """Get cron jobs from openclaw CLI"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("jobs", [])
    except Exception as e:
        print(f"Error getting cron jobs: {e}")
    
    return []

def get_cron_with_stats():
    """Get cron jobs with execution stats from logs"""
    jobs = get_cron_jobs()
    
    # Get stats from event logs
    from services.event_parser import get_recent_events
    events = get_recent_events(limit=500)
    
    # Aggregate stats by job name/id
    job_stats = {}
    for e in events:
        name = e.get("name", "unknown")
        if name not in job_stats:
            job_stats[name] = {"runs": 0, "tokens": 0, "ok": 0, "error": 0}
        job_stats[name]["runs"] += 1
        job_stats[name]["tokens"] += e.get("tokens", 0)
        if e.get("status") == "ok":
            job_stats[name]["ok"] += 1
        else:
            job_stats[name]["error"] += 1
    
    # Enrich jobs with stats
    enriched_jobs = []
    for job in jobs:
        job_id = job.get("id", "")
        job_name = job.get("name", job_id[:8])
        agent = job.get("agentId", "main")
        
        # Find matching stats
        stats = job_stats.get(job_id, {})
        
        # Get model from payload
        model = "MiniMax-M2.5"
        payload = job.get("payload", {})
        if payload.get("model"):
            model = payload["model"].split("/")[-1]
        
        # Calculate cost
        tokens = stats.get("tokens", 0)
        if tokens == 0:
            tokens = 15000  # Estimate
        
        model_key = model
        costs = MODEL_COSTS.get(model_key, {"input": 15.0, "output": 60.0})
        cost = (tokens / 1_000_000) * (costs["input"] + costs["output"])
        
        enriched_jobs.append({
            "id": job_id,
            "name": job_name,
            "agent": agent,
            "model": model,
            "schedule": job.get("schedule", {}).get("expr", "?"),
            "enabled": job.get("enabled", True),
            "status": "active" if job.get("enabled") else "disabled",
            "runs": stats.get("runs", 0),
            "tokens": stats.get("tokens", 0),
            "ok": stats.get("ok", 0),
            "error": stats.get("error", 0),
            "monthly_cost": round(cost * 30, 2),
            "next_run": job.get("state", {}).get("nextRunAtMs"),
        })
    
    return enriched_jobs

def get_cron_stats():
    """Get cron job statistics"""
    jobs = get_cron_with_stats()
    
    return {
        "total_jobs": len(jobs),
        "active_jobs": len([j for j in jobs if j.get("status") == "active"]),
        "disabled_jobs": len([j for j in jobs if j.get("status") == "disabled"]),
        "total_monthly_cost": sum(j.get("monthly_cost", 0) for j in jobs),
        "jobs": jobs
    }
