"""
Test script to place a small manual trade
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.aster_client import AsterClient
from config.config import config
from loguru import logger


async def test_small_trade():
    """Place a small $1 LONG trade on BTCUSDT"""
    
    logger.info("=" * 60)
    logger.info("Testing Small Trade: $1 LONG on BTCUSDT")
    logger.info("=" * 60)
    
    async with AsterClient() as client:
        try:
            # Get current price
            logger.info("Fetching current BTC price...")
            ticker = await client.get_ticker("BTCUSDT")
            current_price = float(ticker.get('lastPrice', 0))
            logger.info(f"Current BTC Price: ${current_price:,.2f}")
            
            # Calculate BTC quantity for $1 USD
            usd_amount = 1.0
            btc_quantity = usd_amount / current_price
            btc_quantity = round(btc_quantity, 3)  # Round to 3 decimals
            
            if btc_quantity < 0.001:
                logger.warning(f"Calculated quantity {btc_quantity} is below minimum, using 0.001 BTC")
                btc_quantity = 0.001
            
            notional_value = btc_quantity * current_price
            
            logger.info(f"Trade Details:")
            logger.info(f"  USD Amount: ${usd_amount}")
            logger.info(f"  BTC Quantity: {btc_quantity} BTC")
            logger.info(f"  Actual Notional: ${notional_value:.2f}")
            logger.info(f"  Side: BUY (LONG)")
            logger.info(f"  Type: MARKET")
            logger.info(f"  Leverage: {config.trading.leverage}x")
            
            # Try to set leverage first
            try:
                logger.info(f"\nSetting leverage to {config.trading.leverage}x...")
                leverage_result = await client.set_leverage("BTCUSDT", config.trading.leverage)
                logger.success(f"✅ Leverage set: {leverage_result}")
            except Exception as e:
                logger.warning(f"Could not set leverage: {e}")
            
            # Place the order
            logger.info("\n🚀 Placing MARKET order...")
            order = await client.place_order(
                symbol="BTCUSDT",
                side="BUY",
                size=btc_quantity,
                order_type="MARKET",
                position_side="BOTH",
                reduce_only=False
            )
            
            logger.success("=" * 60)
            logger.success("✅ ORDER PLACED SUCCESSFULLY!")
            logger.success("=" * 60)
            logger.info(f"Order Response: {order}")
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ ORDER FAILED: {e}")
            logger.error("=" * 60)
            
            # Try to get more details about the error
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(test_small_trade())

