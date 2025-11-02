import React, { useState, useEffect, useRef } from 'react';
import CountUp from 'react-countup';

const TickerBar = () => {
  const [tickers, setTickers] = useState([]);
  const [imageErrors, setImageErrors] = useState({});
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  // Store last valid tickers to prevent flickering
  const lastValidTickersRef = useRef([]);

  // No HTTP polling fallback - WebSocket only to avoid API bans
  // Initial data will come from WebSocket when it connects

  // WebSocket connection for real-time updates
  useEffect(() => {
    // Determine WebSocket URL (use same logic as axios base URL)
    const isProduction = window.location.hostname === 'tradethebot.com';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // Use same base URL logic as axios
    let wsHost;
    if (isProduction) {
      wsHost = 'api.tradethebot.com';
    } else if (window.location.hostname === 'localhost') {
      // Local development - use the same port as axios (defaults to 8000)
      wsHost = 'localhost:8000';
    } else {
      // For other environments (like Cloudflare Tunnel), use current host
      wsHost = window.location.host;
    }
    
    const wsUrl = `${wsProtocol}//${wsHost}/ws/tickers`;
    console.log('🔌 Connecting to WebSocket:', wsUrl);

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ TickerBar WebSocket connected');
          setIsConnected(true);
          // Clear any reconnect timeout
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'tickers' && Array.isArray(data.data)) {
              // Merge new ticker data with existing tickers to prevent flickering
              // Aster may send partial updates (e.g., only 1-2 tickers), so we merge instead of replace
              setTickers(prevTickers => {
                const currentTickersMap = new Map(
                  prevTickers.map(t => [t.symbol, t])
                );
                
                // Update map with new ticker data
                if (data.data && data.data.length > 0) {
                  data.data.forEach(newTicker => {
                    if (newTicker && newTicker.symbol && newTicker.lastPrice && newTicker.lastPrice !== '0') {
                      currentTickersMap.set(newTicker.symbol, newTicker);
                    }
                  });
                }
                
                // Convert back to array and ensure we have all 5 symbols
                const mergedTickers = Array.from(currentTickersMap.values());
                
                // Store valid tickers in ref for fallback
                if (mergedTickers.length > 0) {
                  lastValidTickersRef.current = mergedTickers;
                }
                
                return mergedTickers;
              });
            }
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error, event.data);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ TickerBar WebSocket error:', error);
          setIsConnected(false);
        };

        ws.onclose = (event) => {
          console.log('🔌 TickerBar WebSocket disconnected', event.code, event.reason);
          setIsConnected(false);
          
          // Auto-reconnect WebSocket only (no HTTP polling fallback to avoid API bans)
          // Only reconnect if it wasn't a clean close
          if (event.code !== 1000) { // Not a normal closure
            reconnectTimeoutRef.current = setTimeout(() => {
              console.log('🔄 Reconnecting TickerBar WebSocket (no HTTP fallback)...');
              connectWebSocket();
            }, 5000);
          }
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('❌ Error creating WebSocket:', error);
        setIsConnected(false);
      }
    };

    // Connect on mount
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  // Create a map of symbols to display properties
  const symbolDisplay = {
    'ASTERUSDT': { name: 'ASTER', color: 'bg-orange-500', logo: '/aster_logo.png' },
    'BTCUSDT': { name: 'BTC', color: 'bg-orange-500', logo: '/btc-logo.svg' },
    'ETHUSDT': { name: 'ETH', color: 'bg-gray-600', logo: '/eth-logo.svg' },
    'SOLUSDT': { name: 'SOL', color: 'bg-purple-500', logo: '/sol-logo.svg' },
    'BNBUSDT': { name: 'BNB', color: 'bg-yellow-500', logo: '/bnb-logo.svg' },
  };

  // Show placeholder symbols even when loading or if WebSocket fails
  const symbolsToShow = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ASTERUSDT'];
  
  // Build display tickers - always show all 5 symbols, merge with any received data
  const tickersMap = new Map(
    [...tickers, ...lastValidTickersRef.current]
      .filter(t => t && t.symbol && t.lastPrice && t.lastPrice !== '0')
      .map(t => [t.symbol, t])
  );
  
  // Ensure we always show all 5 symbols
  const displayTickers = symbolsToShow.map(symbol => {
    // Use received ticker data if available, otherwise use placeholder
    const ticker = tickersMap.get(symbol);
    return ticker || { symbol, lastPrice: '0', priceChangePercent: '0' };
  });

  return (
    <div className="bg-black/60 backdrop-blur-md border-b border-blue-500/30 sticky top-[73px] sm:top-[89px] z-40 neon-border-blue">
      <div className="max-w-[1920px] mx-auto px-1 sm:px-3 lg:px-6 py-1 sm:py-2 lg:py-3">
        <div className="flex items-center justify-center">
          {/* Connection indicator */}
          {!isConnected && (
            <div className="absolute right-2 top-1/2 -translate-y-1/2">
              <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse" title="Reconnecting..."></div>
            </div>
          )}
          
          {/* Horizontal scrollable ticker bar for mobile */}
          <div className="flex items-center space-x-0.5 sm:space-x-1 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent pb-0.5 -mx-2 px-1 sm:mx-0 sm:px-0 w-full justify-center">
            {displayTickers.map((ticker, index) => {
              const display = symbolDisplay[ticker.symbol] || { name: ticker.symbol ? ticker.symbol.replace('USDT', '') : 'N/A', color: 'bg-gray-500' };
              
              return (
                <React.Fragment key={ticker.symbol}>
                  {index > 0 && <div className="w-px h-4 sm:h-6 lg:h-8 bg-slate-700/50 flex-shrink-0" />}
                  <div className="flex items-center space-x-0.5 sm:space-x-1.5 lg:space-x-3 px-1 sm:px-2 lg:px-4 py-0.5 sm:py-1.5 lg:py-2 hover:bg-slate-800/50 rounded-lg transition-colors whitespace-nowrap flex-shrink-0">
                    {/* Logo Image or Fallback Circle */}
                    {!imageErrors[ticker.symbol] ? (
                      <img 
                        src={display.logo} 
                        alt={display.name}
                        className="w-4 h-4 sm:w-6 sm:h-6 lg:w-8 lg:h-8 rounded-full object-cover flex-shrink-0"
                        onError={() => setImageErrors(prev => ({ ...prev, [ticker.symbol]: true }))}
                      />
                    ) : (
                      <div className={`w-4 h-4 sm:w-6 sm:h-6 lg:w-8 lg:h-8 rounded-full ${display.color} flex items-center justify-center text-white text-[10px] sm:text-xs font-bold flex-shrink-0`}>
                        {display.name[0]}
                      </div>
                    )}
                    
                    {/* Price - Animated */}
                    <span className="text-[10px] sm:text-xs lg:text-sm text-gray-300 tabular-nums flex-shrink-0">
                      $<CountUp 
                        end={parseFloat(ticker.lastPrice || 0)} 
                        decimals={ticker.symbol === 'ASTERUSDT' 
                          ? (parseFloat(ticker.lastPrice || 0) >= 1 ? 4 : 5)
                          : 0
                        }
                        duration={0.8}
                        preserveValue={true}
                        separator=","
                      />
                    </span>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TickerBar;
