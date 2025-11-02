"""
Test script to verify Aster API connection
"""
import asyncio
import sys
sys.path.append('.')

from api.aster_client import AsterClient
from config.config import config
from loguru import logger


async def test_connection():
    """Test connection to Aster API"""
    logger.info("Testing Aster API connection...")
    logger.info(f"API URL: {config.aster.api_url}")
    
    try:
        async with AsterClient() as client:
            # Test market data endpoints
            logger.info("Fetching markets...")
            markets = await client.get_markets()
            logger.info(f"✓ Markets: {len(markets)} available")
            
            logger.info("Fetching orderbook...")
            orderbook = await client.get_orderbook()
            logger.info(f"✓ Orderbook: {len(orderbook.get('bids', []))} bids, {len(orderbook.get('asks', []))} asks")
            
            logger.info("Fetching recent trades...")
            trades = await client.get_recent_trades()
            logger.info(f"✓ Recent trades: {len(trades)} trades")
            
            logger.info("Fetching funding rates...")
            funding = await client.get_funding_rates()
            logger.info(f"✓ Funding rates retrieved")
            
            # Test account endpoints
            logger.info("Fetching balance...")
            balance = await client.get_balance()
            logger.info(f"✓ Balance: ${balance.get('total', 0)}")
            
            logger.info("Fetching positions...")
            positions = await client.get_positions()
            logger.info(f"✓ Positions: {len(positions)} open")
            
            logger.success("All API tests passed! ✓")
            
    except Exception as e:
        logger.error(f"API test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_connection())

