import React, { useState } from 'react';
import { LineChart as LineChartIcon, BarChart3, TrendingUp, PieChart as PieChartIcon } from 'lucide-react';
import BotPerformanceChart from './BotPerformanceChart';
import AdditionalCharts from './AdditionalCharts';

const ChartsContainer = ({ trades, performance, symbol, allBotsTrades, bots }) => {
  const [activeTab, setActiveTab] = useState('cumulative');

  const tabs = [
    { id: 'cumulative', label: 'Cumulative P&L', icon: LineChartIcon },
    { id: 'individual', label: 'Individual Trades', icon: BarChart3 },
    { id: 'distribution', label: 'Distribution', icon: BarChart3 },
    { id: 'comparison', label: 'Asset Comparison', icon: PieChartIcon },
    { id: 'trends', label: 'Win Rate Trends', icon: TrendingUp },
  ];

  return (
    <div className="space-y-4">
      {/* Tab Navigation */}
      <div className="flex items-center space-x-1.5 sm:space-x-2 border-b border-gray-800/50 pb-2 sm:pb-3 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent -mx-2 px-2 sm:mx-0 sm:px-0">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-1.5 sm:space-x-2 px-2.5 sm:px-3 lg:px-4 py-2 sm:py-2 rounded-lg transition-all whitespace-nowrap flex-shrink-0 text-xs sm:text-sm ${
                activeTab === tab.id
                  ? 'bg-blue-600/30 border border-blue-500/50 text-white neon-glow-blue'
                  : 'text-gray-400 hover:text-white hover:bg-blue-500/10'
              }`}
            >
              <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {(activeTab === 'cumulative' || activeTab === 'individual') && (
        <BotPerformanceChart 
          trades={trades} 
          performance={performance}
          symbol={symbol}
          allBotsTrades={allBotsTrades}
          bots={bots}
          viewMode={activeTab} // 'cumulative' or 'individual'
        />
      )}
      
      {(activeTab === 'distribution' || activeTab === 'comparison' || activeTab === 'trends') && (
        <AdditionalCharts 
          allBotsTrades={allBotsTrades}
          viewMode={activeTab} // 'distribution', 'comparison', or 'trends'
        />
      )}
    </div>
  );
};

export default ChartsContainer;


