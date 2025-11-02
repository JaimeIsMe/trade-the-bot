import React from 'react';
import { BookOpen, Brain, TrendingUp, Shield, Target, Zap, BarChart3, Activity } from 'lucide-react';

const Info = () => {
  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
      <div className="bg-black/40 backdrop-blur-md rounded-xl border border-blue-500/30 p-4 sm:p-6 neon-border-blue neon-glow-blue">
        <div className="flex items-center space-x-3 mb-6">
          <BookOpen className="w-8 h-8 text-blue-400 neon-text-blue" />
          <h1 className="text-2xl sm:text-3xl font-bold text-white neon-text-blue">Building Autonomous AI Trading Bots</h1>
        </div>
        
        <div className="space-y-6 text-gray-300">
          {/* Introduction */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-3 neon-text-blue">Why We Built This</h2>
            <p className="leading-relaxed mb-4">
              At <span className="text-blue-400 font-semibold neon-text-blue">Trade The Bot</span>, we set out to answer a fundamental question: 
              <em className="text-gray-400"> Can a large language model act as a systematic trading agent with minimal human guidance?</em>
            </p>
            <p className="leading-relaxed mb-4">
              Unlike traditional trading bots that rely on hardcoded rules and technical indicators, we're exploring whether modern AI—specifically <span className="text-purple-400 font-semibold neon-text-purple">Qwen3 Flash</span>—can autonomously reason about market conditions, assess risk, and execute trades across multiple cryptocurrencies simultaneously. Our goal is to understand how AI behaves in real-world financial markets, where milliseconds matter and every decision has real consequences.
            </p>
            <p className="leading-relaxed">
              We chose cryptocurrency perpetuals trading because markets operate 24/7, data is abundant and auditable, and the decentralized nature of platforms like Aster DEX allows for transparent validation of every trade. This isn't paper trading—we're using real capital in real markets, facing real execution challenges, fees, and market dynamics.
            </p>
          </section>

          {/* What the AI Does */}
          <section className="pt-6 border-t border-blue-500/30">
            <div className="flex items-center space-x-2 mb-4">
              <Brain className="w-6 h-6 text-purple-400 neon-text-purple" />
              <h2 className="text-xl font-semibold text-white neon-text-purple">What Our AI Does</h2>
            </div>
            
            <p className="leading-relaxed mb-4">
              Our trading system deploys <span className="text-purple-400 font-semibold neon-text-purple">Qwen3 Flash</span> as the core decision-making engine across five independent trading bots, each specialized for a different cryptocurrency: <span className="text-orange-400">BTC</span>, <span className="text-gray-400">ETH</span>, <span className="text-yellow-400">BNB</span>, <span className="text-purple-400 neon-text-purple">SOL</span>, and <span className="text-orange-400">ASTER</span>. Each bot operates autonomously, analyzing market conditions and making trading decisions every few minutes.
            </p>

            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue neon-glow-blue mb-4">
              <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-blue-400 neon-text-blue" />
                <span className="neon-text-blue">Market Analysis Process</span>
              </h3>
              <p className="text-sm text-gray-400 mb-3">
                At each decision point (~2-3 minutes), the AI receives:
              </p>
              <ul className="list-disc list-inside space-y-2 text-sm text-gray-400 ml-2">
                <li><span className="text-white">Multi-timeframe price data:</span> Current and historical prices across 1m, 5m, 15m, 1h, and 4h intervals</li>
                <li><span className="text-white">Technical indicators:</span> RSI, MACD, Bollinger Bands, ATR (Average True Range), and volume analysis</li>
                <li><span className="text-white">Market structure:</span> Support/resistance levels, trend identification, volatility metrics</li>
                <li><span className="text-white">Account state:</span> Current positions, available balance, unrealized P&L, margin ratios</li>
                <li><span className="text-white">Open orders:</span> Active stop-loss and take-profit orders</li>
              </ul>
            </div>

            <p className="leading-relaxed">
              The AI processes this information, reasons about market conditions, and generates a structured trading decision with justification, confidence score, and exit plan. This happens autonomously—no human intervention required.
            </p>
          </section>

          {/* Decision Space */}
          <section className="pt-6 border-t border-blue-500/30">
            <div className="flex items-center space-x-2 mb-4">
              <Target className="w-6 h-6 text-green-400 neon-text-green" />
              <h2 className="text-xl font-semibold text-white neon-text-green">What Decisions Can the AI Make?</h2>
            </div>

            <p className="leading-relaxed mb-4">
              Each bot has a constrained but flexible action space, designed to balance autonomy with risk control:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-green-500/30 neon-border-green neon-glow-green">
                <h3 className="font-semibold text-white mb-2 flex items-center space-x-2">
                  <TrendingUp className="w-5 h-5 text-green-400 neon-text-green" />
                  <span className="neon-text-green">Entry Actions</span>
                </h3>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><span className="text-green-400 font-semibold neon-text-green">BUY (Long):</span> Enter a position betting the price will rise</li>
                  <li><span className="text-red-400 font-semibold">SELL (Short):</span> Enter a position betting the price will fall</li>
                  <li><span className="text-gray-400 font-semibold">HOLD:</span> Wait for better opportunities</li>
                </ul>
              </div>

              <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-red-500/30">
                <h3 className="font-semibold text-white mb-2 flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-red-400" />
                  <span>Exit Actions</span>
                </h3>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><span className="text-white font-semibold">CLOSE:</span> Exit current position</li>
                  <li><span className="text-white font-semibold">Auto-exit:</span> Triggered by stop-loss or take-profit levels</li>
                  <li><span className="text-white font-semibold">Position management:</span> Can close positions independently of entry decisions</li>
                </ul>
              </div>
            </div>

            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-purple-500/30 neon-border-purple neon-glow-purple">
              <h3 className="font-semibold text-white mb-3 neon-text-purple">Each Decision Includes:</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-400">
                <div className="flex items-start space-x-2">
                  <Target className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0 neon-text-purple" />
                  <div>
                    <span className="text-white font-semibold">Confidence Score:</span> Self-reported 0-100% confidence in the decision
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Activity className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0 neon-text-blue" />
                  <div>
                    <span className="text-white font-semibold">Position Size:</span> Quantity determined by confidence and available capital
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <TrendingUp className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0 neon-text-green" />
                  <div>
                    <span className="text-white font-semibold">Take Profit:</span> Price target for profit-taking
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Shield className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="text-white font-semibold">Stop Loss:</span> Price level that triggers automatic exit
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-800">
                The AI must provide justification for each decision, explaining its reasoning based on technical analysis, market conditions, and risk assessment.
              </p>
            </div>
          </section>

          {/* Leverage, TP, SL */}
          <section className="pt-6 border-t border-blue-500/30">
            <div className="flex items-center space-x-2 mb-4">
              <Zap className="w-6 h-6 text-yellow-400" />
              <h2 className="text-xl font-semibold text-white">Trading Parameters</h2>
            </div>

            <div className="space-y-4">
              <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-yellow-500/30">
                <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <span>Leverage</span>
                </h3>
                <p className="text-sm text-gray-400 mb-3">
                  Each bot uses <span className="text-yellow-400 font-semibold">5x leverage</span> by default, allowing positions to be 5x larger than the capital allocated. This amplifies both profits and losses:
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-400 ml-2">
                  <li>Leverage is set per-symbol and can be adjusted by the AI if market conditions warrant</li>
                  <li>5x leverage means a $100 position requires $20 in margin</li>
                  <li>Leverage amplifies P&L: a 1% price move = 5% P&L at 5x leverage</li>
                  <li>All bots start with 5x leverage and maintain it unless explicitly changed</li>
                </ul>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-green-500/30 neon-border-green neon-glow-green">
                  <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
                    <Target className="w-5 h-5 text-green-400 neon-text-green" />
                    <span className="neon-text-green">Take Profit (TP)</span>
                  </h3>
                  <p className="text-sm text-gray-400 mb-3">
                    The AI sets <span className="text-green-400 font-semibold neon-text-green">dynamic take-profit targets</span> based on:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-400 ml-2">
                    <li>Technical resistance levels</li>
                    <li>ATR-based volatility estimates</li>
                    <li>Risk/reward ratios (typically 1.5:1 to 3:1)</li>
                    <li>Market structure and trend strength</li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-3 pt-2 border-t border-gray-800">
                    TP levels are typically 1-3% above entry for longs, adjusted based on volatility and confidence.
                  </p>
                </div>

                <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-red-500/30">
                  <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-red-400" />
                    <span>Stop Loss (SL)</span>
                  </h3>
                  <p className="text-sm text-gray-400 mb-3">
                    Stop-loss levels are calculated using:
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-400 ml-2">
                    <li>ATR-based volatility (typically 1-2x ATR)</li>
                    <li>Support/resistance levels</li>
                    <li>Risk management rules (max 2-3% loss per trade)</li>
                    <li>Margin requirements and liquidation risk</li>
                  </ul>
                  <p className="text-xs text-gray-500 mt-3 pt-2 border-t border-gray-800">
                    SL is typically 0.5-2% below entry for longs, tighter for volatile assets, looser for stable trends.
                  </p>
                </div>
              </div>

              <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue neon-glow-blue">
                <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-blue-400 neon-text-blue" />
                  <span className="neon-text-blue">Position Sizing</span>
                </h3>
                <p className="text-sm text-gray-400 mb-3">
                  Position sizes are determined dynamically based on:
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-400 ml-2">
                  <li><span className="text-white font-semibold">AI confidence score:</span> Higher confidence = larger position size</li>
                  <li><span className="text-white font-semibold">Available capital:</span> Respects margin requirements and account constraints</li>
                  <li><span className="text-white font-semibold">Risk per trade:</span> Typically 1-5% of account balance per position</li>
                  <li><span className="text-white font-semibold">Volatility:</span> Smaller sizes in high volatility, larger in stable trends</li>
                  <li><span className="text-white font-semibold">Portfolio diversification:</span> Considers existing positions across all 5 bots</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Risk Management */}
          <section className="pt-6 border-t border-blue-500/30">
            <div className="flex items-center space-x-2 mb-4">
              <Shield className="w-6 h-6 text-blue-400 neon-text-blue" />
              <h2 className="text-xl font-semibold text-white neon-text-blue">Risk Management & Constraints</h2>
            </div>

            <div className="space-y-4">
              <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue">
                <h3 className="font-semibold text-white mb-3">Built-in Safety Mechanisms</h3>
                <ul className="list-disc list-inside space-y-2 text-sm text-gray-400">
                  <li><span className="text-white font-semibold">Margin monitoring:</span> Bots cannot exceed available margin or trigger liquidation</li>
                  <li><span className="text-white font-semibold">Maximum position limits:</span> Each bot respects portfolio-level constraints</li>
                  <li><span className="text-white font-semibold">Overtrading protection:</span> Built-in mechanisms prevent excessive trading frequency</li>
                  <li><span className="text-white font-semibold">Fee awareness:</span> AI considers trading fees when evaluating small profit opportunities</li>
                  <li><span className="text-white font-semibold">Sharpe ratio feedback:</span> Bots receive their risk-adjusted returns to encourage better risk management</li>
                </ul>
              </div>

              <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue">
                <h3 className="font-semibold text-white mb-3">What the AI Cannot Do</h3>
                <ul className="list-disc list-inside space-y-2 text-sm text-gray-400">
                  <li>Cannot access external news or social media sentiment (technical analysis only)</li>
                  <li>Cannot see other bots' positions or decisions (independent operation)</li>
                  <li>Cannot modify leverage mid-position (set at entry)</li>
                  <li>Cannot pyramid positions (add to existing positions)</li>
                  <li>Cannot exceed hard limits on position size or margin usage</li>
                  <li>Cannot trade assets outside the 5-asset universe (BTC, ETH, SOL, BNB, ASTER)</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Frequency & Strategy */}
          <section className="pt-6 border-t border-blue-500/30">
            <h2 className="text-xl font-semibold text-white mb-4 neon-text-blue">Trading Frequency & Strategy</h2>
            
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-4 border border-blue-500/30 neon-border-blue neon-glow-blue mb-4">
              <p className="text-sm text-gray-400 leading-relaxed mb-3">
                Our bots engage in <span className="text-white font-semibold">mid-to-low frequency trading (MLFT)</span>, making decisions every 2-3 minutes rather than microseconds. This frequency allows the AI to:
              </p>
              <ul className="list-disc list-inside space-y-2 text-sm text-gray-400 ml-2">
                <li>Process comprehensive market data and technical indicators</li>
                <li>Reason about market conditions without rushing</li>
                <li>Balance trading activity with fee costs</li>
                <li>Maintain coherent strategies over time</li>
              </ul>
            </div>

            <p className="text-sm text-gray-400 leading-relaxed">
              Each bot operates independently, analyzing its assigned cryptocurrency and making decisions based solely on that asset's market data. There's no coordination between bots—each is a separate AI agent competing for capital allocation within the shared portfolio. This design allows us to observe how AI behaves across different market conditions and asset characteristics.
            </p>
          </section>

          {/* Conclusion */}
          <section className="pt-6 border-t border-blue-500/30">
            <h2 className="text-xl font-semibold text-white mb-4 neon-text-blue">The Goal</h2>
            <p className="leading-relaxed text-gray-300 mb-4">
              Our objective isn't to build the perfect trading bot—it's to understand how modern AI systems behave in real-world financial markets. We're exploring questions like:
            </p>
            <ul className="list-disc list-inside space-y-2 text-sm text-gray-400 mb-4 ml-2">
              <li>Can LLMs reliably follow risk management rules?</li>
              <li>Do different models show consistent behavioral patterns?</li>
              <li>Where do AI agents fail, and how can we improve them?</li>
              <li>What capabilities are needed for truly autonomous trading?</li>
            </ul>
            <p className="leading-relaxed text-gray-300">
              By running live with real capital, we gain insights that paper trading cannot provide: real execution challenges, fee impacts, adverse selection, and the full operational stack. Every trade is auditable on-chain, and every decision is transparent. This transparency is part of our methodology—we believe evaluating AI in consequential, realistic environments is the fastest path to understanding both its capabilities and limitations.
            </p>
            <p className="text-sm text-gray-400 mt-4 pt-4 border-t border-blue-500/30">
              <em className="text-blue-400 neon-text-blue">Trade The Bot</em> represents an ongoing experiment in autonomous AI trading. Season 1 focuses on understanding baseline behavior and risk management. Future iterations will introduce more sophisticated features, improved prompts, and statistical rigor as we continue to push the boundaries of what AI can achieve in financial markets.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Info;

