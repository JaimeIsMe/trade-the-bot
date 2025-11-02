"""
Diagnostic script to understand Aster API authentication
"""
import asyncio
import aiohttp
import hmac
import hashlib
import time
import json
import sys
sys.path.append('.')

from config.config import config
from loguru import logger


async def test_public_endpoints():
    """Try public endpoints that don't need auth"""
    base_url = "https://api.hypereth.io/v1/aster"
    
    public_endpoints = [
        "/markets",
        "/tickers",
        "/time",
        "/ping",
        "/health",
        "/status",
    ]
    
    logger.info("Testing public endpoints (no auth required)...")
    
    async with aiohttp.ClientSession() as session:
        for endpoint in public_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url, timeout=5) as response:
                    logger.info(f"GET {endpoint}: Status {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        logger.success(f"✓ {endpoint} works!")
                        logger.info(f"Response: {json.dumps(data, indent=2)[:200]}...")
                        return True
            except Exception as e:
                logger.debug(f"✗ {endpoint}: {e}")
    
    return False


async def test_auth_headers():
    """Test different authentication header formats"""
    base_url = "https://api.hypereth.io/v1/aster"
    api_key = config.aster.api_key
    api_secret = config.aster.api_secret
    
    logger.info(f"\nTesting authentication with:")
    logger.info(f"API Key: {api_key[:10]}...")
    logger.info(f"API Secret: {api_secret[:10]}...")
    
    # Test 1: Our current method
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/markets"
    
    # Try different signature formats
    signatures = []
    
    # Format 1: timestamp + method + path
    message1 = f"{timestamp}{method}{path}"
    sig1 = hmac.new(api_secret.encode(), message1.encode(), hashlib.sha256).hexdigest()
    signatures.append(("Format 1 (timestamp+method+path)", {
        "X-ASTER-API-KEY": api_key,
        "X-ASTER-TIMESTAMP": timestamp,
        "X-ASTER-SIGNATURE": sig1,
    }))
    
    # Format 2: Just path
    sig2 = hmac.new(api_secret.encode(), path.encode(), hashlib.sha256).hexdigest()
    signatures.append(("Format 2 (just path)", {
        "X-API-KEY": api_key,
        "X-SIGNATURE": sig2,
    }))
    
    # Format 3: Hypereth specific
    sig3 = hmac.new(api_secret.encode(), message1.encode(), hashlib.sha256).hexdigest()
    signatures.append(("Format 3 (Hypereth)", {
        "api-key": api_key,
        "timestamp": timestamp,
        "signature": sig3,
    }))
    
    # Format 4: Authorization header
    sig4 = hmac.new(api_secret.encode(), message1.encode(), hashlib.sha256).hexdigest()
    signatures.append(("Format 4 (Authorization)", {
        "Authorization": f"Bearer {api_key}",
        "X-Timestamp": timestamp,
        "X-Signature": sig4,
    }))
    
    async with aiohttp.ClientSession() as session:
        for format_name, headers in signatures:
            url = f"{base_url}{path}"
            logger.info(f"\nTrying {format_name}...")
            logger.debug(f"Headers: {headers}")
            
            try:
                async with session.get(url, headers=headers, timeout=5) as response:
                    logger.info(f"Status: {response.status}")
                    if response.status == 200:
                        logger.success(f"✓ {format_name} WORKS!")
                        data = await response.json()
                        logger.info(f"Response: {json.dumps(data, indent=2)[:200]}")
                        return True
                    else:
                        body = await response.text()
                        logger.warning(f"Response: {body[:200]}")
            except Exception as e:
                logger.error(f"Error: {e}")


async def main():
    logger.info("=" * 60)
    logger.info("Aster API Authentication Diagnostic")
    logger.info("=" * 60)
    
    # First try public endpoints
    if await test_public_endpoints():
        logger.success("\n✓ Public endpoints work! API is reachable.")
    else:
        logger.warning("\n⚠ No public endpoints found. All require authentication.")
    
    # Then test auth
    logger.info("\n" + "=" * 60)
    logger.info("Testing Authentication Methods")
    logger.info("=" * 60)
    
    await test_auth_headers()
    
    logger.info("\n" + "=" * 60)
    logger.info("Next Steps:")
    logger.info("1. Check the GitHub API docs: https://github.com/asterdex/api-docs")
    logger.info("2. Look for authentication examples")
    logger.info("3. Update api/aster_client.py with correct auth method")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

