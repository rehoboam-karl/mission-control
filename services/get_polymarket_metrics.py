#!/usr/bin/env python3
"""
Polymarket Bot Metrics Script
Reads trading data and provides observability metrics for Mission Control.
"""
import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Bot data paths
BOT_DIR = Path.home() / "projects" / "Polymarket-Copy-Trading-Bot" / "rust"
LOG_FILE = BOT_DIR / "logs" / "trading.log"
CSV_FILE = BOT_DIR / "matches_optimized.csv"

def get_bot_status():
    """Check if bot process is running."""
    try:
        result = os.popen("pgrep -f 'polymarket|pm_whale' 2>/dev/null").read()
        if result.strip():
            return "running"
        return "stopped"
    except Exception:
        return "unknown"

def parse_trades_from_csv():
    """Parse trades from CSV file."""
    trades = []
    if not CSV_FILE.exists():
        return trades
    
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    trade = {
                        'timestamp': row.get('timestamp', ''),
                        'usd_value': float(row.get('usd_value', 0)),
                        'shares': float(row.get('shares', 0)),
                        'price_per_share': float(row.get('price_per_share', 0)),
                        'direction': row.get('direction', ''),
                        'order_status': row.get('order_status', ''),
                        'clob_asset_id': row.get('clob_asset_id', ''),
                        'tx_hash': row.get('tx_hash', ''),
                    }
                    trades.append(trade)
                except (ValueError, KeyError):
                    continue
    except Exception as e:
        print(f"Error reading CSV: {e}", file=__import__('sys').stderr)
    
    return trades

def parse_logs_from_file():
    """Parse structured JSON logs from trading.log."""
    events = []
    if not LOG_FILE.exists():
        return events
    
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # Try to parse as JSON
                    event = json.loads(line)
                    events.append(event)
                except json.JSONDecodeError:
                    # Skip non-JSON lines
                    continue
    except Exception as e:
        print(f"Error reading logs: {e}", file=__import__('sys').stderr)
    
    return events

def get_recent_trades(trades, limit=10):
    """Get most recent trades."""
    return trades[-limit:] if len(trades) > limit else trades

def calculate_daily_pnl(trades):
    """Calculate P&L for today."""
    today = datetime.now().date()
    daily_pnl = 0.0
    
    for trade in trades:
        try:
            # Parse timestamp - handle different formats
            ts = trade.get('timestamp', '')
            if not ts:
                continue
            
            # Handle "2026-03-07 13:45:31.253" format
            trade_date = datetime.strptime(ts.split('.')[0], '%Y-%m-%d %H:%M:%S').date()
            
            if trade_date == today:
                # For BUY trades, cost is negative P&L
                # For SELL trades, proceeds are positive P&L
                value = trade.get('usd_value', 0)
                if trade.get('direction', '').startswith('BUY'):
                    daily_pnl -= value
                elif trade.get('direction', '').startswith('SELL'):
                    daily_pnl += value
        except Exception:
            continue
    
    return daily_pnl

def get_markets_validated_24h(events):
    """Count markets validated in last 24 hours from logs."""
    cutoff = datetime.now() - timedelta(hours=24)
    count = 0
    
    for event in events:
        if isinstance(event, dict):
            event_type = event.get('event_type', '')
            if event_type == 'market_validated':
                # Try to extract timestamp
                try:
                    ts = event.get('timestamp', '')
                    if ts:
                        event_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        if event_time >= cutoff:
                            count += 1
                except Exception:
                    count += 1
    
    return count

def get_top_whales(events, limit=5):
    """Extract top whales from events."""
    whale_scores = defaultdict(int)
    
    for event in events:
        if isinstance(event, dict):
            event_type = event.get('event_type', '')
            if event_type == 'whale_detected':
                wallet = event.get('wallet', event.get('address', ''))
                if wallet:
                    # Score based on trade volume/frequency
                    score = event.get('score', event.get('whale_score', 0))
                    whale_scores[wallet] = max(whale_scores[wallet], score)
    
    # Sort by score
    sorted_whales = sorted(whale_scores.items(), key=lambda x: x[1], reverse=True)
    return [{'wallet': w, 'score': s} for w, s in sorted_whales[:limit]]

def main():
    """Main function to gather all metrics."""
    metrics = {
        'status': get_bot_status(),
        'timestamp': datetime.now().isoformat(),
        'data_source': 'csv' if CSV_FILE.exists() else 'none',
    }
    
    # Parse data sources
    trades = parse_trades_from_csv()
    events = parse_logs_from_file()
    
    # Calculate metrics
    metrics['recent_trades'] = get_recent_trades(trades, limit=10)
    metrics['daily_pnl'] = calculate_daily_pnl(trades)
    metrics['total_trades'] = len(trades)
    metrics['markets_validated_24h'] = get_markets_validated_24h(events)
    metrics['top_whales'] = get_top_whales(events, limit=5)
    
    # Add whale detection from CSV (based on trade volume)
    if trades:
        trade_volumes = defaultdict(float)
        for trade in trades:
            wallet = trade.get('clob_asset_id', '')[:20]  # Use asset ID as proxy
            trade_volumes[wallet] += trade.get('usd_value', 0)
        
        sorted_volumes = sorted(trade_volumes.items(), key=lambda x: x[1], reverse=True)[:5]
        metrics['top_by_volume'] = [{'asset_id': a, 'volume': v} for a, v in sorted_volumes]
    
    # Output as JSON
    print(json.dumps(metrics, indent=2, default=str))

if __name__ == '__main__':
    main()
