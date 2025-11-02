"""
View AI training data and performance stats
Shows which decisions were good/bad for future model improvements
"""
import sys
sys.path.append('.')

from utils.trade_tracker import TradeTracker
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def main():
    tracker = TradeTracker()
    
    # Get stats
    stats = tracker.get_stats()
    
    # Display overall stats
    console.print("\n")
    console.print(Panel.fit(
        f"[bold cyan]AI Trading Performance Stats[/bold cyan]\n\n"
        f"Total Trades: [bold]{stats.get('total_trades', 0)}[/bold]\n"
        f"Correct Predictions: [bold green]{stats.get('correct_predictions', 0)}[/bold green]\n"
        f"Win Rate: [bold]{stats.get('win_rate', 0):.2f}%[/bold]\n"
        f"Total P&L: [bold]${stats.get('total_pnl_usd', 0):.2f}[/bold]\n"
        f"Avg P&L per Trade: [bold]${stats.get('avg_pnl_per_trade', 0):.2f}[/bold]",
        title="📊 Performance",
        border_style="cyan"
    ))
    
    # Quality distribution
    quality_dist = stats.get('quality_distribution', {})
    if quality_dist:
        console.print("\n[bold]Quality Distribution:[/bold]")
        for quality, count in quality_dist.items():
            emoji = {"excellent": "🌟", "good": "✅", "neutral": "➖", "bad": "❌", "terrible": "💥"}.get(quality, "")
            console.print(f"  {emoji} {quality.capitalize()}: {count}")
    
    # Get all closed trades
    all_trades = tracker.get_training_data()
    
    if not all_trades:
        console.print("\n[yellow]No completed trades yet. Keep trading to build your dataset![/yellow]\n")
        return
    
    # Show recent trades
    console.print("\n[bold cyan]Recent Trades (Last 10):[/bold cyan]")
    
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Symbol", style="cyan")
    table.add_column("Action", justify="center")
    table.add_column("Entry", justify="right")
    table.add_column("Exit", justify="right")
    table.add_column("P&L", justify="right")
    table.add_column("Correct?", justify="center")
    table.add_column("Quality", justify="center")
    table.add_column("Duration", justify="right")
    
    for trade in all_trades[-10:]:
        symbol = trade["symbol"]
        action = trade["decision"]["action"].upper()
        entry = f"${trade['position']['entry_price']:.4f}"
        exit_price = trade['outcome']['exit_price']
        exit_str = f"${exit_price:.4f}" if exit_price else "Open"
        
        pnl = trade['outcome']['pnl_percent']
        pnl_color = "green" if pnl > 0 else "red"
        pnl_str = f"[{pnl_color}]{pnl:+.2f}%[/{pnl_color}]"
        
        correct = "✅" if trade['outcome']['was_correct'] else "❌"
        
        quality = trade['label']['quality']
        quality_emoji = {"excellent": "🌟", "good": "✅", "neutral": "➖", "bad": "❌", "terrible": "💥"}.get(quality, "")
        quality_str = f"{quality_emoji} {quality.capitalize()}"
        
        duration = f"{trade['outcome']['duration_minutes']:.1f}m"
        
        table.add_row(symbol, action, entry, exit_str, pnl_str, correct, quality_str, duration)
    
    console.print(table)
    
    # Show lessons learned
    console.print("\n[bold cyan]Key Lessons:[/bold cyan]")
    excellent_trades = tracker.get_training_data(quality_filter=["excellent", "good"])
    bad_trades = tracker.get_training_data(quality_filter=["bad", "terrible"])
    
    if excellent_trades:
        console.print(f"\n[bold green]✅ What Works ({len(excellent_trades)} trades):[/bold green]")
        for trade in excellent_trades[-3:]:
            console.print(f"  • {trade['decision']['reasoning'][:100]}...")
            for lesson in trade['label']['lessons']:
                console.print(f"    → {lesson}")
    
    if bad_trades:
        console.print(f"\n[bold red]❌ What Doesn't Work ({len(bad_trades)} trades):[/bold red]")
        for trade in bad_trades[-3:]:
            console.print(f"  • {trade['decision']['reasoning'][:100]}...")
            for lesson in trade['label']['lessons']:
                console.print(f"    → {lesson}")
    
    console.print("\n[bold cyan]💡 This data is being saved for future model training![/bold cyan]")
    console.print(f"[dim]Data stored in: logs/trade_outcomes.json[/dim]\n")

if __name__ == "__main__":
    main()



