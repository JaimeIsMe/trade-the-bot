import React, { useMemo, useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, ReferenceLine, Cell, Legend } from 'recharts';

// Color palette for different bots
const BOT_COLORS = {
  'ASTERUSDT': '#06b6d4', // Cyan
  'BTCUSDT': '#3b82f6',   // Blue
  'ETHUSDT': '#8b5cf6',   // Purple
  'SOLUSDT': '#10b981',   // Green
  'BNBUSDT': '#f59e0b',   // Amber
};

const getBotColor = (symbol) => {
  return BOT_COLORS[symbol] || '#64748b'; // Default gray
};

const BotPerformanceChart = ({ trades, performance, symbol, allBotsTrades = {}, bots = [], viewMode = 'cumulative' }) => {
  const [chartHeight, setChartHeight] = useState(500);
  const [isMobile, setIsMobile] = useState(false);
  
  useEffect(() => {
    const updateResponsive = () => {
      const width = window.innerWidth;
      setIsMobile(width < 640);
      
      // Responsive chart height - taller on mobile for better readability
      if (width < 640) {
        setChartHeight(400); // Mobile: taller for better visibility
      } else if (width < 1024) {
        setChartHeight(450); // Tablet
      } else {
        setChartHeight(500); // Desktop
      }
    };
    updateResponsive();
    window.addEventListener('resize', updateResponsive);
    return () => window.removeEventListener('resize', updateResponsive);
  }, []);
  // Build combined chart data from all bots
  const chartData = useMemo(() => {
    // Combine all trades from all bots
    const allTrades = [];
    
    // Process each bot's trades
    Object.keys(allBotsTrades).forEach((botSymbol) => {
      const botTrades = allBotsTrades[botSymbol];
      if (!botTrades || botTrades.length === 0) return;
      
      botTrades.forEach((trade) => {
        // Extract PNL
        let pnl = 0;
        if (trade.pnl !== undefined && trade.pnl !== 0) {
          pnl = parseFloat(trade.pnl);
        } else if (trade.realizedProfit !== undefined) {
          pnl = parseFloat(trade.realizedProfit);
        }
        
        const timestamp = trade.timestamp || trade.time || Date.now();
        
        allTrades.push({
          timestamp,
          pnl,
          symbol: botSymbol,
          trade // Keep original trade for tooltip
        });
      });
    });
    
    // Sort all trades by timestamp
    allTrades.sort((a, b) => a.timestamp - b.timestamp);
    
    // Build cumulative P&L per bot chronologically
    const cumulativeByBot = {};
    const timePoints = [];
    
    // Process trades chronologically and build cumulative values
    allTrades.forEach((trade) => {
      const botSymbol = trade.symbol;
      if (!cumulativeByBot[botSymbol]) {
        cumulativeByBot[botSymbol] = 0;
      }
      cumulativeByBot[botSymbol] += trade.pnl;
      
      // Get time string for this trade
      // For a week's view, include date to distinguish days
      const date = new Date(trade.timestamp);
      const today = new Date();
      const daysDiff = Math.floor((today - date) / (1000 * 60 * 60 * 24));
      
      // Format: Show date + time if older than today, just time if today
      let timeStr;
      if (daysDiff === 0) {
        timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else if (daysDiff < 7) {
        timeStr = date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
      } else {
        timeStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }
      
      // Find or create time point for this timestamp
      let timePoint = timePoints.find(tp => tp.timestamp === trade.timestamp);
      if (!timePoint) {
        timePoint = {
          time: timeStr,
          fullTime: date.toLocaleString(),
          timestamp: trade.timestamp
        };
        timePoints.push(timePoint);
      }
      
      // Update cumulative P&L for this bot at this time point
      timePoint[`${botSymbol}_cumulative`] = cumulativeByBot[botSymbol];
      
      // Also set cumulative values for all other bots at this time point (carry forward previous values)
      Object.keys(allBotsTrades).forEach((otherBotSymbol) => {
        if (otherBotSymbol !== botSymbol && cumulativeByBot[otherBotSymbol] !== undefined) {
          timePoint[`${otherBotSymbol}_cumulative`] = cumulativeByBot[otherBotSymbol];
        }
      });
    });
    
    return timePoints.sort((a, b) => a.timestamp - b.timestamp);
  }, [allBotsTrades]);

  // Build individual trade data for bar chart (from selected bot)
  const barChartData = useMemo(() => {
    if (!trades || trades.length === 0) return [];

    const sortedTrades = [...trades].sort((a, b) => {
      const timeA = new Date(a.timestamp || a.time || 0);
      const timeB = new Date(b.timestamp || b.time || 0);
      return timeA - timeB;
    });
    
    let cumulativePnL = 0;
    return sortedTrades.map((trade, index) => {
      let pnl = 0;
      if (trade.pnl !== undefined && trade.pnl !== 0) {
        pnl = parseFloat(trade.pnl);
      } else if (trade.realizedProfit !== undefined) {
        pnl = parseFloat(trade.realizedProfit);
      }
      
      cumulativePnL += pnl;
      
      const timestamp = trade.timestamp || trade.time || Date.now();
      const date = new Date(timestamp);
      const today = new Date();
      const daysDiff = Math.floor((today - date) / (1000 * 60 * 60 * 24));
      
      // Format: Show date + time if older than today, just time if today
      let timeStr;
      if (daysDiff === 0) {
        timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else if (daysDiff < 7) {
        timeStr = date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
      } else {
        timeStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }
      
      const side = trade.side || trade.action === 'long' ? 'BUY' : trade.action === 'short' ? 'SELL' : 'BUY';
      const price = parseFloat(trade.price || trade.order?.avgPrice || trade.order?.price || 0);
      const qty = parseFloat(trade.qty || trade.order?.size || trade.order?.executedQty || 0);
      
      return {
        time: timeStr,
        date: date.toLocaleDateString(),
        fullTime: date.toLocaleString(),
        pnl: pnl,
        cumulativePnL: cumulativePnL,
        isWin: pnl > 0,
        side: side,
        price: price,
        qty: qty,
        tradeNumber: index + 1
      };
    });
  }, [trades]);

  // Calculate stats (from selected bot's trades)
  const stats = useMemo(() => {
    if (barChartData.length === 0) return { totalPnL: 0, winCount: 0, lossCount: 0, biggestWin: 0, biggestLoss: 0 };
    
    const wins = barChartData.filter(d => d.isWin);
    const losses = barChartData.filter(d => !d.isWin);
    const finalPnL = barChartData[barChartData.length - 1]?.cumulativePnL || 0;
    const biggestWin = Math.max(...barChartData.map(d => d.pnl), 0);
    const biggestLoss = Math.min(...barChartData.map(d => d.pnl), 0);
    
    return {
      totalPnL: finalPnL,
      winCount: wins.length,
      lossCount: losses.length,
      biggestWin,
      biggestLoss
    };
  }, [barChartData]);

  // Determine Y-axis domain for cumulative P&L (from all bots)
  const pnlRange = useMemo(() => {
    if (chartData.length === 0) return { min: -10, max: 10 };
    
    const allValues = [];
    chartData.forEach(point => {
      Object.keys(point).forEach(key => {
        if (key.endsWith('_cumulative')) {
          allValues.push(point[key]);
        }
      });
    });
    
    if (allValues.length === 0) return { min: -10, max: 10 };
    
    const min = Math.min(...allValues, 0);
    const max = Math.max(...allValues, 0);
    const range = max - min;
    const padding = range * 0.1 || 10;
    
    return {
      min: min - padding,
      max: max + padding
    };
  }, [chartData]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-blue-500/30 rounded-lg p-2 sm:p-3 shadow-xl max-w-[85vw] sm:max-w-none">
          <div className="text-xs text-gray-400 mb-1 sm:mb-2 break-words">{data.fullTime}</div>
          <div className="space-y-1 text-xs sm:text-sm">
            {Object.keys(data).filter(key => key.endsWith('_cumulative')).map((key) => {
              const botSymbol = key.replace('_cumulative', '');
              const cumulativeValue = data[key];
              const color = getBotColor(botSymbol);
              const displayName = botSymbol.replace('USDT', '');
              
              return (
                <div key={key} className="flex justify-between space-x-2 sm:space-x-4">
                  <span className="text-gray-400 flex-shrink-0">{displayName}:</span>
                  <span 
                    className="font-semibold flex-shrink-0" 
                    style={{ color }}
                  >
                    {cumulativeValue >= 0 ? '+' : ''}${cumulativeValue?.toFixed(2) || '0.00'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      );
    }
    return null;
  };
  
  const BarTooltip = ({ active, payload }) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-emerald-500/30 rounded-lg p-2 sm:p-3 shadow-xl max-w-[85vw] sm:max-w-none">
          <div className="text-xs text-gray-400 mb-1 sm:mb-2 break-words">{data.fullTime}</div>
          <div className="space-y-1 text-xs sm:text-sm">
            <div className="flex justify-between space-x-2 sm:space-x-4">
              <span className="text-gray-400 flex-shrink-0">Trade #{data.tradeNumber}:</span>
              <span className={`font-semibold flex-shrink-0 ${data.isWin ? 'text-green-400' : 'text-red-400'}`}>
                {data.isWin ? '+' : ''}${data.pnl.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between space-x-2 sm:space-x-4">
              <span className="text-gray-400 flex-shrink-0">Cumulative P&L:</span>
              <span className={`font-semibold flex-shrink-0 ${data.cumulativePnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {data.cumulativePnL >= 0 ? '+' : ''}${data.cumulativePnL.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Cumulative P&L Chart - All Bots Combined */}
      {viewMode === 'cumulative' && (
        <div className="bg-[#1a1a1a] rounded-lg p-3 sm:p-4 border border-gray-800/50">
        <div className="mb-3 sm:mb-4">
          <h3 className="text-base sm:text-lg font-semibold text-white mb-1">Cumulative P&L - All Assets</h3>
          <p className="text-xs text-gray-500">Performance over time for all trading bots</p>
        </div>
        
        {chartData.length === 0 ? (
          <div className="text-center text-gray-500 py-12 sm:py-24 text-sm">
            No trades yet. Waiting for bots to execute trades...
          </div>
        ) : (
          <div className="w-full overflow-x-auto">
            <ResponsiveContainer width="100%" height={chartHeight} minHeight={400}>
              <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              
              <XAxis 
                dataKey="time" 
                stroke="#64748b"
                  style={{ fontSize: isMobile ? '9px' : '10px' }}
                interval="preserveStartEnd"
                  angle={isMobile ? -90 : -45}
                  textAnchor={isMobile ? 'middle' : 'end'}
                  height={isMobile ? 80 : 60}
                  tick={{ fill: '#94a3b8' }}
              />
              
              <YAxis 
                domain={[pnlRange.min, pnlRange.max]}
                stroke="#64748b"
                  style={{ fontSize: isMobile ? '10px' : '12px' }}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
                  width={isMobile ? 50 : 60}
                  tick={{ fill: '#94a3b8' }}
              />
              
              <Tooltip content={<CustomTooltip />} />
              
              {/* Zero line reference */}
              <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
              
              {/* Render a line for each bot */}
              {Object.keys(allBotsTrades).map((botSymbol) => {
                const color = getBotColor(botSymbol);
                const displayName = botSymbol.replace('USDT', '');
                return (
                  <Line
                    key={botSymbol}
                    type="monotone"
                    dataKey={`${botSymbol}_cumulative`}
                    stroke={color}
                      strokeWidth={isMobile ? 1.5 : 2}
                    dot={false}
                      activeDot={{ r: isMobile ? 4 : 5 }}
                    name={displayName}
                  />
                );
              })}
              
              <Legend 
                  wrapperStyle={{ fontSize: isMobile ? '10px' : '12px', paddingTop: '10px' }}
                formatter={(value) => value.replace('USDT', '')}
                  iconSize={isMobile ? 8 : 12}
              />
            </ComposedChart>
          </ResponsiveContainer>
          </div>
        )}
        </div>
      )}

      {/* Individual Trade P&L Bars */}
      {viewMode === 'individual' && (
        <div className="bg-[#1a1a1a] rounded-lg p-4 border border-gray-800/50">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white mb-1">Individual Trade Results</h3>
          <p className="text-xs text-gray-500">Profit/loss per trade</p>
        </div>
        
        {barChartData.length === 0 ? (
          <div className="text-center text-gray-500 py-24 text-sm">
            No trades yet
          </div>
        ) : (
          <div className="w-full overflow-x-auto">
            <ResponsiveContainer width="100%" height={isMobile ? 450 : 600} minHeight={400}>
              <BarChart data={barChartData} margin={{ top: 10, right: 10, left: 10, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              
              <XAxis 
                dataKey="tradeNumber" 
                stroke="#64748b"
                  style={{ fontSize: isMobile ? '9px' : '10px' }}
                  label={{ value: 'Trade #', position: 'insideBottom', offset: -5, style: { fill: '#64748b', fontSize: isMobile ? '9px' : '10px' } }}
                  tick={{ fill: '#94a3b8' }}
              />
              
              <YAxis 
                stroke="#64748b"
                  style={{ fontSize: isMobile ? '10px' : '12px' }}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
                  width={isMobile ? 50 : 60}
                  tick={{ fill: '#94a3b8' }}
              />
              
              <Tooltip content={<BarTooltip />} />
              
              <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
              
                <Bar dataKey="pnl" maxBarSize={isMobile ? 20 : 30}>
                {barChartData.map((entry, index) => (
                  <Cell 
                    key={`bar-${index}`}
                    fill={entry.isWin ? '#10b981' : '#ef4444'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          </div>
        )}
        </div>
      )}
    </div>
  );
};

export default BotPerformanceChart;

