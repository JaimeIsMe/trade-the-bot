import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, DollarSign, Target, Zap } from 'lucide-react';
import ChartsContainer from './components/ChartsContainer';
import TickerBar from './components/TickerBar';
import BotTabs from './components/BotTabs';
import ModelInfo from './components/ModelInfo';
import AssetsInfo from './components/AssetsInfo';
import Info from './components/Info';
import { saveToCache, getFromCache } from './utils/cache';
// Rate limiter no longer needed with WebSocket-only approach
// import { shouldThrottle, handle429Error, resetErrorCount, getRecommendedDelay, getUsageStats } from './utils/rateLimiter';

// Configure axios base URL for production (use Cloudflare Tunnel URL when deployed)
// In production, API is at api.tradethebot.com
const isProduction = window.location.hostname === 'tradethebot.com';
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || (isProduction ? 'https://api.tradethebot.com' : '');

// Simplified error handling - no complex rate limiting needed with WebSocket approach
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 429 || error.response.status === 418) {
        console.error('🚫 Rate limited or banned. Using cached data and WebSocket updates.');
      }
    }
    return Promise.reject(error);
  }
);

function App() {
  const [status, setStatus] = useState('offline');
  const [portfolio, setPortfolio] = useState({});
  const [bots, setBots] = useState([]);
  const [selectedBot, setSelectedBot] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');
  
  // Use ref to track last valid portfolio to prevent showing $0 on API errors
  const lastValidPortfolioRef = useRef(null);
  
  // Use refs to track last valid bot data to prevent showing zeros on API errors
  const lastValidBotPerformanceRef = useRef(null);
  const lastValidBotTradesRef = useRef(null);
  
  // Bot-specific state
  const [botPerformance, setBotPerformance] = useState({});
  const [botDecisions, setBotDecisions] = useState([]);
  const [botTrades, setBotTrades] = useState([]);
  const [botPositions, setBotPositions] = useState([]);
  const [botCandles, setBotCandles] = useState([]);
  const [overallPnL, setOverallPnL] = useState(0);
  
  // Store trades for all bots (for combined chart)
  const [allBotsTrades, setAllBotsTrades] = useState({}); // { symbol: trades[] }
  const [isInitialLoad, setIsInitialLoad] = useState(true); // Track if we've done initial data load
  
  // WebSocket refs for account data and decisions
  const accountWsRef = useRef(null);
  const reconnectAccountWsTimeoutRef = useRef(null);
  const decisionsWsRef = useRef(null);
  const reconnectDecisionsWsTimeoutRef = useRef(null);

  // Fetch decisions for all bots and combine them
  const fetchAllDecisions = useCallback(async (botList) => {
    console.log('⚠️ HTTP polling disabled - decisions via WebSocket only');
    return; // Skip all HTTP calls - decisions come via WebSocket
    
    if (!botList || botList.length === 0) return;
    
    try {
      // Fetch decisions for all bots in parallel
      const decisionPromises = botList.map(bot => 
        axios.get(`/api/decisions?symbol=${bot.symbol}&limit=100`).catch(err => {
          console.error(`Error fetching decisions for ${bot.symbol}:`, err);
          return null;
        })
      );
      
      const decisionResponses = await Promise.all(decisionPromises);
      
      // Combine all decisions from all bots
      const allDecisions = [];
      decisionResponses.forEach((res, index) => {
        if (res?.data && Array.isArray(res.data)) {
          const botSymbol = botList[index].symbol;
          // Add symbol info to each decision for display
          res.data.forEach(decision => {
            allDecisions.push({
              ...decision,
              symbol: botSymbol,
              asset: botSymbol.replace('USDT', '')
            });
          });
        }
      });
      
      // Sort by timestamp (newest first) and limit to 100
      allDecisions.sort((a, b) => {
        const timeA = new Date(a.timestamp || a.created_at || 0).getTime();
        const timeB = new Date(b.timestamp || b.created_at || 0).getTime();
        return timeB - timeA; // Newest first
      });
      
      // Limit to 100 most recent
      setBotDecisions(allDecisions.slice(0, 100));
    } catch (error) {
      console.error('Error fetching all decisions:', error);
    }
  }, []);

  // Fetch initial historical data once on mount
  useEffect(() => {
    const loadInitialData = async () => {
      console.log('📥 Loading initial data (ONCE on mount)...');
      
      // Load portfolio from cache first
      const cachedPortfolio = getFromCache('portfolio');
      if (cachedPortfolio) {
        setPortfolio(cachedPortfolio.data);
        lastValidPortfolioRef.current = cachedPortfolio.data;
      }
      
      // Load bots from cache
      const cachedBots = getFromCache('bots');
      if (cachedBots) {
        const cachedBotsList = cachedBots.data.bots || [];
        // Sort bots to match TickerBar order: BTC, ETH, BNB, SOL, ASTER
        const botOrder = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ASTERUSDT'];
        cachedBotsList.sort((a, b) => {
          const aIndex = botOrder.indexOf(a.symbol || a.name);
          const bIndex = botOrder.indexOf(b.symbol || b.name);
          if (aIndex === -1) return 1;
          if (bIndex === -1) return -1;
          return aIndex - bIndex;
        });
        setBots(cachedBotsList);
        if (cachedBotsList.length > 0) {
          setSelectedBot(cachedBotsList[0]);
          
          // Load trades for all bots from cache
          const allTradesFromCache = {};
          cachedBots.data.bots.forEach(bot => {
            const cachedTrades = getFromCache(`trades_${bot.symbol}`);
            if (cachedTrades && cachedTrades.data) {
              allTradesFromCache[bot.symbol] = cachedTrades.data;
            }
          });
          
          // Set allBotsTrades with cached data
          if (Object.keys(allTradesFromCache).length > 0) {
            setAllBotsTrades(allTradesFromCache);
            console.log('✅ Loaded cached trades for', Object.keys(allTradesFromCache).length, 'bots');
          }
        }
      }
      
      // ⚠️ Fetch initial data ONCE - backend has aggressive caching now
      try {
        console.log('📥 Fetching initial bot list and portfolio...');
        
        // Fetch bots list (this triggers backend cache population)
        const botsRes = await axios.get('/api/bots').catch(() => null);
        if (botsRes?.data?.bots) {
          const botsList = botsRes.data.bots || [];
          const botOrder = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ASTERUSDT'];
          botsList.sort((a, b) => {
            const aIndex = botOrder.indexOf(a.symbol || a.name);
            const bIndex = botOrder.indexOf(b.symbol || b.name);
            if (aIndex === -1) return 1;
            if (bIndex === -1) return -1;
            return aIndex - bIndex;
          });
          setBots(botsList);
          saveToCache('bots', { bots: botsList });
          
          if (botsList.length > 0) {
            setSelectedBot(botsList[0]);
            console.log('✅ Loaded', botsList.length, 'bots');
            
            // Fetch trades for ALL bots (for combined chart)
            console.log('📥 Fetching trades for all bots...');
            const tradesPromises = botsList.map(bot => 
              axios.get(`/api/trades?symbol=${bot.symbol}&limit=500`).catch(() => null)
            );
            const tradesResponses = await Promise.all(tradesPromises);
            
            const allTrades = {};
            tradesResponses.forEach((res, index) => {
              if (res?.data && Array.isArray(res.data)) {
                const symbol = botsList[index].symbol;
                allTrades[symbol] = res.data;
                saveToCache(`trades_${symbol}`, res.data);
              }
            });
            
            if (Object.keys(allTrades).length > 0) {
              setAllBotsTrades(allTrades);
              console.log('✅ Loaded trades for', Object.keys(allTrades).length, 'bots');
            }
            
            // Fetch decisions for all bots initially (WebSocket only sends NEW ones)
            console.log('📥 Fetching initial decisions for all bots...');
            const decisionPromises = botsList.map(bot => 
              axios.get(`/api/decisions?symbol=${bot.symbol}&limit=100`).catch(() => null)
            );
            const decisionResponses = await Promise.all(decisionPromises);
            
            const allDecisions = [];
            decisionResponses.forEach((res, index) => {
              if (res?.data && Array.isArray(res.data)) {
                const symbol = botsList[index].symbol;
                res.data.forEach(decision => {
                  allDecisions.push({
                    ...decision,
                    symbol: symbol,
                    asset: symbol.replace('USDT', '')
                  });
                });
              }
            });
            
            // Sort by timestamp (newest first) and limit to 100
            allDecisions.sort((a, b) => {
              const timeA = new Date(a.timestamp || a.created_at || 0).getTime();
              const timeB = new Date(b.timestamp || b.created_at || 0).getTime();
              return timeB - timeA;
            });
            
            setBotDecisions(allDecisions.slice(0, 100));
            console.log('✅ Loaded', allDecisions.length, 'decisions');
          }
        }
        
        // Fetch portfolio (cached for 2 min on backend)
        const portfolioRes = await axios.get('/api/portfolio/summary').catch(() => null);
        if (portfolioRes?.data) {
          setPortfolio(portfolioRes.data);
          saveToCache('portfolio', portfolioRes.data);
          lastValidPortfolioRef.current = portfolioRes.data;
        }
        
        console.log('✅ Initial data loaded - backend will cache for 2-3 minutes');
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
      
      setIsInitialLoad(false);
    };
    
    loadInitialData();
  }, [fetchAllDecisions]);

  // WebSocket connection for real-time account updates
  useEffect(() => {
    // Determine WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsHost;
    if (isProduction) {
      wsHost = 'api.tradethebot.com';
    } else if (window.location.hostname === 'localhost') {
      wsHost = 'localhost:8000';
    } else {
      wsHost = window.location.host;
    }
    
    const wsUrl = `${wsProtocol}//${wsHost}/ws/account`;
    console.log('🔌 Connecting to account WebSocket:', wsUrl);

    const connectAccountWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ Account WebSocket connected');
          if (reconnectAccountWsTimeoutRef.current) {
            clearTimeout(reconnectAccountWsTimeoutRef.current);
            reconnectAccountWsTimeoutRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'account_update') {
              // Update portfolio with real-time balance and positions
              const updateData = data.data;
              
              setPortfolio(prev => {
                const updated = {
                  ...prev,
                  total_balance: updateData.totalBalance || prev.total_balance || 0,
                  cash_balance: updateData.balances?.USDT?.walletBalance || prev.cash_balance || 0,
                  in_positions: updateData.totalBalance - (updateData.balances?.USDT?.walletBalance || 0) || prev.in_positions || 0,
                  unrealized_pnl: updateData.totalUnrealizedPnl || prev.unrealized_pnl || 0
                };
                
                // Store as last valid
                lastValidPortfolioRef.current = updated;
                saveToCache('portfolio', updated);
                
                return updated;
              });
              
              // Update overall P&L if we have positions
              if (updateData.positions && updateData.positions.length > 0) {
                const totalRealized = updateData.positions.reduce((sum, pos) => sum + (pos.realizedPnl || 0), 0);
                setOverallPnL(totalRealized);
              }
              
              console.log('📊 Account updated:', {
                balance: updateData.totalBalance,
                positions: updateData.positions?.length || 0,
                unrealizedPnl: updateData.totalUnrealizedPnl
              });
            }
            else if (data.type === 'trade_execution') {
              // New trade executed - refresh trade history for that symbol immediately!
              const tradeData = data.data;
              const symbol = tradeData.symbol;
              console.log('🎯 Trade executed:', tradeData);
              
              // Refresh trades and performance for this specific symbol immediately
              const refreshTradesForSymbol = async (symbolToRefresh) => {
                try {
              // ⚠️ HTTP polling disabled - skip trade refresh after WebSocket event
              console.log('⚠️ Trade executed but HTTP polling disabled - using cached data');
              return; // Skip all HTTP calls
                  
                  // Fetch both trades and performance in parallel
                  const [tradesRes, perfRes] = await Promise.all([
                    axios.get(`/api/trades?symbol=${symbolToRefresh}&limit=500`).catch(() => null),
                    axios.get(`/api/performance?symbol=${symbolToRefresh}`).catch(() => null)
                  ]);
                  
                  // Update trades
                  if (tradesRes?.data && Array.isArray(tradesRes.data) && tradesRes.data.length > 0) {
                    // Update allBotsTrades with new data
                    setAllBotsTrades(prev => ({
                      ...prev,
                      [symbolToRefresh]: tradesRes.data
                    }));
                    
                    // If this is the selected bot, also update botTrades
                    if (selectedBot && selectedBot.symbol === symbolToRefresh) {
                      setBotTrades(tradesRes.data);
                      lastValidBotTradesRef.current = tradesRes.data;
                      saveToCache(`trades_${symbolToRefresh}`, tradesRes.data);
                    }
                    
                    console.log(`✅ Refreshed trades for ${symbolToRefresh} after trade execution`);
                  }
                  
                  // Update performance if available
                  if (perfRes?.data) {
                    if (selectedBot && selectedBot.symbol === symbolToRefresh) {
                      setBotPerformance(perfRes.data);
                      lastValidBotPerformanceRef.current = perfRes.data;
                      saveToCache(`performance_${symbolToRefresh}`, perfRes.data);
                    }
                    
                    // Update overall P&L
                    setOverallPnL(prev => {
                      // Recalculate total - this is approximate but good enough
                      return prev + (tradeData.realizedProfit || 0);
                    });
                  }
                } catch (error) {
                  console.error(`Error refreshing data for ${symbolToRefresh}:`, error);
                }
              };
              
              refreshTradesForSymbol(symbol);
            }
            else if (data.type === 'error') {
              console.error('❌ Account WebSocket error:', data.message);
            }
          } catch (error) {
            console.error('❌ Error parsing account WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ Account WebSocket error:', error);
        };

        ws.onclose = (event) => {
          console.log('🔌 Account WebSocket disconnected', event.code);
          
          // Auto-reconnect WebSocket only (no HTTP polling fallback to avoid API bans)
          // Only reconnect if it wasn't a clean close
          if (event.code !== 1000) {
            reconnectAccountWsTimeoutRef.current = setTimeout(() => {
              console.log('🔄 Reconnecting account WebSocket (no HTTP fallback)...');
              connectAccountWebSocket();
            }, 5000);
          }
        };

        accountWsRef.current = ws;
      } catch (error) {
        console.error('❌ Error creating account WebSocket:', error);
      }
    };

    // Connect on mount
    connectAccountWebSocket();

    // Cleanup on unmount
    return () => {
      if (accountWsRef.current) {
        accountWsRef.current.close(1000, 'Component unmounting');
      }
      if (reconnectAccountWsTimeoutRef.current) {
        clearTimeout(reconnectAccountWsTimeoutRef.current);
      }
    };
  }, []); // Only connect once on mount - account data is global, not bot-specific
  
  // WebSocket connection for real-time AI decisions
  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsHost;
    if (isProduction) {
      wsHost = 'api.tradethebot.com';
    } else if (window.location.hostname === 'localhost') {
      wsHost = 'localhost:8000';
    } else {
      wsHost = window.location.host;
    }
    
    const wsUrl = `${wsProtocol}//${wsHost}/ws/decisions`;
    console.log('🔌 Connecting to decisions WebSocket:', wsUrl);
    
    const connectDecisionsWebSocket = () => {
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          console.log('✅ Decisions WebSocket connected');
          if (reconnectDecisionsWsTimeoutRef.current) {
            clearTimeout(reconnectDecisionsWsTimeoutRef.current);
            reconnectDecisionsWsTimeoutRef.current = null;
          }
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'new_decisions') {
              // Prepend new decisions to existing ones
              setBotDecisions(prev => {
                const combined = [...data.data, ...prev];
                // Remove duplicates based on timestamp
                const unique = combined.filter((decision, index, self) =>
                  index === self.findIndex(d => d.timestamp === decision.timestamp)
                );
                // Keep only most recent 100
                return unique.slice(0, 100);
              });
              console.log('🆕 Received new decisions:', data.data.length);
            }
          } catch (error) {
            console.error('❌ Error parsing decisions WebSocket message:', error);
          }
        };
        
        ws.onerror = (error) => {
          console.error('❌ Decisions WebSocket error:', error);
        };
        
        ws.onclose = (event) => {
          console.log('🔌 Decisions WebSocket disconnected', event.code);
          
          // Auto-reconnect (no HTTP fallback)
          if (event.code !== 1000) {
            reconnectDecisionsWsTimeoutRef.current = setTimeout(() => {
              console.log('🔄 Reconnecting decisions WebSocket...');
              connectDecisionsWebSocket();
            }, 5000);
          }
        };
        
        decisionsWsRef.current = ws;
      } catch (error) {
        console.error('❌ Error creating decisions WebSocket:', error);
      }
    };
    
    connectDecisionsWebSocket();
    
    return () => {
      if (decisionsWsRef.current) {
        decisionsWsRef.current.close(1000, 'Component unmounting');
      }
      if (reconnectDecisionsWsTimeoutRef.current) {
        clearTimeout(reconnectDecisionsWsTimeoutRef.current);
      }
    };
  }, []);
  
  // Fetch bot-specific data when user switches between bots
  const fetchBotData = useCallback(async (bot) => {
    if (!bot || !bot.symbol) return;
    
    const symbol = bot.symbol;
    console.log(`📥 Loading data for ${symbol}...`);
    
    // Try cache first
      const cachedPerf = getFromCache(`performance_${symbol}`);
    const cachedTrades = getFromCache(`trades_${symbol}`);
    
      if (cachedPerf) {
        setBotPerformance(cachedPerf.data);
        lastValidBotPerformanceRef.current = cachedPerf.data;
      }
      
      if (cachedTrades) {
        setBotTrades(cachedTrades.data);
        lastValidBotTradesRef.current = cachedTrades.data;
      }
      
    // Fetch fresh data (backend will serve from cache if within 2-3 min)
    try {
      // Fetch performance (backend cached for 2 min)
      const perfRes = await axios.get(`/api/performance?symbol=${symbol}`).catch(err => {
        console.error(`Error fetching performance for ${symbol}:`, err);
        return null;
      });
      if (perfRes?.data) {
        // Only update if we got valid data (has trades or meaningful values)
        // If API returns all zeros but we have previous valid data, preserve it
        const hasValidData = perfRes.data.total_trades > 0 || 
                            perfRes.data.realized_pnl !== 0 || 
                            perfRes.data.total_pnl !== 0 ||
                            lastValidBotPerformanceRef.current === null;
        
        if (hasValidData) {
          setBotPerformance(perfRes.data);
          lastValidBotPerformanceRef.current = perfRes.data;
          // Save to cache
          saveToCache(`performance_${symbol}`, perfRes.data);
        } else if (lastValidBotPerformanceRef.current) {
          // API returned zeros but we have previous valid data - preserve it
          setBotPerformance(lastValidBotPerformanceRef.current);
        }
      }
    } catch (error) {
      console.error(`Error fetching performance for ${symbol}:`, error);
      // Try to load from cache on error
      const cached = getFromCache(`performance_${symbol}`);
      if (cached) {
        setBotPerformance(cached.data);
        lastValidBotPerformanceRef.current = cached.data;
      } else if (lastValidBotPerformanceRef.current) {
        // Preserve last valid performance on error
        setBotPerformance(lastValidBotPerformanceRef.current);
      }
    }

    // Decisions are now fetched for all bots together - see fetchAllDecisions

    try {
      const tradesRes = await axios.get(`/api/trades?symbol=${symbol}&limit=500`).catch(err => {
        console.error(`Error fetching trades for ${symbol}:`, err);
        return null;
      });
      if (tradesRes?.data) {
        // Only update if we got trades or if we don't have previous data
        const hasTrades = Array.isArray(tradesRes.data) && tradesRes.data.length > 0;
        
        if (hasTrades || lastValidBotTradesRef.current === null) {
          setBotTrades(tradesRes.data);
          lastValidBotTradesRef.current = tradesRes.data;
          // Save to cache
          saveToCache(`trades_${symbol}`, tradesRes.data);
          
          // Update allBotsTrades for combined chart
          setAllBotsTrades(prev => ({
            ...prev,
            [symbol]: tradesRes.data
          }));
        } else if (lastValidBotTradesRef.current) {
          // API returned empty but we have previous valid trades - preserve them
          setBotTrades(lastValidBotTradesRef.current);
        }
      }
    } catch (error) {
      console.error(`Error fetching trades for ${symbol}:`, error);
      // Try to load from cache on error
      const cached = getFromCache(`trades_${symbol}`);
      if (cached) {
        setBotTrades(cached.data);
        lastValidBotTradesRef.current = cached.data;
      } else if (lastValidBotTradesRef.current) {
        // Preserve last valid trades on error
        setBotTrades(lastValidBotTradesRef.current);
      }
    }

    try {
      const positionsRes = await axios.get('/api/positions').catch(err => {
        console.error(`Error fetching positions:`, err);
        return null;
      });
      if (positionsRes?.data) {
        setBotPositions(positionsRes.data.filter(p => p.symbol === symbol));
      }
    } catch (error) {
      console.error(`Error fetching positions:`, error);
    }

    // ⚠️ KLINES FETCHING DISABLED to prevent API bans
    // Chart data is now cached on the backend for 60 seconds minimum
    // and rate-limited to max 10 requests per minute per symbol
    console.log(`⚠️ Klines fetching disabled for ${symbol} - using backend cache only`);
  }, []);

  // Update bot-specific data when selected bot changes
  useEffect(() => {
    if (selectedBot) {
      // Reset refs when switching bots to avoid showing previous bot's data
      lastValidBotPerformanceRef.current = null;
      lastValidBotTradesRef.current = null;
      
      // Load cached data for this bot first
      const cachedPerformance = getFromCache(`performance_${selectedBot.symbol}`);
      if (cachedPerformance) {
        setBotPerformance(cachedPerformance.data);
      }
      
      const cachedTrades = getFromCache(`trades_${selectedBot.symbol}`);
      if (cachedTrades) {
        setBotTrades(cachedTrades.data);
      }
      
      // Fetch bot data (backend will serve from cache if recent)
      fetchBotData(selectedBot);
    }
  }, [selectedBot?.name]);

  // fetchData removed - no longer needed with WebSocket-only approach
  // Historical data is fetched once on mount, real-time updates come via WebSocket

  // NO POLLING LOOP - We rely on:
  // 1. Initial data load (once on mount) for historical data
  // 2. WebSocket for all real-time updates (account, prices, trade executions)
  // This eliminates 95% of API calls and prevents bans

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(value || 0);
  };

  const formatPercent = (value) => {
    return `${((value || 0) * 100).toFixed(2)}%`;
  };

  // Calculate combined stats from all bots' trades
  const combinedStats = useMemo(() => {
    let totalTrades = 0;
    let totalWins = 0;
    let totalLosses = 0;
    let biggestWin = 0;
    let biggestLoss = 0;
    
    // Aggregate stats from all bots' trades
    Object.values(allBotsTrades).forEach(trades => {
      if (Array.isArray(trades)) {
        trades.forEach(trade => {
          const pnl = parseFloat(trade.pnl || trade.realizedProfit || 0);
          totalTrades++;
          if (pnl > 0) {
            totalWins++;
            biggestWin = Math.max(biggestWin, pnl);
          } else if (pnl < 0) {
            totalLosses++;
            biggestLoss = Math.min(biggestLoss, pnl);
          }
        });
      }
    });
    
    const winRate = totalTrades > 0 ? totalWins / totalTrades : 0;
    
    return {
      totalTrades,
      totalWins,
      totalLosses,
      winRate,
      biggestWin,
      biggestLoss
    };
  }, [allBotsTrades]);

  const getTotalTrades = () => {
    return combinedStats.totalTrades || 0;
  };

  const getTotalWinRate = () => {
    return combinedStats.winRate || 0;
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Fintech Background */}
      <div className="absolute inset-0 -z-10 bg-fintech-gradient" />
      <div className="absolute inset-0 -z-10 bg-grid opacity-60" />
      
      {/* Neon animated gradient orbs (blue, purple, teal only) */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl -z-10 bg-orb" style={{ animationDelay: '0s', boxShadow: '0 0 100px rgba(59, 130, 246, 0.4)' }} />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl -z-10 bg-orb" style={{ animationDelay: '7s', boxShadow: '0 0 100px rgba(168, 85, 247, 0.4)' }} />
      <div className="absolute top-1/2 right-0 w-80 h-80 bg-cyan-500/15 rounded-full blur-3xl -z-10 bg-orb" style={{ animationDelay: '14s', boxShadow: '0 0 100px rgba(6, 182, 212, 0.4)' }} />
      <div className="absolute bottom-1/4 left-0 w-72 h-72 bg-cyan-500/15 rounded-full blur-3xl -z-10 bg-orb" style={{ animationDelay: '10s', boxShadow: '0 0 100px rgba(6, 182, 212, 0.4)' }} />
      
      {/* Header */}
      <header className="bg-black/60 backdrop-blur-md border-b border-blue-500/30 sticky top-0 z-50 neon-border-blue">
        <div className="max-w-[1920px] mx-auto px-3 sm:px-4 lg:px-6 py-2 sm:py-3 lg:py-4">
          <div className="flex flex-col items-center space-y-2 sm:space-y-3">
            {/* Centered Title */}
            <div className="flex flex-col items-center">
              <h1 className="text-2xl sm:text-4xl lg:text-5xl font-bold text-blue-400 neon-text-blue neon-flicker">Trade The Bot</h1>
              <span className="text-xs sm:text-sm text-gray-400">AI-Powered Multi-Asset Dashboard</span>
            </div>
            
            {/* Navigation Links */}
            <div className="flex items-center space-x-3 sm:space-x-4">
              <button 
                onClick={() => setCurrentPage('dashboard')}
                className={`text-xs sm:text-sm transition-all py-1 px-2 rounded ${
                  currentPage === 'dashboard' ? 'text-white font-semibold bg-blue-600/30 border border-blue-500/50 neon-glow-blue neon-text-blue' : 'text-gray-400 hover:text-white hover:bg-blue-500/10'
                }`}
              >
                Dashboard
              </button>
              <span className="text-gray-600">|</span>
              <button 
                onClick={() => setCurrentPage('model')}
                className={`text-xs sm:text-sm transition-all py-1 px-2 rounded ${
                  currentPage === 'model' ? 'text-white font-semibold bg-blue-600/30 border border-blue-500/50 neon-glow-blue neon-text-blue' : 'text-gray-400 hover:text-white hover:bg-blue-500/10'
                }`}
              >
                Model
              </button>
              <span className="text-gray-600">|</span>
              <button 
                onClick={() => setCurrentPage('assets')}
                className={`text-xs sm:text-sm transition-all py-1 px-2 rounded ${
                  currentPage === 'assets' ? 'text-white font-semibold bg-blue-600/30 border border-blue-500/50 neon-glow-blue neon-text-blue' : 'text-gray-400 hover:text-white hover:bg-blue-500/10'
                }`}
              >
                Assets
              </button>
              <span className="text-gray-600">|</span>
              <button 
                onClick={() => setCurrentPage('info')}
                className={`text-xs sm:text-sm transition-all py-1 px-2 rounded ${
                  currentPage === 'info' ? 'text-white font-semibold bg-blue-600/30 border border-blue-500/50 neon-glow-blue neon-text-blue' : 'text-gray-400 hover:text-white hover:bg-blue-500/10'
                }`}
              >
                Info
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Ticker Bar - Hidden on Model, Assets, and Info pages */}
      {currentPage !== 'model' && currentPage !== 'assets' && currentPage !== 'info' && <TickerBar />}

      {/* Main Content */}
      <div className="max-w-[1920px] mx-auto px-3 sm:px-4 lg:px-6 pb-4 sm:pb-6">
        {currentPage === 'model' ? (
          <ModelInfo />
        ) : currentPage === 'assets' ? (
          <AssetsInfo />
        ) : currentPage === 'info' ? (
          <Info />
        ) : selectedBot ? (
          <>
            {/* Main Grid with Stats, Charts and AI Decisions */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6">
              {/* Empty spacer on left to center content */}
              <div className="lg:col-span-1 hidden lg:block"></div>
              
              {/* Stats Cards Row - Spans same width as Charts + AI Decisions */}
              <div className="lg:col-span-10 mb-4 sm:mb-6 lg:mb-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
                  <StatCard
                    label="Total Balance"
                    value={formatCurrency(portfolio.total_balance)}
                    icon={<DollarSign className="w-4 h-4" />}
                    color="blue"
                    breakdown={[
                      { label: 'Cash', value: formatCurrency(portfolio.available_balance || 0) },
                      { label: 'In Positions', value: formatCurrency(portfolio.total_exposure || 0) }
                    ]}
                  />
                  <StatCard
                    label="Open P&L"
                    value={formatCurrency(portfolio.total_unrealized_pnl)}
                    icon={<TrendingUp className="w-4 h-4" />}
                    color={portfolio.total_unrealized_pnl >= 0 ? 'cyan' : 'purple'}
                  />
                  <StatCard
                    label="Total P&L"
                    value={formatCurrency(overallPnL + portfolio.total_unrealized_pnl)}
                    icon={<Activity className="w-4 h-4" />}
                    color={(overallPnL + portfolio.total_unrealized_pnl) >= 0 ? 'cyan' : 'purple'}
                  />
                  <StatCard
                    label="Total Trades"
                    value={getTotalTrades()}
                    icon={<Activity className="w-4 h-4" />}
                    color="cyan"
                  />
                  <StatCard
                    label="Win Rate"
                    value={formatPercent(getTotalWinRate())}
                    icon={<Target className="w-4 h-4" />}
                    color="cyan"
                  />
                </div>
              </div>
              
              {/* Empty spacer on right to center content */}
              <div className="lg:col-span-1 hidden lg:block"></div>
              
              {/* Empty spacer on left to center content */}
              <div className="lg:col-span-1 hidden lg:block"></div>
              
              {/* Center Column - Tabbed Charts */}
              <div className="lg:col-span-7">
                <div className="bg-black/40 backdrop-blur-md rounded-xl border border-blue-500/30 p-3 sm:p-4 lg:p-5 neon-border-blue neon-glow-blue">
                  <ChartsContainer
                    trades={botTrades} 
                    performance={botPerformance}
                    symbol={selectedBot.symbol}
                    allBotsTrades={allBotsTrades}
                    bots={bots}
                  />
            </div>
          </div>

              {/* Right Column - AI Decisions */}
              <div className="lg:col-span-3">
                <BotTabs
                  bots={bots}
                  selectedBot={selectedBot}
                  onBotSelect={setSelectedBot}
                  botDecisions={botDecisions}
                />
              </div>
              
              {/* Empty spacer on right to center content */}
              <div className="lg:col-span-1 hidden lg:block"></div>
            </div>
          </>
        ) : (
          <div className="text-center py-20">
            <Zap className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-400 mb-2">No Bots Active</h2>
            <p className="text-gray-500">Waiting for trading bots to initialize...</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Stat Card Component
const StatCard = ({ label, value, icon, color = 'blue', trend, breakdown, compact = false }) => {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/40 text-blue-300',
    cyan: 'from-cyan-500/20 to-cyan-600/10 border-cyan-500/40 text-cyan-300',
    purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/40 text-purple-300',
  };

  const glowClasses = {
    blue: 'neon-glow-blue',
    cyan: 'neon-glow-cyan',
    purple: 'neon-glow-purple',
  };

  const textGlowClasses = {
    blue: 'neon-text-blue',
    cyan: 'neon-text-cyan',
    purple: 'neon-text-purple',
  };

  // Compact cards have less padding
  const paddingClass = compact ? 'p-2' : 'p-3 sm:p-4';

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} backdrop-blur-sm rounded-lg border ${paddingClass} flex-shrink-0 w-[calc(100vw-2rem)] sm:w-auto lg:w-full ${glowClasses[color]} hover:scale-105 transition-all`}>
      <div className="flex flex-col items-center justify-center text-center h-full">
        <div className="flex items-center space-x-1 mb-1">
          <div className={`p-0.5 rounded bg-${color}-500/20 ${textGlowClasses[color]}`}>
            {React.cloneElement(icon, { className: 'w-3 h-3' })}
          </div>
          <span className="text-[10px] text-gray-400 uppercase tracking-wide">{label}</span>
        </div>
        <div className={`text-lg font-bold ${textGlowClasses[color]}`}>{value}</div>
        {breakdown && (
          <div className="mt-1 w-full space-y-0">
            {breakdown.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-[9px] px-1">
                <span className="text-gray-500">{item.label}:</span>
                <span className="text-gray-300 font-medium">{item.value}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;

