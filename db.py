"""Mission Control v4 - Database"""

import aiosqlite
from pathlib import Path
from config import MC_DB

async def get_db():
    """Get database connection"""
    db = await aiosqlite.connect(MC_DB)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    """Initialize database schema"""
    # Create a new connection for initialization
    db = await aiosqlite.connect(MC_DB)
    db.row_factory = aiosqlite.Row
    
    try:
        # Agents table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'unknown',
                last_seen INTEGER,
                session_key TEXT,
                model TEXT,
                message_count INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Events table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                type TEXT NOT NULL,
                agent_name TEXT,
                action TEXT,
                details TEXT,
                severity TEXT DEFAULT 'info'
            )
        """)
        
        # Cron jobs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cron_jobs (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                schedule TEXT,
                last_run INTEGER,
                next_run INTEGER,
                status TEXT DEFAULT 'pending',
                cost REAL DEFAULT 0,
                error TEXT
            )
        """)
        
        # Tasks table (from todoist)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                todoist_id TEXT UNIQUE,
                content TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                due TEXT,
                project TEXT,
                completed INTEGER DEFAULT 0,
                synced_at INTEGER
            )
        """)
        
        # Relationships table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                type TEXT DEFAULT 'related',
                weight REAL DEFAULT 1.0
            )
        """)
        
        await db.commit()
    finally:
        await db.close()

async def close_db(db):
    await db.close()
