import React from 'react';
import { Target } from 'lucide-react';

const PositionsPanel = ({ positions, compact = false }) => {
  const positionList = Array.isArray(positions) ? positions : [];

  if (compact) {
    // Compact version for dual strategy view
    return (
      <div className="space-y-2">
        {positionList.length === 0 ? (
          <div className="text-center text-gray-500 py-4 text-sm">
            No open positions
          </div>
        ) : (
          positionList.map((position, index) => (
            <PositionCard key={index} position={position} compact={true} />
          ))
        )}
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="space-y-4">
        {positionList.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No open positions
          </div>
        ) : (
          positionList.map((position, index) => (
            <PositionCard key={index} position={position} />
          ))
        )}
      </div>
    </div>
  );
};

const PositionCard = ({ position, compact = false }) => {
  const symbol = position.symbol || 'Unknown';
  const side = position.side || 'long';
  const pnl = position.unrealized_pnl || 0;
  const entryPrice = position.entry_price || 0;
  const size = position.size || 0;
  const leverage = position.leverage || 1;
  const notional = position.notional || 0;
  const pnlPercent = notional > 0 ? (pnl / notional) * 100 : 0;

  if (compact) {
    return (
      <div className="bg-black/30 rounded-lg p-3 border border-purple-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {side.toUpperCase()}
            </div>
            <span className="text-sm text-gray-300">${notional.toFixed(0)}</span>
          </div>
          <div className="text-right">
            <div className={`font-bold text-sm ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {pnl >= 0 ? '+' : ''}${Math.abs(pnl).toFixed(2)}
            </div>
            <div className={`text-xs ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-black/30 rounded-lg p-4 border border-purple-500/10 hover:border-purple-500/30 transition-all">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="font-bold text-white">{symbol}</div>
          <div className={`text-xs font-bold px-2 py-0.5 rounded-full inline-block ${
            side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {side.toUpperCase()}
          </div>
        </div>
        <div className="text-right">
          <div className={`font-bold text-lg ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {pnl >= 0 ? '+' : ''}${Math.abs(pnl).toFixed(4)}
          </div>
          <div className={`text-sm ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div>
          <div className="text-gray-500">Entry Price</div>
          <div className="text-gray-300">${entryPrice.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-gray-500">Notional</div>
          <div className="text-gray-300">${notional.toFixed(2)}</div>
        </div>
        <div>
          <div className="text-gray-500">Size</div>
          <div className="text-gray-300">{size.toFixed(3)} BTC</div>
        </div>
        <div>
          <div className="text-gray-500">Leverage</div>
          <div className="text-gray-300">{leverage}x</div>
        </div>
      </div>
    </div>
  );
};

export default PositionsPanel;

