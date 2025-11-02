import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, DollarSign, Target, Brain, Zap } from 'lucide-react';
import DecisionLog from './components/DecisionLog';
import PositionsPanel from './components/PositionsPanel';
import TradeHistory from './components/TradeHistory';
import PriceChart from './components/PriceChart';
import TickerBar from './components/TickerBar';

function App() {
  const [status, setStatus] = useState('offline');
  const [portfolio, setPortfolio] = useState({});
  
  // ASTER bot state
  const [asterPerformance, setAsterPerformance] = useState({});
  const [asterDecisions, setAsterDecisions] = useState([]);
  const [asterTrades, setAsterTrades] = useState([]);
  const [asterPositions, setAsterPositions] = useState([]);
  const [asterCandles, setAsterCandles] = useState([]);
  
  // Moon/BTC bot state  
  const [btcPerformance, setBtcPerformance] = useState({});
  const [btcDecisions, setBtcDecisions] = useState([]);
  const [btcTrades, setBtcTrades] = useState([]);
  const [btcPositions, setBtcPositions] = useState([]);
  const [btcCandles, setBtcCandles] = useState([]);

  // Fetch data on mount and set up polling
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // Update every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [
        statusRes,
        portfolioRes,
        asterPerfRes,
        asterDecisionsRes,
        asterTradesRes,
        asterPositionsRes,
        asterCandlesRes,
        btcPerfRes,
        btcDecisionsRes,
        btcTradesRes,
        btcPositionsRes,
        btcCandlesRes
      ] = await Promise.all([
        axios.get('/api/status'),
        axios.get('/api/portfolio/summary'),
        axios.get('/api/performance?symbol=ASTERUSDT'),
        axios.get('/api/decisions?symbol=ASTERUSDT&limit=30'),
        axios.get('/api/trades?symbol=ASTERUSDT&limit=50'),
        axios.get('/api/positions'),
        axios.get('/api/klines?symbol=ASTERUSDT&interval=5m&limit=288'),
        axios.get('/api/performance?symbol=BTCUSDT'),
        axios.get('/api/decisions?symbol=BTCUSDT&limit=30'),
        axios.get('/api/trades?symbol=BTCUSDT&limit=50'),
        axios.get('/api/positions'),
        axios.get('/api/klines?symbol=BTCUSDT&interval=5m&limit=288'),
      ]);

      setStatus(statusRes.data.status);
      setPortfolio(portfolioRes.data);
      
      setAsterPerformance(asterPerfRes.data);
      setAsterDecisions(asterDecisionsRes.data);
      setAsterTrades(asterTradesRes.data);
      setAsterPositions(asterPositionsRes.data.filter(p => p.symbol === 'ASTERUSDT'));
      setAsterCandles(asterCandlesRes.data);
      
      setBtcPerformance(btcPerfRes.data);
      setBtcDecisions(btcDecisionsRes.data);
      setBtcTrades(btcTradesRes.data);
      setBtcPositions(btcPositionsRes.data.filter(p => p.symbol === 'BTCUSDT'));
      setBtcCandles(btcCandlesRes.data);
      
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

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

  return (
    <div className="min-h-screen bg-[#0a0a0a] relative overflow-hidden">
      {/* Decorative Background Gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Header background glow - centered behind Dashboard text */}
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 w-[900px] h-[250px] bg-gradient-to-b from-purple-500/30 via-pink-500/20 to-transparent blur-3xl"></div>
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-10 w-[600px] h-[200px] bg-gradient-to-br from-cyan-400/15 via-purple-500/15 to-pink-500/15 rounded-full blur-2xl"></div>
        
        {/* Top right purple gradient blob */}
        <div className="absolute -top-40 -right-40 w-[700px] h-[700px] bg-gradient-to-br from-purple-500/25 to-pink-500/25 rounded-full blur-3xl animate-pulse"></div>
        
        {/* Top left angled shape */}
        <div className="absolute -top-20 -left-20 w-[600px] h-[500px] bg-gradient-to-br from-purple-600/20 to-transparent transform -rotate-45 blur-2xl"></div>
        
        {/* Middle right gradient */}
        <div className="absolute top-1/3 -right-32 w-[500px] h-[600px] bg-gradient-to-l from-pink-500/20 to-purple-600/15 rounded-full blur-3xl"></div>
        
        {/* Middle left cyan accent */}
        <div className="absolute top-1/2 -left-40 w-[450px] h-[450px] bg-gradient-to-r from-cyan-500/15 to-blue-500/10 rounded-full blur-3xl"></div>
        
        {/* Bottom right pink/purple mix */}
        <div className="absolute -bottom-20 right-1/4 w-[550px] h-[550px] bg-gradient-to-tl from-pink-600/20 to-purple-500/15 rounded-full blur-3xl"></div>
        
        {/* Bottom left purple accent */}
        <div className="absolute -bottom-32 -left-32 w-[600px] h-[600px] bg-gradient-to-tr from-purple-500/25 to-transparent rounded-full blur-3xl"></div>
        
        {/* Center subtle glow */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-br from-purple-500/8 via-purple-600/5 to-transparent rounded-full blur-3xl"></div>
        
        {/* Additional floating shapes */}
        <div className="absolute top-1/4 left-1/3 w-[300px] h-[300px] bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-2xl"></div>
        <div className="absolute bottom-1/3 right-1/3 w-[350px] h-[350px] bg-gradient-to-tl from-pink-500/12 to-purple-500/12 rounded-full blur-2xl"></div>
      </div>

      {/* Content - needs relative positioning to stay above background */}
      <div className="relative z-10">
        {/* Header */}
        <header className="bg-gradient-to-r from-purple-900/40 via-[#111111]/80 to-pink-900/40 backdrop-blur-xl border-b border-purple-500/20">
        <div className="max-w-[1800px] mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-center flex-1">
              <div className="text-center">
                <h1 className="text-5xl font-bold text-white tracking-tight drop-shadow-[0_0_15px_rgba(168,85,247,0.4)]">
                  Aster Vibe Trading Dashboard
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-[#1a1a1a] border border-gray-800/50">
                <div className={`w-2.5 h-2.5 rounded-full ${status === 'running' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className="text-sm font-medium text-gray-300 capitalize">{status}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Scrolling Ticker Bar */}
      <TickerBar />

      {/* Main Content */}
      <main className="max-w-[1800px] mx-auto px-6 py-8">
        
        {/* Portfolio Summary Cards */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Available Balance */}
          <div className="bg-[#1a1a1a]/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-800/50 hover:border-gray-700/50 transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/10">
                <DollarSign className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-xs text-gray-500">●●●</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-gray-400">Available Balance</div>
              <div className="text-3xl font-bold text-white tracking-tight">
                {formatCurrency(portfolio.available_balance || 0)}
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-500">Total:</span>
                <span className="text-gray-400">{formatCurrency(portfolio.total_balance || 0)}</span>
              </div>
            </div>
          </div>

          {/* Total Orders/Trades */}
          <div className="bg-[#1a1a1a]/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-800/50 hover:border-gray-700/50 transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-600/10">
                <Activity className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-xs text-gray-500">●●●</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-gray-400">Total Trades</div>
              <div className="text-3xl font-bold text-white tracking-tight">
                {(asterPerformance.total_trades || 0) + (btcPerformance.total_trades || 0)}
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-green-500">↑ {formatPercent(((asterPerformance.win_rate || 0) + (btcPerformance.win_rate || 0)) / 2)}</span>
                <span className="text-gray-600">Win rate</span>
              </div>
            </div>
          </div>

          {/* Unrealized PNL */}
          <div className="bg-[#1a1a1a]/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-800/50 hover:border-gray-700/50 transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-pink-500/10 to-pink-600/10">
                <TrendingUp className="w-5 h-5 text-pink-400" />
              </div>
              <div className="text-xs text-gray-500">●●●</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-gray-400">Unrealized PNL</div>
              <div className={`text-3xl font-bold tracking-tight ${portfolio.total_unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {portfolio.total_unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(portfolio.total_unrealized_pnl || 0)}
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <span className={portfolio.total_unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}>
                  {portfolio.total_unrealized_pnl >= 0 ? '↑' : '↓'} {Math.abs((portfolio.total_unrealized_pnl / portfolio.total_balance * 100) || 0).toFixed(2)}%
                </span>
                <span className="text-gray-600">From {(asterPerformance.total_trades || 0) + (btcPerformance.total_trades || 0)} positions</span>
              </div>
            </div>
          </div>

          {/* Active Strategies */}
          <div className="bg-[#1a1a1a]/80 backdrop-blur-sm rounded-2xl p-6 border border-gray-800/50 hover:border-gray-700/50 transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/10 to-cyan-600/10">
                <Target className="w-5 h-5 text-cyan-400" />
              </div>
              <div className="text-xs text-gray-500">●●●</div>
            </div>
            <div className="space-y-1">
              <div className="text-sm text-gray-400">Exposure</div>
              <div className="text-3xl font-bold text-white tracking-tight">
                {formatCurrency(portfolio.total_exposure || 0)}
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-cyan-500">→ {portfolio.strategies_active || 2} strategies</span>
                <span className="text-gray-600">Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Two-Column Strategy Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* LEFT COLUMN: ASTER BOT */}
          <div className="space-y-5">
            <div className="bg-[#1a1a1a]/80 backdrop-blur-sm rounded-2xl p-5 border border-gray-800/50">
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10">
                    <Brain className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">ASTER Strategy</h2>
                    <p className="text-xs text-gray-500">AI-Powered | 1min Candles | GPT-4o mini | 2.5min checks</p>
                  </div>
                </div>
                <div className="text-xs text-gray-500">●●●</div>
              </div>
              
              {/* ASTER Performance Stats */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-[#111111]/60 backdrop-blur-sm rounded-xl p-4 border border-gray-800/30">
                  <div className="text-xs text-gray-500 mb-1">Trades</div>
                  <div className="text-2xl font-bold text-white">{asterPerformance.total_trades || 0}</div>
                  <div className="text-xs text-green-500 mt-1">↑ {formatPercent(asterPerformance.win_rate)}</div>
                </div>
                <div className="bg-[#111111]/60 backdrop-blur-sm rounded-xl p-4 border border-gray-800/30">
                  <div className="text-xs text-gray-500 mb-1">PNL</div>
                  <div className={`text-2xl font-bold ${asterPerformance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {asterPerformance.total_pnl >= 0 ? '+' : ''}{formatCurrency(asterPerformance.total_pnl || 0)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">Realized</div>
                </div>
                <div className="bg-[#111111]/60 backdrop-blur-sm rounded-xl p-4 border border-gray-800/30">
                  <div className="text-xs text-gray-500 mb-1">Exposure</div>
                  <div className="text-2xl font-bold text-cyan-400">{formatCurrency(portfolio.aster_exposure || 0)}</div>
                  <div className="text-xs text-gray-500 mt-1">Current</div>
                </div>
              </div>
              
              {/* ASTER Positions */}
              <PositionsPanel positions={asterPositions} compact={true} />
            </div>
            
            {/* ASTER Price Chart */}
            <PriceChart candles={asterCandles} symbol="ASTERUSDT" />
            
            {/* ASTER Decision Log */}
            <DecisionLog decisions={asterDecisions} title="ASTER AI Decisions" />
            
            {/* ASTER Trade History */}
            <TradeHistory trades={asterTrades} title="ASTER Trade History" />
          </div>

          {/* RIGHT COLUMN: MOON/BTC BOT */}
          <div className="space-y-5">
            <div className="bg-[#1a1a1a]/80 backdrop-blur-sm rounded-2xl p-5 border border-gray-800/50">
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10">
                    <Zap className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">MOON Strategy</h2>
                    <p className="text-xs text-gray-500">Lunar Phase | BTC | Rule-Based ($0 cost)</p>
                  </div>
                </div>
                <div className="text-xs text-gray-500">●●●</div>
              </div>
              
              {/* BTC Performance Stats */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-[#111111]/60 backdrop-blur-sm rounded-xl p-4 border border-gray-800/30">
                  <div className="text-xs text-gray-500 mb-1">Trades</div>
                  <div className="text-2xl font-bold text-white">{btcPerformance.total_trades || 0}</div>
                  <div className="text-xs text-green-500 mt-1">↑ {formatPercent(btcPerformance.win_rate)}</div>
                </div>
                <div className="bg-[#111111]/60 backdrop-blur-sm rounded-xl p-4 border border-gray-800/30">
                  <div className="text-xs text-gray-500 mb-1">PNL</div>
                  <div className={`text-2xl font-bold ${btcPerformance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {btcPerformance.total_pnl >= 0 ? '+' : ''}{formatCurrency(btcPerformance.total_pnl || 0)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">Realized</div>
                </div>
                <div className="bg-[#111111]/60 backdrop-blur-sm rounded-xl p-4 border border-gray-800/30">
                  <div className="text-xs text-gray-500 mb-1">Exposure</div>
                  <div className="text-2xl font-bold text-purple-400">{formatCurrency(portfolio.btc_exposure || 0)}</div>
                  <div className="text-xs text-gray-500 mt-1">Current</div>
                </div>
              </div>
              
              {/* BTC Positions */}
              <PositionsPanel positions={btcPositions} compact={true} />
            </div>
            
            {/* BTC Price Chart */}
            <PriceChart candles={btcCandles} symbol="BTCUSDT" />
            
            {/* BTC Decision Log */}
            <DecisionLog decisions={btcDecisions} title="MOON AI Decisions" />
            
            {/* BTC Trade History */}
            <TradeHistory trades={btcTrades} title="MOON Trade History" />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 pb-8 border-t border-purple-500/10">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <p className="text-gray-500 text-sm">© 2025 Aster Vibe Trader. Competition Entry.</p>
              <a 
                href="https://www.asterdex.com/en" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
              >
                Powered by Aster DEX
              </a>
            </div>
            <div className="flex items-center space-x-4 text-xs text-gray-600">
              <span>2 Strategies</span>
              <span>•</span>
              <span>GPT-4 + Moon Phases</span>
              <span>•</span>
              <span>5min Updates</span>
            </div>
          </div>
        </div>
      </footer>
      </div>
    </div>
  );
}

export default App;

