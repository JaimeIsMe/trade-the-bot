import React from 'react';
import { MessageSquare } from 'lucide-react';
import DecisionLog from './DecisionLog';

const BotTabs = ({ bots, selectedBot, onBotSelect, botDecisions }) => {
  return (
    <div className="bg-black/40 backdrop-blur-md rounded-xl border border-blue-500/30 overflow-hidden neon-border-blue neon-glow-blue">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur-sm border-b border-blue-500/20 px-2 sm:px-3 lg:px-4 py-2 sm:py-3">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-semibold text-white">AI Decisions</h3>
          <span className="text-xs text-gray-400 ml-2">({botDecisions.length} recent)</span>
        </div>
      </div>

      {/* AI Decisions Content */}
      <div className="h-[700px] overflow-y-auto">
        <DecisionLog 
          decisions={botDecisions} 
          title="All Assets AI Decisions" 
        />
      </div>
    </div>
  );
};

export default BotTabs;

