import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, DollarSign, Target, Brain } from 'lucide-react';
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
    const interval = setInterval(fetchData, 3000);
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
    <div className="min-h-screen bg-[#0d0d0d]">
      {/* Clean, minimal header */}
      <header className="bg-[#111111] border-b border-gray-800">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">Aster Vibe Trading</h1>
              <span className="text-sm text-gray-500">AI-Powered Trading Dashboard</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#1a1a1a] border border-gray-800">
                <div className={`w-2 h-2 rounded-full ${status === 'running' ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className="text-xs font-medium text-gray-400 capitalize">{status}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Ticker Bar */}
      <TickerBar />

      {/* Main Content */}
      <div className="max-w-[1920px] mx-auto px-6 py-6">
        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard
            label="Total Balance"
            value={formatCurrency(portfolio.total_balance)}
            icon={<DollarSign className="w-5 h-5" />}
            color="blue"
          />
          <StatCard
            label="Total Trades"
            value={asterPerformance.total_trades || 0}
            icon={<Activity className="w-5 h-5" />}
            color="cyan"
          />
          <StatCard
            label="Win Rate"
            value={formatPercent(asterPerformance.win_rate)}
            icon={<Target className="w-5 h-5" />}
            color="emerald"
            trend={asterPerformance.win_rate > 0.5 ? 'up' : 'down'}
          />
          <StatCard
            label="Unrealized P&L"
            value={formatCurrency(portfolio.total_unrealized_pnl)}
            icon={<TrendingUp className="w-5 h-5" />}
            color={portfolio.total_unrealized_pnl >= 0 ? 'emerald' : 'red'}
            trend={portfolio.total_unrealized_pnl >= 0 ? 'up' : 'down'}
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Charts & Positions */}
          <div className="col-span-8 space-y-6">
            {/* Price Chart */}
            <div className="bg-[#111111] rounded-xl border border-gray-800 p-5">
              <h2 className="text-lg font-semibold text-white mb-4">ASTERUSDT</h2>
              <PriceChart candles={asterCandles} />
            </div>

            {/* Positions */}
            <PositionsPanel positions={asterPositions} />
          </div>

          {/* Right Column - Decisions & History */}
          <div className="col-span-4 space-y-6">
            <DecisionLog decisions={asterDecisions} title="ASTER AI Decisions" />
            <TradeHistory trades={asterTrades} />
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
const StatCard = ({ label, value, icon, color = 'blue', trend }) => {
  const colorClasses = {
    blue: 'from-blue-500/10 to-blue-600/5 border-blue-500/20 text-blue-400',
    cyan: 'from-cyan-500/10 to-cyan-600/5 border-cyan-500/20 text-cyan-400',
    emerald: 'from-emerald-500/10 to-emerald-600/5 border-emerald-500/20 text-emerald-400',
    red: 'from-red-500/10 to-red-600/5 border-red-500/20 text-red-400',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} rounded-xl border p-4`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
        <div className={`p-1.5 rounded-lg bg-${color}-500/10`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {trend && (
        <div className="mt-1 text-xs text-gray-500">
          {trend === 'up' ? '↑' : '↓'} {trend === 'up' ? 'Positive' : 'Negative'}
        </div>
      )}
    </div>
  );
};

export default App;

