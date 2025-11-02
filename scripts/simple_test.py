"""
Simple test - just check if we can get markets and ticker
"""
import asyncio
import sys
sys.path.append('.')

from api.aster_client import AsterClient
from loguru import logger


async def test():
    """Quick test"""
    logger.info("Testing Aster API...")
    
    async with AsterClient() as client:
        # Test market data (public)
        markets = await client.get_markets()
        logger.success(f"✓ Got {len(markets.get('symbols', []))} markets")
        
        # Get ticker for BTC
        ticker = await client.get_ticker("BTCUSDT")
        logger.success(f"✓ BTCUSDT Price: ${ticker.get('lastPrice')}")
        
        # Try to get account info (private - might fail)
        try:
            account = await client.get_account()
            logger.success(f"✓ Account info retrieved!")
            logger.info(f"Assets: {len(account.get('assets', []))}")
        except Exception as e:
            logger.warning(f"Account endpoint needs more work: {e}")
        
        logger.success("\n✅ Basic connection is working! Public endpoints work great.")
        logger.info("Private endpoints (balance, positions) may need further investigation.")


if __name__ == "__main__":
    asyncio.run(test())

