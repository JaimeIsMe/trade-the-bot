"""Quick script to check open orders"""
import asyncio
from api.aster_client import AsterClient
import json

async def main():
    async with AsterClient() as client:
        # Get open orders for ASTERUSDT
        orders = await client.get_open_orders("ASTERUSDT")
        
        print("\n" + "="*60)
        print(f"OPEN ORDERS FOR ASTERUSDT: {len(orders)} orders")
        print("="*60)
        
        for i, order in enumerate(orders, 1):
            print(f"\nOrder {i}:")
            print(f"  Type: {order.get('type')}")
            print(f"  Side: {order.get('side')}")
            print(f"  Quantity: {order.get('origQty')}")
            print(f"  Price: {order.get('price', 'N/A')}")
            print(f"  Stop Price: {order.get('stopPrice', 'N/A')}")
            print(f"  Status: {order.get('status')}")
            
        print("\n" + "="*60)
        
        # Also check position
        account = await client.get_account()
        positions = account.get('positions', [])
        for pos in positions:
            if pos.get('symbol') == 'ASTERUSDT' and float(pos.get('positionAmt', 0)) != 0:
                print("\nCURRENT POSITION:")
                print(f"  Side: {'LONG' if float(pos.get('positionAmt', 0)) > 0 else 'SHORT'}")
                print(f"  Size: {abs(float(pos.get('positionAmt', 0)))}")
                print(f"  Entry: ${float(pos.get('entryPrice', 0)):.4f}")
                print(f"  P&L: ${float(pos.get('unrealizedProfit', 0)):+.4f}")
                print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

