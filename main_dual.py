"""
Dual Trading Bot Launcher
Runs both ASTERUSDT and Moon Phase BTC bots simultaneously
"""
import asyncio
import threading
from loguru import logger

from config.config import config
from api.aster_client import AsterClient
from agent.trader import VibeTrader
from agent.moon_trader import MoonPhaseTrader
from utils.logger import setup_logger


def run_dashboard_api(trader, moon_trader):
    """Run the dashboard API server in a separate thread"""
    import uvicorn
    from dashboard_api.server import app, set_trader_instance
    
    # Set the trader instance (for now, just the main one)
    set_trader_instance(trader)
    
    logger.info(f"Starting Dashboard API on http://localhost:{config.dashboard.api_port}")
    uvicorn.run(app, host="0.0.0.0", port=config.dashboard.api_port, log_level="warning")


async def main():
    """Main function to run both traders"""
    setup_logger()
    
    logger.info("=" * 70)
    logger.info("DUAL TRADING BOT SYSTEM")
    logger.info("=" * 70)
    logger.info(f"Bot 1: ASTERUSDT Vibe Trader (AI-driven)")
    logger.info(f"Bot 2: BTCUSDT Moon Phase Trader (Lunar cycles)")
    logger.info(f"Trading Mode: {config.trading.mode}")
    logger.info(f"Update Interval: {config.trading.update_interval}s")
    logger.info("=" * 70)
    
    try:
        # Initialize Aster API clients for both bots
        async with AsterClient() as aster_client_1, AsterClient() as aster_client_2:
            
            # Initialize ASTERUSDT trader
            logger.info("Initializing ASTERUSDT Vibe Trader...")
            aster_trader = VibeTrader(aster_client_1)
            
            # Initialize BTCUSDT Moon Phase trader
            logger.info("Initializing BTCUSDT Moon Phase Trader...")
            moon_trader = MoonPhaseTrader(aster_client_2, symbol="BTCUSDT")
            
            # Start dashboard API in background thread
            api_thread = threading.Thread(
                target=run_dashboard_api, 
                args=(aster_trader, moon_trader), 
                daemon=True
            )
            api_thread.start()
            logger.info("Dashboard API started in background")
            
            # Run both traders concurrently
            logger.success("Starting both trading bots!")
            await asyncio.gather(
                aster_trader.start(),
                moon_trader.start()
            )
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("Shutting down both trading bots")


if __name__ == "__main__":
    asyncio.run(main())

