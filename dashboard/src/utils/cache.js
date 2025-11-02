/**
 * localStorage cache utility for API responses
 * Stores successful API responses with timestamps
 */

const CACHE_PREFIX = 'aster_dashboard_cache_';
const CACHE_EXPIRY_MS = 10 * 60 * 1000; // 10 minutes expiry (increased for better caching)

/**
 * Save data to cache with timestamp
 */
export const saveToCache = (key, data) => {
  try {
    const cacheData = {
      data,
      timestamp: Date.now()
    };
    localStorage.setItem(`${CACHE_PREFIX}${key}`, JSON.stringify(cacheData));
  } catch (error) {
    console.warn(`Failed to save to cache (${key}):`, error);
  }
};

/**
 * Get data from cache if it exists and hasn't expired
 */
export const getFromCache = (key) => {
  try {
    const cached = localStorage.getItem(`${CACHE_PREFIX}${key}`);
    if (!cached) return null;
    
    const cacheData = JSON.parse(cached);
    const age = Date.now() - cacheData.timestamp;
    
    // Return cached data if it's within expiry time
    if (age < CACHE_EXPIRY_MS) {
      return cacheData;
    } else {
      // Expired - remove it
      localStorage.removeItem(`${CACHE_PREFIX}${key}`);
      return null;
    }
  } catch (error) {
    console.warn(`Failed to read from cache (${key}):`, error);
    return null;
  }
};

/**
 * Get cache age in human-readable format
 */
export const getCacheAge = (timestamp) => {
  const ageMs = Date.now() - timestamp;
  const ageSeconds = Math.floor(ageMs / 1000);
  const ageMinutes = Math.floor(ageSeconds / 60);
  
  if (ageSeconds < 60) {
    return `${ageSeconds} second${ageSeconds !== 1 ? 's' : ''} ago`;
  } else if (ageMinutes < 60) {
    return `${ageMinutes} minute${ageMinutes !== 1 ? 's' : ''} ago`;
  } else {
    const hours = Math.floor(ageMinutes / 60);
    return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  }
};

/**
 * Clear all cache
 */
export const clearCache = () => {
  try {
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(CACHE_PREFIX)) {
        localStorage.removeItem(key);
      }
    });
  } catch (error) {
    console.warn('Failed to clear cache:', error);
  }
};




