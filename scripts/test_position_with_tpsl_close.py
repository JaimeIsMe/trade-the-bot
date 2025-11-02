"""
Test script to:
1. Open a position with TP/SL
2. Wait 60 seconds
3. Close the position AND cancel all open orders (TP/SL)
"""
import asyncio
import os
from dotenv import load_dotenv
from api.aster_client import AsterClient

load_dotenv()

async def main():
    print("\n" + "="*60)
    print("  TESTING POSITION CLOSE WITH TP/SL CLEANUP")
    print("="*60 + "\n")
    
    async with AsterClient() as client:
        symbol = "ASTERUSDT"
        
        # Step 1: Get current price
        print(f"[1/6] Fetching current {symbol} price...")
        ticker = await client.get_ticker(symbol)
        current_price = float(ticker['lastPrice'])
        print(f"      Current price: ${current_price}")
        
        # Step 2: Open a small LONG position
        print(f"\n[2/6] Opening LONG position...")
        size_usd = 5  # $5 position
        quantity = 6  # Hardcoded 6 ASTER to ensure above $5 notional
        
        order = await client.place_order(
            symbol=symbol,
            side="BUY",
            size=quantity,
            order_type="MARKET"
        )
        print(f"      Order placed: {order.get('orderId')}")
        print(f"      Size: {quantity} ASTER")
        
        # Wait a moment for order to fill
        await asyncio.sleep(2)
        
        # Step 3: Set Take Profit (2% above entry)
        print(f"\n[3/6] Setting Take Profit and Stop Loss...")
        tp_price = round(current_price * 1.02, 2)  # 2% profit
        sl_price = round(current_price * 0.98, 2)  # 2% loss
        
        tp_order = await client.set_take_profit(
            symbol, 
            tp_price, 
            quantity, 
            side="SELL"
        )
        print(f"      Take Profit set at ${tp_price} (Order ID: {tp_order.get('orderId')})")
        
        sl_order = await client.set_stop_loss(
            symbol, 
            sl_price, 
            quantity, 
            side="SELL"
        )
        print(f"      Stop Loss set at ${sl_price} (Order ID: {sl_order.get('orderId')})")
        
        # Step 4: Check open orders
        print(f"\n[4/6] Checking open orders...")
        open_orders = await client.get_open_orders(symbol)
        print(f"      Open orders: {len(open_orders)}")
        for order in open_orders:
            print(f"        - {order['type']} {order['side']} @ ${order.get('stopPrice', order.get('price', 'N/A'))} (ID: {order['orderId']})")
        
        # Step 5: Wait 60 seconds
        print(f"\n[5/6] Waiting 60 seconds before closing...")
        for i in range(60, 0, -10):
            print(f"      {i} seconds remaining...")
            await asyncio.sleep(10)
        
        # Step 6: Close position AND cancel all orders
        print(f"\n[6/6] Closing position and canceling TP/SL orders...")
        
        # Check if position still exists
        check_position = await client.get_position(symbol)
        position_amt = float(check_position.get('positionAmt', 0)) if check_position else 0
        
        if position_amt != 0:
            # Close the position
            close_order = await client.close_position(symbol)
            print(f"      Position closed: {close_order.get('orderId')}")
        else:
            print(f"      No position to close (may have hit TP/SL during wait)")
        
        # Cancel all open orders for this symbol
        cancel_result = await client.cancel_all_orders(symbol)
        print(f"      All orders canceled: {cancel_result}")
        
        # Verify cleanup
        await asyncio.sleep(2)
        open_orders_after = await client.get_open_orders(symbol)
        position = await client.get_position(symbol)
        position_size = float(position.get('positionAmt', 0)) if position else 0
        
        print(f"\n" + "="*60)
        print("  FINAL STATUS")
        print("="*60)
        print(f"  Position size: {position_size} {symbol.replace('USDT', '')}")
        print(f"  Open orders: {len(open_orders_after)}")
        
        if position_size == 0 and len(open_orders_after) == 0:
            print("\n  SUCCESS! Position and orders fully cleaned up!")
        else:
            print("\n  WARNING! Cleanup incomplete!")
            if position_size != 0:
                print(f"    - Position still open: {position_size}")
            if len(open_orders_after) > 0:
                print(f"    - {len(open_orders_after)} orders still open")
                for order in open_orders_after:
                    print(f"        {order['type']} {order['side']} @ ${order.get('stopPrice', order.get('price', 'N/A'))}")
        print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

