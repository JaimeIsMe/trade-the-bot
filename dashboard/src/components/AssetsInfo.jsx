import React from 'react';
import { Coins, TrendingUp, Zap, Shield } from 'lucide-react';

const AssetsInfo = () => {
  const assets = [
    {
      symbol: 'BTC',
      name: 'Bitcoin',
      logo: '/btc-logo.svg',
      description: 'The original cryptocurrency and digital gold standard. Bitcoin is the world\'s first decentralized digital currency, valued for its scarcity, security, and widespread adoption.',
      features: [
        'Market cap leader',
        'High liquidity',
        'Store of value',
        'Institutional adoption'
      ],
      color: 'orange'
    },
    {
      symbol: 'ETH',
      name: 'Ethereum',
      logo: '/eth-logo.svg',
      description: 'The second-largest cryptocurrency and the foundation of decentralized finance (DeFi). Ethereum enables smart contracts and powers thousands of decentralized applications.',
      features: [
        'Smart contract platform',
        'DeFi ecosystem',
        'NFT marketplace',
        'Constant innovation'
      ],
      color: 'gray'
    },
    {
      symbol: 'BNB',
      name: 'Binance Coin',
      logo: '/bnb-logo.svg',
      description: 'The native token of Binance, the world\'s largest cryptocurrency exchange. BNB offers utility across the Binance ecosystem including trading fee discounts and token launches.',
      features: [
        'Exchange utility token',
        'Low transaction fees',
        'Binance ecosystem access',
        'Regular token burns'
      ],
      color: 'yellow'
    },
    {
      symbol: 'SOL',
      name: 'Solana',
      logo: '/sol-logo.svg',
      description: 'A high-performance blockchain platform designed for decentralized apps and crypto projects. Solana offers fast transactions and low fees, making it ideal for DeFi and NFT applications.',
      features: [
        'High transaction speed',
        'Low fees',
        'Growing DeFi ecosystem',
        'NFT marketplace support'
      ],
      color: 'purple'
    },
    {
      symbol: 'ASTER',
      name: 'Aster',
      logo: '/aster_logo.png',
      description: 'The native token of Aster DEX, a decentralized perpetuals exchange. ASTER powers the platform\'s trading ecosystem and provides access to advanced trading features.',
      features: [
        'DEX native token',
        'Perpetuals trading',
        'Trading rewards',
        'Platform governance'
      ],
      color: 'orange'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      orange: 'text-orange-400 border-orange-500/30 bg-orange-500/10',
      gray: 'text-gray-400 border-gray-500/30 bg-gray-500/10',
      yellow: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
      purple: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
      cyan: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10'
    };
    return colors[color] || colors.cyan;
  };

  const getNeonBorderClass = (color) => {
    const borders = {
      orange: 'neon-border-yellow',
      gray: 'neon-border-blue',
      yellow: 'neon-border-yellow',
      purple: 'neon-border-purple',
      cyan: 'neon-border-cyan'
    };
    return borders[color] || borders.cyan;
  };

  const getNeonTextClass = (color) => {
    const texts = {
      orange: 'neon-text-yellow',
      gray: 'neon-text-blue',
      yellow: 'neon-text-yellow',
      purple: 'neon-text-purple',
      cyan: 'neon-text-cyan'
    };
    return texts[color] || texts.cyan;
  };

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
      <div className="bg-black/40 backdrop-blur-md rounded-xl border border-blue-500/30 p-4 sm:p-6 neon-border-blue neon-glow-blue">
        <div className="flex items-center space-x-3 mb-4">
          <Coins className="w-8 h-8 text-blue-400 neon-text-blue" />
          <h1 className="text-2xl font-bold text-white neon-text-blue">Trading Assets</h1>
        </div>
        
        <p className="text-gray-300 mb-6 leading-relaxed">
          Our AI trading system actively monitors and trades across 5 major cryptocurrencies, providing diversification and exposure to different market segments. Each asset offers unique characteristics and trading opportunities.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {assets.map((asset) => (
            <div 
              key={asset.symbol}
              className={`bg-black/60 backdrop-blur-md rounded-lg p-4 sm:p-5 border ${getColorClasses(asset.color)} ${getNeonBorderClass(asset.color)} transition-all hover:border-opacity-50 hover:shadow-lg`}
            >
              <div className="flex items-center space-x-3 mb-3">
                <img 
                  src={asset.logo} 
                  alt={asset.name}
                  className="w-10 h-10 sm:w-12 sm:h-12 rounded-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
                <div className="flex-1">
                  <h3 className={`text-lg sm:text-xl font-bold text-white ${getNeonTextClass(asset.color)}`}>{asset.name}</h3>
                  <span className="text-xs sm:text-sm text-gray-400">{asset.symbol}</span>
                </div>
              </div>
              
              <p className="text-sm text-gray-300 mb-4 leading-relaxed">
                {asset.description}
              </p>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-xs sm:text-sm text-gray-400">
                  <Zap className={`w-4 h-4 ${getNeonTextClass(asset.color)}`} />
                  <span className="font-semibold">Key Features:</span>
                </div>
                <ul className="space-y-1.5 pl-6">
                  {asset.features.map((feature, index) => (
                    <li key={index} className="text-xs sm:text-sm text-gray-400 list-disc">
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-blue-500/30">
          <div className="flex items-center space-x-2 mb-3">
            <TrendingUp className="w-6 h-6 text-green-400 neon-text-green" />
            <h3 className="font-semibold text-white neon-text-green">Trading Strategy</h3>
          </div>
          <p className="text-sm text-gray-400 leading-relaxed mb-4">
            Our AI system analyzes each asset independently, identifying optimal entry and exit points based on technical indicators, market structure, and volatility patterns. By trading across multiple assets simultaneously, we achieve better risk diversification and capitalize on opportunities across different market segments.
          </p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-3 border border-blue-500/30 neon-border-blue">
              <Shield className="w-5 h-5 text-blue-400 mb-2 neon-text-blue" />
              <h4 className="font-semibold text-white mb-1 text-sm neon-text-blue">Risk Management</h4>
              <p className="text-xs text-gray-400">
                Each asset is traded with independent risk parameters, stop-loss levels, and position sizing based on volatility and market conditions.
              </p>
            </div>
            
            <div className="bg-black/60 backdrop-blur-md rounded-lg p-3 border border-green-500/30 neon-border-green">
              <TrendingUp className="w-5 h-5 text-green-400 mb-2 neon-text-green" />
              <h4 className="font-semibold text-white mb-1 text-sm neon-text-green">Market Coverage</h4>
              <p className="text-xs text-gray-400">
                Simultaneous trading across 5 assets provides exposure to different market dynamics, from high-cap stability to emerging opportunities.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetsInfo;
