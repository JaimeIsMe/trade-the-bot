import React from 'react';
import { History, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const TradeHistory = ({ trades }) => {
  return (
    <div className="p-4">
      <div className="space-y-3 overflow-y-auto">
        {trades.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No trades yet
          </div>
        ) : (
          trades.slice().reverse().map((trade, index) => (
            <TradeCard key={index} trade={trade} />
          ))
        )}
      </div>
    </div>
  );
};

const TradeCard = ({ trade }) => {
  const action = trade.action || 'unknown';
  const pnl = trade.pnl || 0;
  
  const actionColors = {
    long: 'text-green-400',
    short: 'text-red-400',
    close: 'text-yellow-400',
  };

  return (
    <div className="bg-black/30 rounded-lg p-3 border border-purple-500/10 hover:border-purple-500/30 transition-all hover:bg-black/50">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className={`text-sm font-bold ${actionColors[action] || 'text-gray-400'}`}>
              {action.toUpperCase()}
            </span>
            {trade.order?.symbol && (
              <span className="text-sm text-gray-400">{trade.order.symbol}</span>
            )}
          </div>
          
          {trade.order && (
            <div className="text-xs text-gray-500 space-y-1">
              {trade.order.size && (
                <div>Size: ${parseFloat(trade.order.size).toLocaleString()}</div>
              )}
              {trade.order.price && parseFloat(trade.order.price) > 0 && (
                <div>Price: ${parseFloat(trade.order.price).toFixed(2)}</div>
              )}
              {trade.order.avgPrice && parseFloat(trade.order.avgPrice) > 0 && (
                <div>Avg Price: ${parseFloat(trade.order.avgPrice).toFixed(2)}</div>
              )}
            </div>
          )}
        </div>

        <div className="text-right">
          {pnl !== 0 && (
            <div className={`text-sm font-semibold mb-1 ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
            </div>
          )}
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>
              {trade.timestamp ? formatDistanceToNow(new Date(trade.timestamp), { addSuffix: true }) : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeHistory;

