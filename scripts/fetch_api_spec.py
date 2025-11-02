"""
Script to fetch and display Aster API specification
Helps understand the available endpoints and their usage
"""
import asyncio
import aiohttp
import json
import sys
sys.path.append('.')

from loguru import logger


async def fetch_api_spec():
    """Fetch API specification or public endpoints"""
    
    base_url = "https://api.hypereth.io/v1/aster"
    
    logger.info("Fetching Aster API information...")
    
    # Common public endpoints to try
    endpoints_to_try = [
        "/info",
        "/markets",
        "/instruments",
        "/tickers",
        "/time",
        "/status",
        "/health",
        "/ping",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_try:
            url = f"{base_url}{endpoint}"
            try:
                logger.info(f"Trying: {url}")
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.success(f"✓ {endpoint}: Success")
                        logger.info(f"Response: {json.dumps(data, indent=2)}")
                        print("\n" + "="*60 + "\n")
                    elif response.status == 401:
                        logger.info(f"✓ {endpoint}: Exists (requires auth)")
                    elif response.status == 404:
                        logger.debug(f"✗ {endpoint}: Not found")
                    else:
                        logger.info(f"? {endpoint}: Status {response.status}")
            except asyncio.TimeoutError:
                logger.debug(f"✗ {endpoint}: Timeout")
            except Exception as e:
                logger.debug(f"✗ {endpoint}: {e}")


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Aster API Specification Fetcher")
    logger.info("=" * 60)
    logger.info("This script will try to discover available API endpoints")
    logger.info("")
    
    await fetch_api_spec()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Next Steps:")
    logger.info("1. Review the GitHub API docs: https://github.com/asterdex/api-docs")
    logger.info("2. Check Hypereth docs: https://docs.hypereth.io/api-reference/introduction")
    logger.info("3. Update api/aster_client.py with correct endpoints")
    logger.info("4. Test with your API credentials")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

