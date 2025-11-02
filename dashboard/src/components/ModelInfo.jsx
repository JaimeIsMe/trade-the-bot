import React from 'react';
import { Brain, Zap, TrendingUp, Shield, Globe, Sparkles } from 'lucide-react';

const ModelInfo = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-black/40 backdrop-blur-md rounded-xl border border-blue-500/30 p-6 neon-border-blue neon-glow-blue">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="w-8 h-8 text-purple-400 neon-text-purple" />
          <h1 className="text-2xl font-bold text-white neon-text-blue">AI Trading Model</h1>
        </div>
        
        <div className="space-y-4 text-gray-300">
          <p className="leading-relaxed">
            Our multi-bot trading system leverages <span className="text-purple-400 font-semibold neon-text-purple">Qwen3 Flash</span>, a state-of-the-art large language model by Alibaba Cloud, to analyze cryptocurrency markets across multiple timeframes and assets simultaneously. This advanced AI provides exceptional speed and accuracy for real-time trading decisions.
          </p>
          
          <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-purple-500/30 neon-border-purple neon-glow-purple">
            <div className="flex items-center space-x-2 mb-3">
              <Sparkles className="w-5 h-5 text-purple-400 neon-text-purple" />
              <h3 className="font-semibold text-white neon-text-purple">Powered by Qwen3 Flash</h3>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              Qwen3 Flash combines lightning-fast inference with deep market understanding, enabling our bots to process complex technical analysis, evaluate multiple indicators simultaneously, and generate confident trading signals with precise entry and exit recommendations in real-time.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue">
              <Zap className="w-6 h-6 text-yellow-400 mb-2 neon-text-yellow" />
              <h3 className="font-semibold text-white mb-2 neon-text-blue">Multi-Timeframe Analysis</h3>
              <p className="text-sm text-gray-400">
                Simultaneously analyzes 1m, 5m, 15m, 1h, and 4h charts to identify optimal entry and exit points.
              </p>
            </div>
            
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-green-500/30 neon-border-green">
              <TrendingUp className="w-6 h-6 text-green-400 mb-2 neon-text-green" />
              <h3 className="font-semibold text-white mb-2 neon-text-green">Technical Indicators</h3>
              <p className="text-sm text-gray-400">
                Utilizes RSI, MACD, Bollinger Bands, ATR, and volume analysis to make data-driven decisions.
              </p>
            </div>
            
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue neon-glow-blue">
              <Shield className="w-6 h-6 text-blue-400 mb-2 neon-text-blue" />
              <h3 className="font-semibold text-white mb-2 neon-text-blue">Risk Management</h3>
              <p className="text-sm text-gray-400">
                Implements dynamic stop-loss and take-profit levels, position sizing, and leverage management to protect capital.
              </p>
            </div>
            
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-cyan-500/30 neon-border-cyan">
              <Globe className="w-6 h-6 text-cyan-400 mb-2 neon-text-cyan" />
              <h3 className="font-semibold text-white mb-2 neon-text-cyan">Multi-Asset Trading</h3>
              <p className="text-sm text-gray-400">
                Monitors and trades 5 major cryptocurrencies (ASTER, BTC, ETH, SOL, BNB) concurrently for diversification.
              </p>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-blue-500/30">
            <div className="flex items-center space-x-3 mb-4">
              <Sparkles className="w-6 h-6 text-purple-400 neon-text-purple" />
              <h3 className="font-semibold text-white text-lg neon-text-purple">Model Approach</h3>
            </div>
            
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-purple-500/30 neon-border-purple neon-glow-purple mb-4">
              <p className="text-sm text-gray-300 leading-relaxed mb-3">
                Our trading system utilizes <span className="text-purple-400 font-semibold neon-text-purple">Qwen3 Flash</span>, a state-of-the-art large language model developed by Alibaba Cloud. Qwen3 Flash represents a breakthrough in AI-powered market analysis, offering exceptional speed and accuracy for real-time trading decisions.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                <div className="flex items-start space-x-2">
                  <Zap className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0 neon-text-yellow" />
                  <div>
                    <span className="text-xs font-semibold text-white">Ultra-Fast Processing</span>
                    <p className="text-xs text-gray-400 mt-1">Lightning-fast inference enables real-time market analysis and instant decision-making.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-2">
                  <Brain className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0 neon-text-purple" />
                  <div>
                    <span className="text-xs font-semibold text-white">Advanced Reasoning</span>
                    <p className="text-xs text-gray-400 mt-1">Deep understanding of market patterns, technical indicators, and risk assessment.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-2">
                  <TrendingUp className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0 neon-text-green" />
                  <div>
                    <span className="text-xs font-semibold text-white">Cost-Effective</span>
                    <p className="text-xs text-gray-400 mt-1">Optimized model architecture provides enterprise-grade performance at lower costs.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-2">
                  <Shield className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0 neon-text-blue" />
                  <div>
                    <span className="text-xs font-semibold text-white">Reliable & Stable</span>
                    <p className="text-xs text-gray-400 mt-1">Consistent performance across diverse market conditions and trading scenarios.</p>
                  </div>
                </div>
              </div>
              
              <p className="text-xs text-gray-400 mt-4 pt-3 border-t border-gray-800">
                Qwen3 Flash's combination of speed and intelligence makes it ideal for cryptocurrency trading, where milliseconds matter and market conditions change rapidly. The model processes complex technical analysis, evaluates multiple indicators simultaneously, and generates confident trading signals with precise entry and exit recommendations.
              </p>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-blue-500/30">
            <ul className="list-disc list-inside space-y-2 text-sm text-gray-400">
              <li><span className="text-purple-400 neon-text-purple">Qwen3 Flash</span> processes real-time market data across multiple exchanges with ultra-fast inference</li>
              <li>Confidence-based trading with dynamic position sizing determined by AI analysis</li>
              <li>Automatic execution of trades based on AI-generated signals and market conditions</li>
              <li>Continuous learning from market patterns and trading outcomes</li>
              <li>Built-in anti-overtrading mechanisms to maintain discipline and risk control</li>
            </ul>
          </div>
          
          <div className="mt-6 pt-4 border-t border-blue-500/30">
            <p className="text-sm text-gray-400 leading-relaxed">
              The system operates autonomously, with <span className="text-purple-400 font-semibold neon-text-purple">Qwen3 Flash</span> making intelligent trading decisions based on technical analysis, market sentiment, and risk parameters. The model's combination of speed and intelligence makes it ideal for cryptocurrency trading, where milliseconds matter and market conditions change rapidly.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelInfo;
