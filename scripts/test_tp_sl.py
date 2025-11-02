"""
Test script to place a manual order with Take Profit and Stop Loss
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.aster_client import AsterClient
from config.config import config
from loguru import logger


async def test_tp_sl_order():
    """Place a small order with TP and SL"""
    
    logger.info("=" * 60)
    logger.info("Testing Order with Take Profit and Stop Loss")
    logger.info("=" * 60)
    
    async with AsterClient() as client:
        try:
            # Get current price
            logger.info("Fetching current BTC price...")
            ticker = await client.get_ticker("BTCUSDT")
            current_price = float(ticker.get('lastPrice', 0))
            logger.info(f"Current BTC Price: ${current_price:,.2f}")
            
            # Small test order
            btc_quantity = 0.001
            notional_value = btc_quantity * current_price
            
            # Calculate TP and SL levels (example: 2% TP, 1% SL)
            take_profit_price = current_price * 1.02  # 2% profit
            stop_loss_price = current_price * 0.99    # 1% loss
            
            logger.info(f"\nTrade Plan:")
            logger.info(f"  Side: BUY (LONG)")
            logger.info(f"  Quantity: {btc_quantity} BTC")
            logger.info(f"  Notional: ${notional_value:.2f}")
            logger.info(f"  Entry: ${current_price:.2f}")
            logger.info(f"  Take Profit: ${take_profit_price:.2f} (+2%)")
            logger.info(f"  Stop Loss: ${stop_loss_price:.2f} (-1%)")
            
            # Place the market order
            logger.info("\n🚀 Placing MARKET BUY order...")
            order = await client.place_order(
                symbol="BTCUSDT",
                side="BUY",
                size=btc_quantity,
                order_type="MARKET",
                position_side="BOTH",
                reduce_only=False
            )
            
            logger.success(f"✅ Order placed!")
            logger.info(f"Order ID: {order.get('orderId')}")
            logger.info(f"Status: {order.get('status')}")
            
            # Wait a moment for order to fill
            await asyncio.sleep(2)
            
            # Now try to set Take Profit (SELL to close a LONG position)
            logger.info(f"\n📈 Setting Take Profit at ${take_profit_price:.2f}...")
            try:
                tp_order = await client.set_take_profit(
                    symbol="BTCUSDT",
                    target_price=take_profit_price,
                    size=btc_quantity,
                    side="SELL"  # SELL to close a LONG position
                )
                logger.success(f"✅ Take Profit set!")
                logger.info(f"TP Order ID: {tp_order.get('orderId')}")
                logger.info(f"TP Order: {tp_order}")
            except Exception as e:
                logger.error(f"❌ Take Profit FAILED: {e}")
                logger.error(f"Full error: {str(e)}")
            
            # Now try to set Stop Loss (SELL to close a LONG position)
            logger.info(f"\n📉 Setting Stop Loss at ${stop_loss_price:.2f}...")
            try:
                sl_order = await client.set_stop_loss(
                    symbol="BTCUSDT",
                    stop_price=stop_loss_price,
                    size=btc_quantity,
                    side="SELL"  # SELL to close a LONG position
                )
                logger.success(f"✅ Stop Loss set!")
                logger.info(f"SL Order ID: {sl_order.get('orderId')}")
                logger.info(f"SL Order: {sl_order}")
            except Exception as e:
                logger.error(f"❌ Stop Loss FAILED: {e}")
                logger.error(f"Full error: {str(e)}")
            
            logger.info("\n" + "=" * 60)
            logger.info("Test completed! Check your Aster dashboard for the orders.")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(test_tp_sl_order())

