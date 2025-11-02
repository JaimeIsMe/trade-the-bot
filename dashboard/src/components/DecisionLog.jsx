import React from 'react';
import { Brain, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const DecisionLog = ({ decisions, title = "AI Decision Log" }) => {
  // Sort decisions by timestamp (newest first)
  const sortedDecisions = [...decisions].sort((a, b) => {
    const timeA = a.timestamp || 0;
    const timeB = b.timestamp || 0;
    return timeB - timeA; // Descending order (newest first)
  });

  return (
    <div className="p-4">
      <div className="space-y-2.5 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent">
        {sortedDecisions.length === 0 ? (
          <div className="text-center text-gray-500 py-12 text-sm">
            No decisions yet
          </div>
        ) : (
          sortedDecisions.map((log, index) => (
            <DecisionCard key={index} log={log} />
          ))
        )}
      </div>
    </div>
  );
};

const DecisionCard = ({ log }) => {
  const decision = log.decision || {};
  const action = decision.action || 'hold';
  
  const actionColors = {
    long: 'bg-green-500/20 text-green-400 border-green-500/30',
    short: 'bg-red-500/20 text-red-400 border-red-500/30',
    close: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    hold: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  return (
    <div className="bg-[#111111] rounded-xl p-3 lg:p-4 border border-gray-800/30 hover:border-gray-700/50 transition-all">
      <div className="flex items-start justify-between mb-2 lg:mb-3">
        <div className="flex items-center space-x-1.5 lg:space-x-2">
          <span className={`px-2 lg:px-2.5 py-0.5 lg:py-1 rounded-lg text-xs font-semibold border ${actionColors[action] || actionColors.hold}`}>
            {action.toUpperCase()}
          </span>
          {(log.asset || decision.symbol || log.symbol) && (
            <span className="text-xs lg:text-sm font-medium text-blue-400">
              {log.asset || (decision.symbol || log.symbol || '').replace('USDT', '')}
            </span>
          )}
        </div>
        <div className="flex items-center space-x-1 text-xs text-gray-500">
          <Clock className="w-3 h-3 lg:w-3.5 lg:h-3.5" />
          <span>
            {log.timestamp ? formatDistanceToNow(new Date(log.timestamp), { addSuffix: true }) : 'N/A'}
          </span>
        </div>
      </div>

      {decision.reasoning && (
        <div className="mb-2 lg:mb-3 max-h-32 overflow-y-auto pr-2 custom-scrollbar">
          <p className="text-xs lg:text-sm text-gray-400 leading-relaxed">
            {decision.reasoning}
          </p>
        </div>
      )}

      <div className="flex items-center justify-between text-xs pt-2 border-t border-gray-800/50">
        {decision.confidence !== undefined && (
          <div className="flex items-center space-x-1.5">
            <span className="text-gray-600">Confidence:</span>
            <span className={`font-semibold ${
              decision.confidence > 70 ? 'text-green-400' :
              decision.confidence > 40 ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              {decision.confidence}%
            </span>
          </div>
        )}
        {decision.size && (
          <span className="text-gray-600">
            Size: ${decision.size.toLocaleString()}
          </span>
        )}
      </div>

      {(decision.stop_loss || decision.take_profit) && (
        <div className="mt-2 pt-2 border-t border-slate-600/30 flex items-center justify-between text-xs">
          {decision.stop_loss && (
            <span className="text-red-400">SL: ${decision.stop_loss}</span>
          )}
          {decision.take_profit && (
            <span className="text-green-400">TP: ${decision.take_profit}</span>
          )}
        </div>
      )}
    </div>
  );
};

export default DecisionLog;

