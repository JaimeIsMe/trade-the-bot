"""
Simple real-time monitor for Aster Vibe Trader
Shows latest decisions, errors, and status
"""
import time
import os
from datetime import datetime
from collections import deque

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_latest_logs(filename, num_lines=50):
    """Get latest log entries"""
    try:
        with open(filename, 'r') as f:
            return deque(f, num_lines)
    except FileNotFoundError:
        return []

def parse_log_line(line):
    """Extract key info from log line"""
    if 'Decision:' in line:
        return ('DECISION', line.split('Decision:')[1].strip())
    elif 'ERROR' in line:
        if 'rate_limit' in line:
            return ('ERROR', 'Rate limit hit')
        elif 'authentication_error' in line:
            return ('ERROR', 'Invalid API key')
        elif '400' in line or '401' in line or '405' in line:
            return ('ERROR', 'API error')
        return ('ERROR', 'Error occurred')
    elif 'SUCCESS' in line or 'success' in line.lower():
        return ('SUCCESS', line)
    return None

def monitor():
    """Main monitoring loop"""
    print("🚀 Aster Vibe Trader Monitor")
    print("=" * 60)
    print("Press Ctrl+C to exit\n")
    
    last_decisions = []
    last_errors = []
    
    while True:
        clear_screen()
        
        print("=" * 60)
        print(f"📊 ASTER VIBE TRADER MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Read latest logs
        logs = get_latest_logs('logs/vibe_trader.log', 100)
        
        # Parse for decisions and errors
        recent_decisions = []
        recent_errors = []
        
        for line in logs:
            parsed = parse_log_line(line)
            if parsed:
                log_type, content = parsed
                if log_type == 'DECISION' and 'Decision:' in line:
                    timestamp = line.split('|')[0].strip()
                    recent_decisions.append((timestamp, content))
                elif log_type == 'ERROR':
                    timestamp = line.split('|')[0].strip() if '|' in line else 'Unknown'
                    recent_errors.append((timestamp, content))
        
        # Display latest decisions
        print("\n💡 RECENT DECISIONS (Latest 5):")
        print("-" * 60)
        if recent_decisions:
            for ts, decision in recent_decisions[-5:]:
                action = decision.split('-')[0].strip()
                reason = decision.split('-', 1)[1].strip() if '-' in decision else 'N/A'
                
                # Color code actions
                if 'hold' in action.lower():
                    icon = "⏸️"
                elif 'long' in action.lower() or 'buy' in action.lower():
                    icon = "📈"
                elif 'short' in action.lower() or 'sell' in action.lower():
                    icon = "📉"
                else:
                    icon = "❓"
                
                print(f"{icon} [{ts}] {action}")
                if reason != 'N/A':
                    print(f"   └─ {reason[:80]}")
        else:
            print("   No decisions yet...")
        
        # Display error summary
        print("\n⚠️  ERROR SUMMARY:")
        print("-" * 60)
        if recent_errors:
            error_counts = {}
            for _, error in recent_errors[-20:]:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   • {error}: {count}x")
        else:
            print("   ✅ No errors!")
        
        # System status
        print("\n📊 SYSTEM STATUS:")
        print("-" * 60)
        
        # Check if bot is running
        try:
            import psutil
            python_procs = [p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]
            if python_procs:
                print(f"   ✅ Bot is RUNNING ({len(python_procs)} Python process(es))")
            else:
                print("   ❌ Bot appears STOPPED")
        except:
            print("   ℹ️  Status check unavailable (install psutil for process monitoring)")
        
        # Log file info
        if os.path.exists('logs/vibe_trader.log'):
            size = os.path.getsize('logs/vibe_trader.log') / 1024
            print(f"   📝 Log file: {size:.1f} KB")
        
        print("\n" + "=" * 60)
        print("Refreshing every 5 seconds... (Ctrl+C to exit)")
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped!")

