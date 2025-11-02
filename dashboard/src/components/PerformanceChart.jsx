import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';

const PerformanceChart = ({ trades }) => {
  const chartData = useMemo(() => {
    if (!trades || trades.length === 0) return [];

    let cumulativePnL = 0;
    return trades.map((trade, index) => {
      cumulativePnL += trade.pnl || 0;
      return {
        index: index + 1,
        pnl: cumulativePnL,
        timestamp: new Date(trade.timestamp).toLocaleTimeString(),
      };
    });
  }, [trades]);

  return (
    <div className="bg-slate-900/30 backdrop-blur-sm border border-purple-500/10 rounded-xl p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10">
          <TrendingUp className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Performance Chart</h2>
          <p className="text-xs text-gray-500">Cumulative P&L</p>
        </div>
      </div>

      {chartData.length === 0 ? (
        <div className="text-center text-gray-500 py-24">
          No trading data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              dataKey="index" 
              stroke="#64748b"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#64748b"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #8b5cf6',
                borderRadius: '8px',
                color: '#f1f5f9'
              }}
              formatter={(value) => [`$${value.toFixed(2)}`, 'P&L']}
            />
            <Line
              type="monotone"
              dataKey="pnl"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: '#8b5cf6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default PerformanceChart;

