"""
Launch script for Aster Vibe Trader
Runs both the trading agent and dashboard API server
"""
import asyncio
import uvicorn
from multiprocessing import Process
from loguru import logger

from main import main as run_trader
from dashboard_api.server import app, set_trader_instance
from config.config import config
from utils.logger import setup_logger


def run_dashboard_api():
    """Run the dashboard API server"""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.dashboard.api_port,
        log_level="info"
    )


async def run_system():
    """Run the complete system"""
    setup_logger()
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Aster Vibe Trader System")
    logger.info("=" * 60)
    logger.info(f"Trading Mode: {config.trading.mode}")
    logger.info(f"LLM Provider: {config.llm.provider} ({config.llm.model})")
    logger.info(f"Dashboard API: http://localhost:{config.dashboard.api_port}")
    logger.info(f"Dashboard UI: http://localhost:{config.dashboard.port}")
    logger.info("=" * 60)
    
    # Start dashboard API in separate process
    api_process = Process(target=run_dashboard_api)
    api_process.start()
    
    try:
        # Run the trader
        await run_trader()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        logger.info("Shutting down system...")
        api_process.terminate()
        api_process.join()


if __name__ == "__main__":
    asyncio.run(run_system())

