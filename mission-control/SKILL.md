---
name: mission-control
description: Mission Control Dashboard for OpenClaw - provides comprehensive visibility into agent activities, scheduled tasks, and workspace content through a web-based interface. Use when the user wants to see activity history, view scheduled cron jobs, or search across workspace files and session transcripts. Includes three main components (1) Activity Feed showing all tool calls and file changes grouped by day, (2) Weekly Calendar displaying scheduled cron jobs during work hours (9-18h GMT-3), and (3) Global Search for full-text search across MEMORY.md, memory files, and session transcripts.
---

# Mission Control Dashboard

A comprehensive web-based dashboard for monitoring and searching your OpenClaw workspace.

## Components

### 1. Activity Feed
- **Displays:** All tool calls and file changes from OpenClaw sessions
- **Grouping:** Activities grouped by day
- **Filtering:** Filter by type (all, tool_call, file_change)
- **Data source:** `~/.openclaw/sessions/` and git history

### 2. Weekly Calendar
- **Displays:** Scheduled cron jobs for the upcoming week
- **Format:** Sunday-Saturday grid view
- **Work Hours:** 9:00-18:00 (filtered automatically)
- **Timezone:** America/Sao_Paulo (GMT-3)
- **Data source:** `~/.openclaw/cron-jobs.json`

### 3. Global Search
- **Scope:** MEMORY.md, memory/*.md, session transcripts, workspace files
- **Type:** Full-text search with preview
- **Results:** Grouped by type (documents vs sessions) with match counts

## Usage

To launch the Mission Control dashboard:

```bash
# Start OpenClaw Canvas Host (if not already running)
openclaw canvas present --url file://$PWD/skills/mission-control/assets/dashboard/index.html
```

Or serve via Python:

```bash
cd skills/mission-control/assets/dashboard
python3 -m http.server 8080
# Open http://localhost:8080 in browser
```

## Backend Scripts

The dashboard uses Python scripts to fetch data:

### `get_activity_feed.py`
Reads OpenClaw session transcripts and git history to build activity timeline.

```bash
python3 scripts/get_activity_feed.py
```

Returns JSON grouped by date:
```json
{
  "2026-02-06": [
    {
      "timestamp": 1738869045000,
      "type": "tool_call",
      "action": "web_search",
      "details": { "query": "..." },
      "formatted_time": "18:30:45"
    }
  ]
}
```

### `get_cron_jobs.py`
Parses OpenClaw cron jobs and formats for weekly calendar view.

```bash
python3 scripts/get_cron_jobs.py
```

Returns calendar data with events filtered to work hours (9-18h).

### `search_workspace.py`
Full-text search across workspace and sessions.

```bash
python3 scripts/search_workspace.py "<query>"
```

Returns search results with file paths, match counts, and preview snippets.

## Web App Stack

- **HTML/CSS/JS:** Vanilla JavaScript with no build step
- **UI Framework:** Bootstrap 5 + Tailwind CSS
- **Charts:** ApexCharts (for future analytics)
- **Icons:** Font Awesome 6

## Development Mode

The dashboard currently uses mock data in `api.js` for development. To connect to real backend scripts:

1. Set up a backend server (Flask/FastAPI) that executes Python scripts
2. Update `API.executeScript()` in `api.js` to call your backend endpoints
3. Ensure CORS is configured if serving from different origin

## Future Enhancements

- Real-time updates via WebSocket
- Historical analytics charts
- Export activity logs
- Task creation from dashboard
- Mobile-responsive layout improvements
