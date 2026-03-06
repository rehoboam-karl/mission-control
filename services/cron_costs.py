"""Cron Costs Service - Calculate costs per cron job from cron logs"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

OPENCLAW_HOME = Path.home() / ".openclaw"

def get_cron_jobs() -> list:
    """Get cron jobs from cron logs"""
    jobs = defaultdict(lambda: {"runs": 0, "ok": 0, "error": 0, "last_run": None, "total_tokens": 0})
    
    cron_dir = OPENCLAW_HOME / "cron"
    if cron_dir.exists():
        for jsonl_file in cron_dir.rglob("*.jsonl"):
            try:
                with open(jsonl_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            if entry.get("action") == "finished":
                                job_name = entry.get("jobName", entry.get("jobId", "unknown"))
                                ts = entry.get("ts", 0)
                                
                                jobs[job_name]["runs"] += 1
                                if entry.get("status") == "ok":
                                    jobs[job_name]["ok"] += 1
                                else:
                                    jobs[job_name]["error"] += 1
                                
                                if ts and (jobs[job_name]["last_run"] is None or ts > jobs[job_name]["last_run"]):
                                    jobs[job_name]["last_run"] = ts
                                
                                jobs[job_name]["total_tokens"] += entry.get("usage", {}).get("total_tokens", 0)
                        except:
                            pass
            except:
                pass
    
    # Convert to list
    result = []
    for name, data in jobs.items():
        last_run_str = "never"
        if data["last_run"]:
            dt = datetime.fromtimestamp(data["last_run"] / 1000)
            last_run_str = dt.strftime("%Y-%m-%d %H:%M")
        
        status = "active" if data["error"] == 0 else "error"
        
        result.append({
            "name": name,
            "schedule": "auto",
            "enabled": True,
            "last_run": last_run_str,
            "next_run": "",
            "status": status,
            "runs": data["runs"],
            "tokens": data["total_tokens"]
        })
    
    # Sort by last run descending
    result.sort(key=lambda x: x["last_run"] or "", reverse=True)
    return result

def calculate_job_cost(job_name: str, duration_ms: int = 0) -> float:
    """Calculate cost of a job execution"""
    COSTS = {
        'input': 0.15,
        'output': 0.60,
    }
    estimated_tokens = (duration_ms / 60000) * 1000
    cost = (estimated_tokens / 1_000_000) * (COSTS['input'] + COSTS['output'])
    return round(cost, 4)

def get_cron_stats() -> dict:
    """Get cron job statistics"""
    jobs = get_cron_jobs()
    
    return {
        "total_jobs": len(jobs),
        "active_jobs": len([j for j in jobs if j.get("status") == "active"]),
        "disabled_jobs": len([j for j in jobs if j.get("status") == "error"]),
        "jobs": jobs
    }
