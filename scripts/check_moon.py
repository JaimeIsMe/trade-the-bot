"""
Check current moon phase for trading
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.moon_trader import MoonPhaseTrader
from api.aster_client import AsterClient

# Create a moon trader instance just to check the phase
trader = MoonPhaseTrader(AsterClient(), "BTCUSDT")
moon = trader.get_moon_phase()

print("\n" + "=" * 60)
print("MOON CURRENT MOON PHASE FOR TRADING")
print("=" * 60)
print(f"\nPhase: {moon['phase_name'].encode('ascii', 'ignore').decode()}")
print(f"Percentage: {moon['phase_percentage']:.1f}%")
print(f"Illumination: {moon['illumination']:.1f}%")
print(f"Trend: {moon['trend'].upper()}")
print(f"\nTrading Bias: {moon['bias']}")
print(f"Reasoning: {moon['reasoning']}")
print("\n" + "=" * 60)
print("Remember: Moon wanes = BTC waxes = LONG")
print("          Moon waxes = BTC wanes = SHORT")
print("=" * 60 + "\n")

