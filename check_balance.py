#!/usr/bin/env python3
"""
Quick balance checker for Aster account
"""
import asyncio
import os
from dotenv import load_dotenv
from api.aster_client import AsterClient

async def main():
    load_dotenv()
    
    print("Checking Aster account balance...")
    
    try:
        client = AsterClient()
        await client.__aenter__()
        
        # Get balance
        balance_data = await client.get_balance()
        
        print("\nACCOUNT BALANCE:")
        if isinstance(balance_data, list) and len(balance_data) > 0:
            print("All balance entries:")
            for i, balance in enumerate(balance_data):
                print(f"  Asset {i+1}: {balance.get('asset', 'N/A')} - Balance: {balance.get('balance', 'N/A')}")
                print(f"    Available: {balance.get('availableBalance', 'N/A')}")
                print(f"    Margin Used: {balance.get('crossMarginUsed', 'N/A')}")
                print(f"    Unrealized P&L: {balance.get('crossUnPnl', 'N/A')}")
        else:
            print("No balance data available")
        
        # Get positions
        positions = await client.get_positions()
        print(f"\nPOSITIONS ({len(positions)} open):")
        for pos in positions:
            if float(pos.get('positionAmt', 0)) != 0:
                print(f"  {pos.get('symbol')}: {pos.get('positionAmt')} @ ${pos.get('entryPrice')} (P&L: ${pos.get('unrealizedProfit')})")
        
        await client.__aexit__(None, None, None)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
