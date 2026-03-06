"""Cron Costs Service - Cost projections for cron jobs"""

import json
import subprocess
from pathlib import Path

# Preços por milhão de tokens
MODEL_COSTS = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "MiniMax-M2.5": {"input": 15.0, "output": 60.0},
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
}

# Frequências mensais aproximadas
FREQ_MONTHLY = {
    "0 * * * *": 720,
    "*/15 * * * *": 2880,
    "0 7 * * *": 30,
    "30 6 * * *": 30,
    "0 8 * * *": 30,
    "0 8 * * 1-5": 22,
    "0 9 * * 1,3,5": 13,
    "0 9 * * 2,4": 9,
    "0 9 * * 1": 4,
    "0 10 * * 0": 4,
    "0 12 * * 6": 4,
    "0 9 1-7 * 1": 1,
    "0 8 1 * *": 1,
}

def get_cron_costs():
    """Get cron list with cost projections."""
    # Get from event logs (more reliable)
    return get_cron_from_logs()

def get_cron_from_logs():
    """Get cron data from event logs"""
    from services.event_parser import get_recent_events
    
    events = get_recent_events(limit=200)
    jobs = {}
    
    for e in events:
        name = e.get("name", "unknown")
        if name not in jobs:
            jobs[name] = {"runs": 0, "tokens": 0, "ok": 0, "error": 0, "model": e.get("model", "MiniMax-M2.5")}
        jobs[name]["runs"] += 1
        jobs[name]["tokens"] += e.get("tokens", 0)
        if e.get("status") == "ok":
            jobs[name]["ok"] += 1
        else:
            jobs[name]["error"] += 1
    
    result = []
    for name, data in jobs.items():
        # Estimate cost
        model_key = data.get("model", "MiniMax-M2.5")
        if "/" in model_key:
            model_key = model_key.split("/")[-1]
        
        costs = MODEL_COSTS.get(model_key, {"input": 15.0, "output": 60.0})
        tokens = data["tokens"] / max(data["runs"], 1)
        
        input_tokens = tokens * 0.8
        output_tokens = tokens * 0.2
        cost = (
            (input_tokens * costs["input"] / 1_000_000) +
            (output_tokens * costs["output"] / 1_000_000)
        )
        
        result.append({
            "name": name,
            "runs": data["runs"],
            "tokens": data["tokens"],
            "cost_per_run": round(cost, 4),
            "monthly_runs": 30,
            "monthly_cost": round(cost * 30, 2),
            "status": "ok" if data["error"] == 0 else "error"
        })
    
    return result

def get_cron_stats():
    """Get cron job statistics"""
    crons = get_cron_costs()
    
    return {
        "total_jobs": len(crons),
        "active_jobs": len([c for c in crons if c.get("status") == "ok"]),
        "disabled_jobs": len([c for c in crons if c.get("status") == "error"]),
        "total_monthly_cost": sum(c.get("monthly_cost", 0) for c in crons),
        "jobs": crons
    }
