/**
 * Mission Control Dashboard - Main Application Logic
 */

// Global state
let currentActivityFilter = 'all';
let activityData = null;
let calendarData = null;

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Mission Control Dashboard initialized');
    loadDashboard();
});

/**
 * Load all dashboard components
 */
async function loadDashboard() {
    await Promise.all([
        loadActivityFeed(),
        loadCalendar(),
        updateStats()
    ]);
}

/**
 * Refresh all data
 */
async function refreshAll() {
    console.log('Refreshing all data...');
    await loadDashboard();
}

/**
 * Load and render activity feed
 */
async function loadActivityFeed() {
    try {
        activityData = await API.getActivityFeed();
        renderActivityFeed(activityData);
    } catch (error) {
        console.error('Error loading activity feed:', error);
        document.getElementById('activityFeed').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to load activity feed
            </div>
        `;
    }
}

/**
 * Render activity feed
 */
function renderActivityFeed(data) {
    const container = document.getElementById('activityFeed');
    
    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-inbox fa-3x mb-3"></i>
                <p>No activities yet</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    for (const [date, activities] of Object.entries(data)) {
        // Filter activities if needed
        const filtered = currentActivityFilter === 'all' 
            ? activities 
            : activities.filter(a => a.type === currentActivityFilter);
        
        if (filtered.length === 0) continue;
        
        html += `
            <div class="activity-group">
                <div class="activity-date-header">
                    ${formatDate(date)}
                </div>
        `;
        
        for (const activity of filtered) {
            html += renderActivityItem(activity);
        }
        
        html += '</div>';
    }
    
    container.innerHTML = html || `
        <div class="text-center text-muted py-5">
            <p>No activities match the current filter</p>
        </div>
    `;
}

/**
 * Render single activity item
 */
function renderActivityItem(activity) {
    const iconClass = activity.type === 'tool_call' ? 'fa-cog' : 'fa-file-alt';
    const actionLabel = formatActionLabel(activity);
    const description = formatActivityDescription(activity);
    
    return `
        <div class="activity-item ${activity.type}">
            <div class="activity-icon ${activity.type}">
                <i class="fas ${iconClass}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${actionLabel}</div>
                <div class="activity-description">${description}</div>
                <div class="activity-time">
                    <i class="far fa-clock me-1"></i>${activity.formatted_time}
                </div>
            </div>
        </div>
    `;
}

/**
 * Format action label
 */
function formatActionLabel(activity) {
    if (activity.type === 'tool_call') {
        return `<i class="fas fa-bolt me-1"></i>${activity.action}`;
    } else if (activity.type === 'file_change') {
        return `<i class="fas fa-code-branch me-1"></i>${activity.details.message}`;
    }
    return activity.action;
}

/**
 * Format activity description
 */
function formatActivityDescription(activity) {
    if (activity.type === 'tool_call') {
        const details = activity.details;
        if (details.query) return `Query: ${details.query}`;
        if (details.command) return `Command: ${details.command}`;
        return JSON.stringify(details).slice(0, 100);
    } else if (activity.type === 'file_change') {
        const files = activity.details.files || [];
        if (files.length === 0) return 'No files changed';
        if (files.length === 1) return files[0].path;
        return `${files.length} files changed`;
    }
    return '';
}

/**
 * Filter activities by type
 */
function filterActivities(type) {
    currentActivityFilter = type;
    
    // Update button states
    document.querySelectorAll('.btn-group button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Re-render with filter
    if (activityData) {
        renderActivityFeed(activityData);
    }
}

/**
 * Load and render calendar
 */
async function loadCalendar() {
    try {
        calendarData = await API.getCronJobs();
        renderCalendar(calendarData);
    } catch (error) {
        console.error('Error loading calendar:', error);
        document.getElementById('weeklyCalendar').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to load calendar
            </div>
        `;
    }
}

/**
 * Render weekly calendar
 */
function renderCalendar(data) {
    const container = document.getElementById('weeklyCalendar');
    
    if (!data || !data.events) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="fas fa-calendar-times fa-3x mb-3"></i>
                <p>No scheduled tasks</p>
            </div>
        `;
        return;
    }
    
    // Group events by day
    const eventsByDay = {};
    const weekStart = new Date(data.week_start);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    // Initialize all days
    for (let i = 0; i < 7; i++) {
        const day = new Date(weekStart);
        day.setDate(weekStart.getDate() + i);
        eventsByDay[days[i]] = {
            date: day,
            events: []
        };
    }
    
    // Group events
    for (const event of data.events) {
        if (eventsByDay[event.day]) {
            eventsByDay[event.day].events.push(event);
        }
    }
    
    // Render calendar grid
    let html = '<div class="calendar-week">';
    
    for (const day of days) {
        const dayData = eventsByDay[day];
        const isToday = isToday Date(dayData.date);
        const dateStr = dayData.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        
        html += `
            <div class="calendar-day ${isToday ? 'today' : ''}">
                <div class="calendar-day-header">
                    <div>${day.slice(0, 3)}</div>
                    <div class="text-muted" style="font-size: 0.75rem">${dateStr}</div>
                </div>
        `;
        
        if (dayData.events.length > 0) {
            for (const event of dayData.events) {
                html += `
                    <div class="calendar-event" onclick="showEventDetails('${event.id}')">
                        <div class="calendar-event-time">${event.time}</div>
                        <div class="calendar-event-title">${event.title}</div>
                    </div>
                `;
            }
        } else {
            html += '<div class="text-muted small">No events</div>';
        }
        
        html += '</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Check if date is today
 */
function isTodayDate(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
}

/**
 * Show event details (placeholder)
 */
function showEventDetails(eventId) {
    console.log('Show event details:', eventId);
    alert(`Event details for ${eventId}\n(Full implementation pending)`);
}

/**
 * Perform global search
 */
async function performSearch() {
    const query = document.getElementById('globalSearch').value.trim();
    
    if (!query) {
        document.getElementById('searchResults').style.display = 'none';
        return;
    }
    
    const resultsContainer = document.getElementById('searchResults');
    const contentContainer = document.getElementById('searchResultsContent');
    
    resultsContainer.style.display = 'block';
    contentContainer.innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border text-primary spinner-border-sm me-2"></div>
            Searching...
        </div>
    `;
    
    try {
        const results = await API.searchWorkspace(query);
        renderSearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
        contentContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Search failed
            </div>
        `;
    }
}

/**
 * Render search results
 */
function renderSearchResults(results) {
    const container = document.getElementById('searchResultsContent');
    
    if (results.total_results === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="fas fa-search fa-2x mb-2"></i>
                <p>No results found for "${results.query}"</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="mb-3">
            <strong>${results.total_results}</strong> results found for "<em>${results.query}</em>"
        </div>
    `;
    
    // Render document results
    if (results.documents && results.documents.length > 0) {
        html += '<h6 class="mt-3 mb-2"><i class="fas fa-file-alt me-2"></i>Documents</h6>';
        for (const doc of results.documents) {
            html += renderSearchResultItem(doc, results.query);
        }
    }
    
    // Render session results
    if (results.sessions && results.sessions.length > 0) {
        html += '<h6 class="mt-3 mb-2"><i class="fas fa-comments me-2"></i>Sessions</h6>';
        for (const session of results.sessions) {
            html += renderSearchResultItem(session, results.query);
        }
    }
    
    container.innerHTML = html;
}

/**
 * Render single search result
 */
function renderSearchResultItem(item, query) {
    const icon = item.type === 'document' ? 'fa-file-alt' : 'fa-comments';
    const badge = item.type === 'document' ? 'primary' : 'info';
    
    let preview = '';
    if (item.results && item.results.length > 0) {
        const firstResult = item.results[0];
        preview = firstResult.preview || firstResult.line || '';
        // Highlight query terms
        preview = highlightText(preview, query);
    }
    
    return `
        <div class="search-result-item">
            <div class="search-result-header">
                <div class="search-result-title">
                    <i class="fas ${icon} me-2"></i>
                    ${item.file}
                    <span class="badge bg-${badge} search-result-badge">
                        ${item.matches} match${item.matches !== 1 ? 'es' : ''}
                    </span>
                </div>
            </div>
            <div class="search-result-preview">${preview}</div>
            <div class="mt-2">
                <small class="text-muted">
                    <i class="fas fa-folder me-1"></i>${item.path}
                </small>
            </div>
        </div>
    `;
}

/**
 * Highlight search terms in text
 */
function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<span class="search-highlight">$1</span>');
}

/**
 * Update statistics
 */
async function updateStats() {
    // Count activities
    if (activityData) {
        const totalActivities = Object.values(activityData).reduce((sum, day) => sum + day.length, 0);
        document.getElementById('statActivities').textContent = totalActivities;
    }
    
    // Count scheduled tasks
    if (calendarData && calendarData.events) {
        document.getElementById('statScheduled').textContent = calendarData.events.length;
    }
    
    // Count files (placeholder)
    document.getElementById('statFiles').textContent = '42';
}

/**
 * Format date string
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
}
