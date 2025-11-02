import React, { useMemo, useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { BarChart3, TrendingUp, PieChart as PieChartIcon } from 'lucide-react';

// Color palette matching the dashboard theme
const BOT_COLORS = {
  'ASTERUSDT': '#06b6d4', // Cyan
  'BTCUSDT': '#3b82f6',   // Blue
  'ETHUSDT': '#8b5cf6',   // Purple
  'SOLUSDT': '#10b981',   // Green
  'BNBUSDT': '#f59e0b',   // Amber
};

const getBotColor = (symbol) => {
  return BOT_COLORS[symbol] || '#64748b';
};

const AdditionalCharts = ({ allBotsTrades = {}, viewMode = 'distribution' }) => {
  
  // 1. P&L Distribution Data (Histogram)
  const pnlDistribution = useMemo(() => {
    const allPnLs = [];
    
    Object.values(allBotsTrades).forEach(trades => {
      if (Array.isArray(trades)) {
        trades.forEach(trade => {
          const pnl = parseFloat(trade.pnl || trade.realizedProfit || 0);
          if (pnl !== 0) {
            allPnLs.push(pnl);
          }
        });
      }
    });
    
    if (allPnLs.length === 0) return [];
    
    // Create bins for histogram
    const min = Math.min(...allPnLs);
    const max = Math.max(...allPnLs);
    const binCount = 10;
    const binSize = (max - min) / binCount;
    
    const bins = Array.from({ length: binCount }, (_, i) => {
      const binStart = min + (i * binSize);
      const binEnd = binStart + binSize;
      const binCenter = (binStart + binEnd) / 2;
      
      const count = allPnLs.filter(pnl => pnl >= binStart && pnl < binEnd).length;
      
      return {
        range: `$${binStart.toFixed(0)} to $${binEnd.toFixed(0)}`,
        center: binCenter,
        count: count,
        fill: binCenter >= 0 ? '#10b981' : '#ef4444'
      };
    });
    
    return bins;
  }, [allBotsTrades]);
  
  // 2. Asset Performance Comparison
  const assetComparison = useMemo(() => {
    const comparison = [];
    
    Object.entries(allBotsTrades).forEach(([symbol, trades]) => {
      if (Array.isArray(trades) && trades.length > 0) {
        let totalPnL = 0;
        let wins = 0;
        let losses = 0;
        
        trades.forEach(trade => {
          const pnl = parseFloat(trade.pnl || trade.realizedProfit || 0);
          totalPnL += pnl;
          if (pnl > 0) wins++;
          else if (pnl < 0) losses++;
        });
        
        const winRate = trades.length > 0 ? (wins / trades.length) * 100 : 0;
        
        comparison.push({
          asset: symbol.replace('USDT', ''),
          symbol: symbol,
          totalPnL: totalPnL,
          trades: trades.length,
          winRate: winRate,
          wins: wins,
          losses: losses,
          color: getBotColor(symbol)
        });
      }
    });
    
    return comparison.sort((a, b) => b.totalPnL - a.totalPnL);
  }, [allBotsTrades]);
  
  // 3. Rolling Win Rate (30-trade window)
  const rollingWinRate = useMemo(() => {
    // Combine all trades across all bots
    const allTrades = [];
    
    Object.entries(allBotsTrades).forEach(([symbol, trades]) => {
      if (Array.isArray(trades)) {
        trades.forEach(trade => {
          const pnl = parseFloat(trade.pnl || trade.realizedProfit || 0);
          allTrades.push({
            timestamp: trade.timestamp || trade.time || 0,
            pnl: pnl,
            symbol: symbol
          });
        });
      }
    });
    
    // Sort by timestamp
    allTrades.sort((a, b) => a.timestamp - b.timestamp);
    
    if (allTrades.length < 10) return [];
    
    // Calculate rolling win rate with 30-trade window
    const windowSize = 30;
    const rollingData = [];
    
    for (let i = windowSize - 1; i < allTrades.length; i++) {
      const window = allTrades.slice(i - windowSize + 1, i + 1);
      const wins = window.filter(t => t.pnl > 0).length;
      const winRate = (wins / windowSize) * 100;
      
      const date = new Date(allTrades[i].timestamp);
      const timeStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      
      rollingData.push({
        trade: i + 1,
        time: timeStr,
        winRate: winRate,
        timestamp: allTrades[i].timestamp
      });
    }
    
    return rollingData;
  }, [allBotsTrades]);
  
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload[0]) {
      return (
        <div className="bg-slate-800 border border-blue-500/30 rounded-lg p-3 shadow-xl">
          <div className="text-xs text-white font-semibold mb-1">{label}</div>
          <div className="text-sm text-cyan-400">
            {payload[0].name}: {payload[0].value.toFixed(2)}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-4">
      {/* Tab Content */}
      {viewMode === 'distribution' && (
        <div className="bg-[#1a1a1a] rounded-lg p-4 border border-gray-800/50">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white mb-1">P&L Distribution</h3>
          <p className="text-xs text-gray-500">Distribution of trade profits and losses</p>
        </div>
        
        {pnlDistribution.length === 0 ? (
          <div className="text-center text-gray-500 py-12 text-sm">
            No trade data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={pnlDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis 
                dataKey="center" 
                stroke="#64748b"
                style={{ fontSize: '10px' }}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              <YAxis 
                stroke="#64748b"
                style={{ fontSize: '10px' }}
                label={{ value: 'Trades', angle: -90, position: 'insideLeft', style: { fill: '#64748b', fontSize: '10px' } }}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine x={0} stroke="#64748b" strokeDasharray="3 3" />
              <Bar dataKey="count" name="Trades">
                {pnlDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
        </div>
      )}

      {/* 2. Asset Performance Comparison */}
      {viewMode === 'comparison' && (
        <div className="bg-[#1a1a1a] rounded-lg p-4 border border-gray-800/50">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white mb-1">Asset Performance</h3>
          <p className="text-xs text-gray-500">Total P&L comparison by asset</p>
        </div>
        
        {assetComparison.length === 0 ? (
          <div className="text-center text-gray-500 py-12 text-sm">
            No trade data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={assetComparison}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis 
                dataKey="asset" 
                stroke="#64748b"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#64748b"
                style={{ fontSize: '10px' }}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
              <Bar dataKey="totalPnL" name="Total P&L">
                {assetComparison.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
        
        {/* Asset stats below chart - compact view */}
        <div className="mt-3 grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
          {assetComparison.map((asset) => (
            <div key={asset.symbol} className="flex items-center justify-between text-[10px] bg-black/30 rounded p-1.5">
              <div className="flex items-center space-x-1.5">
                <div className="w-2 h-2 rounded" style={{ backgroundColor: asset.color }} />
                <span className="text-gray-400 font-medium">{asset.asset}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={asset.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'} title={`${asset.trades} trades, ${asset.winRate.toFixed(1)}% win rate`}>
                  {asset.totalPnL >= 0 ? '+' : ''}${asset.totalPnL.toFixed(0)}
                </span>
              </div>
            </div>
          ))}
        </div>
        </div>
      )}

      {/* 3. Rolling Win Rate */}
      {viewMode === 'trends' && (
        <div className="bg-[#1a1a1a] rounded-lg p-4 border border-gray-800/50">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white mb-1">Rolling Win Rate</h3>
          <p className="text-xs text-gray-500">Win rate trend (30-trade window)</p>
        </div>
        
        {rollingWinRate.length === 0 ? (
          <div className="text-center text-gray-500 py-12 text-sm">
            Need at least 30 trades for rolling win rate
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={500}>
            <LineChart data={rollingWinRate}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis 
                dataKey="time" 
                stroke="#64748b"
                style={{ fontSize: '10px' }}
                interval="preserveStartEnd"
              />
              <YAxis 
                domain={[0, 100]}
                stroke="#64748b"
                style={{ fontSize: '10px' }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={50} stroke="#64748b" strokeDasharray="3 3" label={{ value: '50%', position: 'right', fill: '#64748b', fontSize: 10 }} />
              <Line 
                type="monotone" 
                dataKey="winRate" 
                stroke="#06b6d4" 
                strokeWidth={2}
                dot={false}
                name="Win Rate (%)"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
        </div>
      )}
    </div>
  );
};

export default AdditionalCharts;

