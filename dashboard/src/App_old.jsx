import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, TrendingUp, DollarSign, Target, Brain, Clock } from 'lucide-react';
import DecisionLog from './components/DecisionLog';
import PositionsPanel from './components/PositionsPanel';
import PerformanceChart from './components/PerformanceChart';
import TradeHistory from './components/TradeHistory';

function App() {
  const [status, setStatus] = useState('offline');
  const [performance, setPerformance] = useState({});
  const [decisions, setDecisions] = useState([]);
  const [trades, setTrades] = useState([]);
  const [positions, setPositions] = useState([]);
  const [balance, setBalance] = useState({});

  // Fetch data on mount and set up polling
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [statusRes, perfRes, decisionsRes, tradesRes, positionsRes, balanceRes] = 
        await Promise.all([
          axios.get('/api/status'),
          axios.get('/api/performance'),
          axios.get('/api/decisions?limit=50'),
          axios.get('/api/trades?limit=100'),
          axios.get('/api/positions'),
          axios.get('/api/balance'),
        ]);

      setStatus(statusRes.data.status);
      setPerformance(perfRes.data);
      setDecisions(decisionsRes.data);
      setTrades(tradesRes.data);
      setPositions(positionsRes.data);
      setBalance(balanceRes.data);
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Aster-style branding */}
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 via-pink-500 to-purple-600 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">
                    Aster <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">Vibe Trader</span>
                  </h1>
                  <p className="text-xs text-gray-500">AI-Powered Trading Arena</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/50 border border-purple-500/20">
                <div className={`w-2 h-2 rounded-full ${status === 'running' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className="text-sm text-gray-300 capitalize">{status}</span>
              </div>
              <a 
                href="https://www.asterdex.com/en" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
              >
                Visit Aster DEX →
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Banner */}
        <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-purple-900/20 via-pink-900/20 to-purple-900/20 border border-purple-500/10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Decentralized AI Trading</h2>
              <p className="text-gray-400">Autonomous GPT-4 powered trading on Aster DEX with full risk management</p>
              <div className="flex items-center space-x-6 mt-3">
                <div>
                  <span className="text-xs text-gray-500">Unrealized PNL: </span>
                  <span className={`text-sm font-bold ${balance.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {balance.pnl >= 0 ? '+' : ''}{formatCurrency(balance.pnl || 0)}
                  </span>
                </div>
                {balance.margin_ratio > 0 && (
                  <div>
                    <span className="text-xs text-gray-500">Margin Ratio: </span>
                    <span className="text-sm font-bold text-blue-400">
                      {balance.margin_ratio?.toFixed(2)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {formatCurrency(balance.available || 0)}
              </div>
              <div className="text-sm text-gray-500">Available Balance</div>
            </div>
          </div>
        </div>

        {/* Performance Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<DollarSign className="w-6 h-6" />}
            title="Total Balance"
            value={formatCurrency(balance.total)}
            subtitle={`Available: ${formatCurrency(balance.available)}`}
            color="purple"
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Total P&L"
            value={formatCurrency(performance.total_pnl)}
            subtitle={`Win Rate: ${formatPercent(performance.win_rate)}`}
            color="blue"
            positive={performance.total_pnl > 0}
          />
          <StatCard
            icon={<Activity className="w-6 h-6" />}
            title="Total Trades"
            value={performance.total_trades || 0}
            subtitle={`Winning: ${performance.winning_trades || 0}`}
            color="green"
          />
          <StatCard
            icon={<Target className="w-6 h-6" />}
            title="Open Positions"
            value={performance.open_positions || 0}
            subtitle={`Exposure: ${formatCurrency(performance.total_exposure)}`}
            color="orange"
          />
        </div>

        {/* Positions and Performance Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <PerformanceChart trades={trades} />
          </div>
          <div>
            <PositionsPanel positions={positions} />
          </div>
        </div>

        {/* Decision Log and Trade History */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DecisionLog decisions={decisions} />
          <TradeHistory trades={trades} />
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 pb-8 border-t border-purple-500/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
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
              <span>GPT-4 Turbo</span>
              <span>•</span>
              <span>3x Leverage</span>
              <span>•</span>
              <span>5min Updates</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

const StatCard = ({ icon, title, value, subtitle, color, positive }) => {
  const iconColors = {
    purple: 'text-purple-400',
    blue: 'text-blue-400',
    green: 'text-green-400',
    orange: 'text-orange-400',
  };

  return (
    <div className="bg-slate-900/30 border border-purple-500/10 hover:border-purple-500/30 backdrop-blur-sm rounded-xl p-6 transition-all hover:scale-105">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 ${iconColors[color]}`}>
          {icon}
        </div>
        {positive !== undefined && (
          <div className={`text-lg font-bold ${positive ? 'text-green-400' : 'text-red-400'}`}>
            {positive ? '↗' : '↘'}
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-gray-400">{title}</div>
      {subtitle && <div className="text-xs text-gray-600 mt-2">{subtitle}</div>}
    </div>
  );
};

export default App;

