"""
Shared Account Data Cache
Centralizes account data fetching to reduce API calls when running multiple bots
"""
import asyncio
import time
from typing import Dict, Any, Optional
from loguru import logger


class SharedAccountCache:
    """
    Singleton cache for account data shared across all bots
    Reduces API calls from N bots to 1 per update cycle
    """
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._account_data: Optional[Dict[str, Any]] = None
        self._last_update: float = 0
        self._cache_duration: int = 30  # Cache for 30 seconds
        self._aster_client = None
        self._initialized = True
        logger.info("✅ SharedAccountCache initialized")
    
    def set_client(self, client):
        """Set the Aster client to use for fetching"""
        self._aster_client = client
    
    async def get_account_data(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get account data - uses cache if fresh, otherwise fetches from API
        
        Args:
            force_refresh: Force a fresh API call even if cache is valid
            
        Returns:
            Account data dictionary or None if fetch fails
        """
        async with self._lock:
            current_time = time.time()
            cache_age = current_time - self._last_update
            
            # Use cache if it's fresh and not forced refresh
            if not force_refresh and self._account_data and cache_age < self._cache_duration:
                logger.debug(f"📦 Using cached account data (age: {cache_age:.1f}s)")
                return self._account_data
            
            # Fetch fresh data
            if not self._aster_client:
                logger.error("❌ No Aster client set for SharedAccountCache")
                return self._account_data  # Return stale data if available
            
            try:
                logger.debug("🔄 Fetching fresh account data (shared across all bots)")
                account = await self._aster_client.get_account()
                self._account_data = account
                self._last_update = current_time
                return account
            except Exception as e:
                logger.error(f"❌ Failed to fetch account data: {e}")
                # Return stale data if available, otherwise None
                return self._account_data
    
    def clear_cache(self):
        """Clear cached data"""
        self._account_data = None
        self._last_update = 0
        logger.info("🗑️ Account cache cleared")
    
    def get_cache_age(self) -> float:
        """Get age of cached data in seconds"""
        if self._last_update == 0:
            return float('inf')
        return time.time() - self._last_update









