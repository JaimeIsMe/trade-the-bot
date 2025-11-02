import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, DollarSign, Target, Brain, Zap } from 'lucide-react';
import DecisionLog from './components/DecisionLog';
import PositionsPanel from './components/PositionsPanel';
import TradeHistory from './components/TradeHistory';

function App() {
  const [status, setStatus] = useState('offline');
  const [portfolio, setPortfolio] = useState({});
  
  // ASTER bot state
  const [asterPerformance, setAsterPerformance] = useState({});
  const [asterDecisions, setAsterDecisions] = useState([]);
  const [asterTrades, setAsterTrades] = useState([]);
  const [asterPositions, setAsterPositions] = useState([]);
  
  // Moon/BTC bot state  
  const [btcPerformance, setBtcPerformance] = useState({});
  const [btcDecisions, setBtcDecisions] = useState([]);
  const [btcTrades, setBtcTrades] = useState([]);
  const [btcPositions, setBtcPositions] = useState([]);

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
        btcPerfRes,
        btcDecisionsRes,
        btcTradesRes,
        btcPositionsRes
      ] = await Promise.all([
        axios.get('/api/status'),
        axios.get('/api/portfolio/summary'),
        axios.get('/api/performance?symbol=ASTERUSDT'),
        axios.get('/api/decisions?symbol=ASTERUSDT&limit=30'),
        axios.get('/api/trades?symbol=ASTERUSDT&limit=50'),
        axios.get('/api/positions'),
        axios.get('/api/performance?symbol=BTCUSDT'),
        axios.get('/api/decisions?symbol=BTCUSDT&limit=30'),
        axios.get('/api/trades?symbol=BTCUSDT&limit=50'),
        axios.get('/api/positions'),
      ]);

      setStatus(statusRes.data.status);
      setPortfolio(portfolioRes.data);
      
      setAsterPerformance(asterPerfRes.data);
      setAsterDecisions(asterDecisionsRes.data);
      setAsterTrades(asterTradesRes.data);
      setAsterPositions(asterPositionsRes.data.filter(p => p.symbol === 'ASTERUSDT'));
      
      setBtcPerformance(btcPerfRes.data);
      setBtcDecisions(btcDecisionsRes.data);
      setBtcTrades(btcTradesRes.data);
      setBtcPositions(btcPositionsRes.data.filter(p => p.symbol === 'BTCUSDT'));
      
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
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-black/90 backdrop-blur-sm border-b border-purple-500/10">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 via-pink-500 to-purple-600 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">
                    Aster <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">Dual Strategy</span>
                  </h1>
                  <p className="text-xs text-gray-500">2 Autonomous AI Trading Bots</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/50 border border-purple-500/20">
                <div className={`w-2 h-2 rounded-full ${status === 'running' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className="text-sm text-gray-300 capitalize">{status}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Portfolio Summary Banner */}
        <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-purple-900/20 via-pink-900/20 to-purple-900/20 border border-purple-500/20">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-sm text-gray-400 mb-1">Total Portfolio Value</div>
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {formatCurrency(portfolio.total_balance || 0)}
              </div>
              <div className="text-xs text-gray-500 mt-1">Available: {formatCurrency(portfolio.available_balance || 0)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Total Unrealized PNL</div>
              <div className={`text-3xl font-bold ${portfolio.total_unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {portfolio.total_unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(portfolio.total_unrealized_pnl || 0)}
              </div>
              <div className="text-xs text-gray-500 mt-1">Margin Ratio: {portfolio.margin_ratio?.toFixed(2)}%</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Total Exposure</div>
              <div className="text-3xl font-bold text-blue-400">
                {formatCurrency(portfolio.total_exposure || 0)}
              </div>
              <div className="text-xs text-gray-500 mt-1">Across both strategies</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Active Strategies</div>
              <div className="text-3xl font-bold text-purple-400">
                {portfolio.strategies_active || 2}
              </div>
              <div className="text-xs text-gray-500 mt-1">Running simultaneously</div>
            </div>
          </div>
        </div>

        {/* Two-Column Strategy Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* LEFT COLUMN: ASTER BOT */}
          <div className="space-y-6">
            <div className="bg-slate-900/30 backdrop-blur-sm border-2 border-cyan-500/30 rounded-xl p-4">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
                  <Brain className="w-5 h-5 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">ASTER Strategy</h2>
                  <p className="text-xs text-gray-500">AI-Powered Technical Analysis | 5min Candles</p>
                </div>
              </div>
              
              {/* ASTER Performance Stats */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-xs text-gray-500">Trades</div>
                  <div className="text-xl font-bold text-cyan-400">{asterPerformance.total_trades || 0}</div>
                  <div className="text-xs text-gray-600">Win: {formatPercent(asterPerformance.win_rate)}</div>
                </div>
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-xs text-gray-500">PNL</div>
                  <div className={`text-xl font-bold ${asterPerformance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {asterPerformance.total_pnl >= 0 ? '+' : ''}{formatCurrency(asterPerformance.total_pnl || 0)}
                  </div>
                  <div className="text-xs text-gray-600">Realized</div>
                </div>
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-xs text-gray-500">Exposure</div>
                  <div className="text-xl font-bold text-blue-400">{formatCurrency(portfolio.aster_exposure || 0)}</div>
                  <div className="text-xs text-gray-600">Current</div>
                </div>
              </div>
              
              {/* ASTER Positions */}
              <PositionsPanel positions={asterPositions} compact={true} />
            </div>
            
            {/* ASTER Decision Log */}
            <DecisionLog decisions={asterDecisions} title="ASTER AI Decisions" />
            
            {/* ASTER Trade History */}
            <TradeHistory trades={asterTrades} title="ASTER Trade History" />
          </div>

          {/* RIGHT COLUMN: MOON/BTC BOT */}
          <div className="space-y-6">
            <div className="bg-slate-900/30 backdrop-blur-sm border-2 border-purple-500/30 rounded-xl p-4">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20">
                  <Zap className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">MOON Strategy</h2>
                  <p className="text-xs text-gray-500">Lunar Phase Trading | BTC Only</p>
                </div>
              </div>
              
              {/* BTC Performance Stats */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-xs text-gray-500">Trades</div>
                  <div className="text-xl font-bold text-purple-400">{btcPerformance.total_trades || 0}</div>
                  <div className="text-xs text-gray-600">Win: {formatPercent(btcPerformance.win_rate)}</div>
                </div>
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-xs text-gray-500">PNL</div>
                  <div className={`text-xl font-bold ${btcPerformance.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {btcPerformance.total_pnl >= 0 ? '+' : ''}{formatCurrency(btcPerformance.total_pnl || 0)}
                  </div>
                  <div className="text-xs text-gray-600">Realized</div>
                </div>
                <div className="bg-black/30 rounded-lg p-3">
                  <div className="text-xs text-gray-500">Exposure</div>
                  <div className="text-xl font-bold text-blue-400">{formatCurrency(portfolio.btc_exposure || 0)}</div>
                  <div className="text-xs text-gray-600">Current</div>
                </div>
              </div>
              
              {/* BTC Positions */}
              <PositionsPanel positions={btcPositions} compact={true} />
            </div>
            
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
  );
}

export default App;


