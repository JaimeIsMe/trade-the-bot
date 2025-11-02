import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Target, Award, AlertCircle } from 'lucide-react';

const PerformanceSummary = ({ performance, portfolio }) => {
  // Calculate metrics
  const totalTrades = performance?.total_trades || 0;
  const winRate = performance?.win_rate || 0;
  const totalPnL = performance?.total_pnl || 0;
  const biggestWin = performance?.biggest_win || 0;
  const biggestLoss = performance?.biggest_loss || 0;
  const sharpeRatio = performance?.sharpe_ratio || 0;
  const accountValue = portfolio?.total_balance || 0;
  const fees = performance?.total_fees || 0;
  
  // Calculate return percentage
  const initialCapital = 2000; // $2k starting capital
  const returnPct = accountValue > 0 ? ((accountValue - initialCapital) / initialCapital) * 100 : 0;

  return (
    <div className="p-3 lg:p-4">
      {/* Table */}
      <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
        <table className="w-full border-collapse min-w-[300px]">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-2 lg:py-3 px-3 lg:px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Metric</th>
              <th className="text-right py-2 lg:py-3 px-3 lg:px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Value</th>
            </tr>
          </thead>
          <tbody>
            {/* Account Value */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Account Value</td>
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-medium text-white text-right">
                ${accountValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
            </tr>

            {/* Return */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Return</td>
              <td className={`py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-semibold text-right ${returnPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(2)}%
              </td>
            </tr>

            {/* Total P&L */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Total P&L</td>
              <td className={`py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-semibold text-right ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
            </tr>

            {/* Fees */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Fees</td>
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-medium text-gray-400 text-right">
                ${fees.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
            </tr>

            {/* Win Rate */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Win Rate</td>
              <td className={`py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-semibold text-right ${winRate >= 0.5 ? 'text-green-400' : 'text-orange-400'}`}>
                {(winRate * 100).toFixed(1)}%
              </td>
            </tr>

            {/* Biggest Win */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Biggest Win</td>
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-semibold text-green-400 text-right">
                +${biggestWin.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
            </tr>

            {/* Biggest Loss */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Biggest Loss</td>
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-semibold text-red-400 text-right">
                ${biggestLoss.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
            </tr>

            {/* Sharpe Ratio */}
            <tr className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Sharpe Ratio</td>
              <td className={`py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-semibold text-right ${sharpeRatio >= 1 ? 'text-green-400' : sharpeRatio >= 0.5 ? 'text-yellow-400' : 'text-gray-400'}`}>
                {sharpeRatio.toFixed(3)}
              </td>
            </tr>

            {/* Total Trades */}
            <tr className="hover:bg-gray-800/30 transition-colors">
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm text-gray-300">Total Trades</td>
              <td className="py-2 lg:py-3 px-3 lg:px-4 text-xs lg:text-sm font-medium text-white text-right">
                {totalTrades}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Quick Stats */}
      <div className="mt-4 lg:mt-6 grid grid-cols-3 gap-3 lg:gap-4 pt-4 lg:pt-6 border-t border-gray-800">
        <div className="text-center">
          <div className="text-xl lg:text-2xl font-bold text-purple-400">{totalTrades}</div>
          <div className="text-xs text-gray-500 mt-1">Trades</div>
        </div>
        <div className="text-center">
          <div className={`text-xl lg:text-2xl font-bold ${returnPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {returnPct >= 0 ? '+' : ''}{returnPct.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Return</div>
        </div>
        <div className="text-center">
          <div className={`text-xl lg:text-2xl font-bold ${winRate >= 0.5 ? 'text-green-400' : 'text-orange-400'}`}>
            {(winRate * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Win Rate</div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceSummary;

