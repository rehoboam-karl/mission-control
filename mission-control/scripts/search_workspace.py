#!/usr/bin/env python3
"""
Full-text search across workspace files, memory, and sessions.
"""
import json
import sys
import re
from pathlib import Path

def search_file(filepath, query, context_lines=2):
    """Search within a file and return matches with context."""
    matches = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                # Get context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = ''.join(lines[start:end])
                
                matches.append({
                    'line_number': i + 1,
                    'line': line.strip(),
                    'context': context.strip(),
                    'preview': line.strip()[:200]
                })
    
    except Exception as e:
        print(f"Error searching {filepath}: {e}", file=sys.stderr)
    
    return matches

def search_workspace(query, workspace_dir):
    """Search across all relevant workspace files."""
    results = []
    workspace_path = Path(workspace_dir)
    
    # Search patterns
    patterns = [
        'MEMORY.md',
        'memory/*.md',
        'memory/**/*.md',
        '*.md',
        'skills/**/*.md'
    ]
    
    searched_files = set()
    
    for pattern in patterns:
        for filepath in workspace_path.glob(pattern):
            if filepath in searched_files:
                continue
            searched_files.add(filepath)
            
            if filepath.is_file():
                matches = search_file(filepath, query)
                if matches:
                    results.append({
                        'file': str(filepath.relative_to(workspace_path)),
                        'path': str(filepath),
                        'type': 'document',
                        'matches': len(matches),
                        'results': matches[:5]  # Limit to 5 matches per file
                    })
    
    return results

def search_sessions(query, sessions_dir):
    """Search OpenClaw session transcripts."""
    results = []
    sessions_path = Path(sessions_dir)
    
    if not sessions_path.exists():
        return results
    
    for session_file in sessions_path.glob("**/*.jsonl"):
        matches = []
        
        try:
            with open(session_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    if query.lower() in line.lower():
                        try:
                            entry = json.loads(line)
                            matches.append({
                                'line_number': line_num,
                                'timestamp': entry.get('ts'),
                                'role': entry.get('role'),
                                'preview': str(entry.get('content', ''))[:200]
                            })
                        except json.JSONDecodeError:
                            continue
                
                if matches:
                    results.append({
                        'file': session_file.stem,
                        'path': str(session_file),
                        'type': 'session',
                        'matches': len(matches),
                        'results': matches[:3]  # Limit to 3 matches per session
                    })
        
        except Exception as e:
            print(f"Error searching {session_file}: {e}", file=sys.stderr)
            continue
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: search_workspace.py <query>", file=sys.stderr)
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    
    # Paths
    openclaw_dir = Path.home() / '.openclaw'
    workspace_dir = openclaw_dir / 'workspace'
    sessions_dir = openclaw_dir / 'sessions'
    
    print(f"Searching for: {query}", file=sys.stderr)
    
    # Search
    workspace_results = search_workspace(query, workspace_dir)
    session_results = search_sessions(query, sessions_dir)
    
    # Combine and output
    output = {
        'query': query,
        'total_results': len(workspace_results) + len(session_results),
        'documents': workspace_results,
        'sessions': session_results
    }
    
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
