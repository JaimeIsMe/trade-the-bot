"""
Test script to fetch and display account data from Aster
"""
import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.aster_client import AsterClient
from loguru import logger


async def test_account_data():
    """Fetch account data from Aster API"""
    
    logger.info("=" * 60)
    logger.info("Testing Aster Account Data Retrieval")
    logger.info("=" * 60)
    
    async with AsterClient() as client:
        try:
            # Try to get account info
            logger.info("\n📊 Fetching account information...")
            try:
                account = await client.get_account()
                logger.success("✅ Account data retrieved!")
                logger.info(f"\nFull account response:")
                logger.info(json.dumps(account, indent=2))
                
                # Extract key metrics
                if account:
                    logger.info("\n" + "=" * 60)
                    logger.info("KEY ACCOUNT METRICS:")
                    logger.info("=" * 60)
                    
                    # Total wallet balance
                    total_balance = float(account.get('totalWalletBalance', 0))
                    logger.info(f"💰 Total Wallet Balance: ${total_balance:.2f} USDT")
                    
                    # Available balance
                    available_balance = float(account.get('availableBalance', 0))
                    logger.info(f"💵 Available Balance: ${available_balance:.2f} USDT")
                    
                    # Total unrealized PNL
                    total_unrealized_pnl = float(account.get('totalUnrealizedProfit', 0))
                    logger.info(f"{'📈' if total_unrealized_pnl >= 0 else '📉'} Unrealized PNL: ${total_unrealized_pnl:.4f} USDT")
                    
                    # Total margin balance
                    total_margin_balance = float(account.get('totalMarginBalance', 0))
                    logger.info(f"💼 Total Margin Balance: ${total_margin_balance:.2f} USDT")
                    
                    # Total position initial margin
                    total_position_margin = float(account.get('totalPositionInitialMargin', 0))
                    logger.info(f"🎯 Position Initial Margin: ${total_position_margin:.2f} USDT")
                    
                    # Margin ratio (if available)
                    if 'totalMaintMargin' in account and float(account['totalMaintMargin']) > 0:
                        margin_ratio = (float(account['totalMarginBalance']) / float(account['totalMaintMargin'])) * 100
                        logger.info(f"📊 Margin Ratio: {margin_ratio:.2f}%")
                    
                    # Positions
                    positions = account.get('positions', [])
                    open_positions = [p for p in positions if float(p.get('positionAmt', 0)) != 0]
                    logger.info(f"📍 Open Positions: {len(open_positions)}")
                    
                    if open_positions:
                        logger.info("\nPosition Details:")
                        for pos in open_positions:
                            symbol = pos.get('symbol')
                            size = float(pos.get('positionAmt', 0))
                            entry_price = float(pos.get('entryPrice', 0))
                            unrealized_pnl = float(pos.get('unrealizedProfit', 0))
                            logger.info(f"  • {symbol}: {size} BTC @ ${entry_price:.2f} | PNL: ${unrealized_pnl:.4f}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to get account data: {e}")
                logger.error(f"This might be a 405 error - let me try balance endpoint instead")
            
            # Try balance endpoint as alternative
            logger.info("\n💵 Fetching balance information...")
            try:
                balance = await client.get_balance()
                logger.success("✅ Balance data retrieved!")
                logger.info(f"\nBalance response:")
                logger.info(json.dumps(balance, indent=2))
            except Exception as e:
                logger.error(f"❌ Failed to get balance: {e}")
            
            logger.info("\n" + "=" * 60)
            logger.info("Test completed!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            logger.error(f"Full traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(test_account_data())

