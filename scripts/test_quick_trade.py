"""
Quick test trade - Open and close a small position
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.aster_client import AsterClient
from config.config import config

async def test_quick_trade():
    """Open and immediately close a small long position"""
    async with AsterClient() as client:
        symbol = "ASTERUSDT"
        
        print(f"\n{'='*50}")
        print(f"QUICK TRADE TEST - {symbol}")
        print(f"{'='*50}\n")
        
        # 1. Get current price
        print("Step 1: Getting current price...")
        ticker = await client.get_ticker(symbol)
        current_price = float(ticker.get('lastPrice', 0))
        print(f"[OK] Current price: ${current_price:.4f}\n")
        
        # 2. Open a small long position ($5 minimum)
        print("Step 2: Opening LONG position...")
        quantity = 6  # 6 ASTER = ~$5.87 notional (above $5 minimum)
        actual_notional = quantity * current_price
        
        print(f"  Size: {quantity} ASTER (~${actual_notional:.2f} notional)")
        
        try:
            order = await client.place_order(
                symbol=symbol,
                side="BUY",
                size=quantity,
                order_type="MARKET"
            )
            print(f"[OK] LONG position opened!")
            print(f"  Order ID: {order.get('orderId')}")
            print(f"  Status: {order.get('status')}\n")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # 3. Check position
            print("Step 3: Checking position...")
            account = await client.get_account()
            positions = account.get('positions', [])
            
            aster_pos = None
            for pos in positions:
                if pos.get('symbol') == symbol and float(pos.get('positionAmt', 0)) != 0:
                    aster_pos = pos
                    break
            
            if aster_pos:
                pos_amt = float(aster_pos.get('positionAmt', 0))
                entry_price = float(aster_pos.get('entryPrice', 0))
                pnl = float(aster_pos.get('unrealizedProfit', 0))
                
                print(f"[OK] Position found!")
                print(f"  Side: {'LONG' if pos_amt > 0 else 'SHORT'}")
                print(f"  Size: {abs(pos_amt):.4f}")
                print(f"  Entry: ${entry_price:.4f}")
                print(f"  PNL: ${pnl:.4f}\n")
                
                # 4. Close the position
                print("Step 4: Closing position...")
                close_order = await client.place_order(
                    symbol=symbol,
                    side="SELL",  # Opposite of LONG
                    size=abs(pos_amt),
                    order_type="MARKET",
                    reduce_only=True
                )
                print(f"[OK] Position CLOSED!")
                print(f"  Order ID: {close_order.get('orderId')}")
                print(f"  Status: {close_order.get('status')}\n")
                
            else:
                print("[X] No position found (order may have been rejected)\n")
                
        except Exception as e:
            print(f"[X] Error: {e}\n")
            return
        
        # 5. Final verification
        print("Step 5: Final verification...")
        await asyncio.sleep(1)
        account = await client.get_account()
        positions = account.get('positions', [])
        
        has_position = False
        for pos in positions:
            if pos.get('symbol') == symbol and float(pos.get('positionAmt', 0)) != 0:
                has_position = True
                break
        
        if not has_position:
            print(f"[OK] SUCCESS! Position closed, no open position on {symbol}\n")
        else:
            print(f"[WAIT] Position still open (may take a moment to clear)\n")
        
        print(f"{'='*50}")
        print("TEST COMPLETE")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    asyncio.run(test_quick_trade())

