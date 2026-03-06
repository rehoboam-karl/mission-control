/**
 * API Interface for Mission Control Dashboard
 * Handles communication with Python backend scripts
 */

const API = {
    // Base paths
    scriptsPath: '../../scripts/',
    
    /**
     * Execute a Python script and return JSON result
     */
    async executeScript(scriptName, args = []) {
        try {
            // In a real deployment, this would call a backend endpoint
            // For now, we'll simulate with demo data
            console.log(`Would execute: ${scriptName}`, args);
            
            switch(scriptName) {
                case 'get_activity_feed.py':
                    return this.getMockActivityFeed();
                case 'get_cron_jobs.py':
                    return this.getMockCronJobs();
                case 'search_workspace.py':
                    return this.getMockSearchResults(args[0]);
                default:
                    throw new Error(`Unknown script: ${scriptName}`);
            }
        } catch (error) {
            console.error('Script execution error:', error);
            throw error;
        }
    },
    
    /**
     * Get activity feed
     */
    async getActivityFeed() {
        return await this.executeScript('get_activity_feed.py');
    },
    
    /**
     * Get cron jobs calendar
     */
    async getCronJobs() {
        return await this.executeScript('get_cron_jobs.py');
    },
    
    /**
     * Search workspace
     */
    async searchWorkspace(query) {
        return await this.executeScript('search_workspace.py', [query]);
    },
    
    /**
     * Mock data generators (for development/demo)
     */
    getMockActivityFeed() {
        const now = new Date();
        const today = now.toISOString().split('T')[0];
        const yesterday = new Date(now - 86400000).toISOString().split('T')[0];
        
        return {
            [today]: [
                {
                    type: 'tool_call',
                    action: 'web_search',
                    details: { query: 'SLV stock price' },
                    formatted_time: '18:30:45',
                    session: 'main'
                },
                {
                    type: 'tool_call',
                    action: 'exec',
                    details: { command: 'gh repo list' },
                    formatted_time: '16:59:22',
                    session: 'main'
                },
                {
                    type: 'file_change',
                    action: 'git_commit',
                    details: {
                        message: 'Update MEMORY.md',
                        files: [{ status: 'M', path: 'MEMORY.md' }]
                    },
                    formatted_time: '15:42:10'
                }
            ],
            [yesterday]: [
                {
                    type: 'tool_call',
                    action: 'gateway_config_patch',
                    details: { section: 'models' },
                    formatted_time: '22:07:53',
                    session: 'main'
                },
                {
                    type: 'file_change',
                    action: 'git_commit',
                    details: {
                        message: 'Create mission-control skill',
                        files: [
                            { status: 'A', path: 'skills/mission-control/SKILL.md' },
                            { status: 'A', path: 'skills/mission-control/scripts/get_activity_feed.py' }
                        ]
                    },
                    formatted_time: '21:30:15'
                }
            ]
        };
    },
    
    getMockCronJobs() {
        const now = new Date();
        const weekStart = new Date(now);
        weekStart.setDate(now.getDate() + (7 - now.getDay()));
        weekStart.setHours(0, 0, 0, 0);
        
        const events = [];
        for (let i = 0; i < 7; i++) {
            const day = new Date(weekStart);
            day.setDate(weekStart.getDate() + i);
            
            if (i % 2 === 0) {
                day.setHours(10, 0, 0, 0);
                events.push({
                    id: `job-${i}-1`,
                    title: 'Check Email Inbox',
                    start: day.toISOString(),
                    day: day.toLocaleDateString('en-US', { weekday: 'long' }),
                    time: '10:00'
                });
            }
            
            if (i % 3 === 0) {
                day.setHours(14, 0, 0, 0);
                events.push({
                    id: `job-${i}-2`,
                    title: 'Sync Calendar',
                    start: day.toISOString(),
                    day: day.toLocaleDateString('en-US', { weekday: 'long' }),
                    time: '14:00'
                });
            }
        }
        
        return {
            week_start: weekStart.toISOString(),
            week_end: new Date(weekStart.getTime() + 7 * 86400000).toISOString(),
            events: events
        };
    },
    
    getMockSearchResults(query) {
        if (!query) {
            return { query: '', total_results: 0, documents: [], sessions: [] };
        }
        
        return {
            query: query,
            total_results: 3,
            documents: [
                {
                    file: 'MEMORY.md',
                    path: '/home/user/.openclaw/workspace/MEMORY.md',
                    type: 'document',
                    matches: 2,
                    results: [
                        {
                            line_number: 15,
                            line: `Found information about ${query}`,
                            context: `Context around ${query} in MEMORY.md`,
                            preview: `Preview of match for ${query}`
                        }
                    ]
                },
                {
                    file: 'memory/2026-02-06.md',
                    path: '/home/user/.openclaw/workspace/memory/2026-02-06.md',
                    type: 'document',
                    matches: 1,
                    results: [
                        {
                            line_number: 42,
                            line: `Daily note mentioning ${query}`,
                            preview: `Daily context for ${query}`
                        }
                    ]
                }
            ],
            sessions: [
                {
                    file: 'agent-main-main',
                    path: '/home/user/.openclaw/sessions/agent-main-main.jsonl',
                    type: 'session',
                    matches: 1,
                    results: [
                        {
                            line_number: 234,
                            timestamp: new Date().toISOString(),
                            role: 'user',
                            preview: `User asked about ${query}`
                        }
                    ]
                }
            ]
        };
    }
};
