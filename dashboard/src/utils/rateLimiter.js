/**
 * Rate Limiter Utility
 * Tracks API usage from response headers and automatically throttles requests
 */

let requestWeightUsed = 0;
let requestWeightLimit = null; // Will be detected from headers
let lastRequestTime = 0;
let consecutive429s = 0;

// Conservative estimate if we can't detect from headers
const ESTIMATED_WEIGHT_LIMIT = 1200; // Conservative estimate per minute
const WEIGHT_THRESHOLD = 0.8; // Slow down at 80% usage

/**
 * Extract request weight from response headers
 */
export const extractRequestWeight = (headers) => {
  // Look for X-MBX-USED-WEIGHT headers (format: X-MBX-USED-WEIGHT-1m, X-MBX-USED-WEIGHT-1s, etc.)
  const weightHeaders = Object.keys(headers).filter(key => 
    key.startsWith('x-mbx-used-weight') || key.startsWith('X-MBX-USED-WEIGHT')
  );
  
  if (weightHeaders.length > 0) {
    // Get the highest weight value across all intervals
    const weights = weightHeaders.map(key => {
      const value = headers[key] || headers[key.toLowerCase()];
      return parseInt(value, 10) || 0;
    });
    return Math.max(...weights);
  }
  
  return null;
};

/**
 * Extract request weight limit from headers (if available)
 */
export const extractWeightLimit = (headers) => {
  // Some APIs include limit in headers like X-MBX-WEIGHT-LIMIT-1m
  const limitHeaders = Object.keys(headers).filter(key => 
    key.includes('weight-limit') || key.includes('WEIGHT-LIMIT')
  );
  
  if (limitHeaders.length > 0) {
    const limit = limitHeaders.map(key => {
      const value = headers[key] || headers[key.toLowerCase()];
      return parseInt(value, 10) || 0;
    });
    return Math.max(...limit);
  }
  
  return null;
};

/**
 * Check if we should throttle based on current usage
 */
export const shouldThrottle = (headers) => {
  const weight = extractRequestWeight(headers);
  const limit = extractWeightLimit(headers) || ESTIMATED_WEIGHT_LIMIT;
  
  if (weight !== null) {
    requestWeightUsed = weight;
    requestWeightLimit = limit;
    
    // If we're above threshold, throttle
    if (weight / limit > WEIGHT_THRESHOLD) {
      console.warn(`High API usage detected: ${weight}/${limit} (${((weight/limit)*100).toFixed(1)}%)`);
      return true;
    }
  }
  
  return false;
};

/**
 * Handle 429 errors - track consecutive errors
 */
export const handle429Error = () => {
  consecutive429s += 1;
  console.warn(`Received 429 error (${consecutive429s} consecutive)`);
  return consecutive429s;
};

/**
 * Reset error count on successful request
 */
export const resetErrorCount = () => {
  consecutive429s = 0;
};

/**
 * Get recommended delay based on current usage
 */
export const getRecommendedDelay = () => {
  // If we have consecutive 429s, use exponential backoff
  if (consecutive429s > 0) {
    return Math.min(300000, 20000 * Math.pow(2, consecutive429s)); // Max 5 minutes, start at 20s
  }
  
  // If we're close to limit, add delay
  if (requestWeightLimit && requestWeightUsed / requestWeightLimit > WEIGHT_THRESHOLD) {
    const usageRatio = requestWeightUsed / requestWeightLimit;
    // Add extra delay proportional to usage
    return 20000 * (1 + usageRatio); // 20s * (1 + usage ratio)
  }
  
  return 60000; // Default: 60 seconds (conservative, especially when fetching trades for all bots)
};

/**
 * Get current usage stats
 */
export const getUsageStats = () => {
  return {
    weightUsed: requestWeightUsed,
    weightLimit: requestWeightLimit || ESTIMATED_WEIGHT_LIMIT,
    usagePercent: requestWeightLimit 
      ? ((requestWeightUsed / requestWeightLimit) * 100).toFixed(1)
      : 'unknown',
    consecutive429s,
    recommendedDelay: getRecommendedDelay()
  };
};

