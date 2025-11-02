"""
Main entry point for Aster Vibe Trader
"""
import asyncio
import threading
from loguru import logger

from config.config import config
from api.aster_client import AsterClient
from agent.trader import VibeTrader
from utils.logger import setup_logger


def run_dashboard_api(trader):
    """Run the dashboard API server in a separate thread"""
    import uvicorn
    from dashboard_api.server import app, set_trader_instance
    
    # Set the trader instance so API can access it
    set_trader_instance(trader)
    
    logger.info(f"Starting Dashboard API on http://localhost:{config.dashboard.api_port}")
    uvicorn.run(app, host="0.0.0.0", port=config.dashboard.api_port, log_level="warning")


async def main():
    """Main function to run the Vibe Trader"""
    setup_logger()
    
    logger.info("=" * 50)
    logger.info("Starting Aster Vibe Trader")
    logger.info(f"Trading Mode: {config.trading.mode}")
    logger.info(f"LLM Provider: {config.llm.provider}")
    logger.info(f"Update Interval: {config.trading.update_interval}s")
    logger.info("=" * 50)
    
    try:
        # Initialize Aster API client
        async with AsterClient() as aster_client:
            # Initialize trading agent
            trader = VibeTrader(aster_client)
            
            # Start dashboard API in background thread
            api_thread = threading.Thread(target=run_dashboard_api, args=(trader,), daemon=True)
            api_thread.start()
            logger.info("Dashboard API started in background")
            
            # Start trading (this will run indefinitely)
            await trader.start()
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        logger.info("Shutting down Vibe Trader")


if __name__ == "__main__":
    asyncio.run(main())

