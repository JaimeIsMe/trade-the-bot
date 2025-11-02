"""
Momentum Trading Strategy
Example strategy that can be used as a template
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class MomentumStrategy:
    """
    Simple momentum-based trading strategy
    Can be used in conjunction with or as input to the AI agent
    """
    
    def __init__(self, lookback_period: int = 20, threshold: float = 0.02):
        """
        Initialize momentum strategy
        
        Args:
            lookback_period: Number of periods to look back for momentum calculation
            threshold: Minimum momentum threshold to generate signal
        """
        self.lookback_period = lookback_period
        self.threshold = threshold
        self.price_history: Dict[str, List[Dict]] = {}
    
    def update_price(self, symbol: str, price: float, timestamp: datetime):
        """Update price history for a symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            "price": price,
            "timestamp": timestamp
        })
        
        # Keep only recent history
        if len(self.price_history[symbol]) > self.lookback_period * 2:
            self.price_history[symbol] = self.price_history[symbol][-self.lookback_period * 2:]
    
    def calculate_momentum(self, symbol: str) -> float:
        """
        Calculate price momentum for a symbol
        
        Returns:
            Momentum value (positive = upward, negative = downward)
        """
        if symbol not in self.price_history:
            return 0.0
        
        history = self.price_history[symbol]
        if len(history) < self.lookback_period:
            return 0.0
        
        recent_prices = history[-self.lookback_period:]
        oldest_price = recent_prices[0]["price"]
        current_price = recent_prices[-1]["price"]
        
        momentum = (current_price - oldest_price) / oldest_price
        return momentum
    
    def get_signal(self, symbol: str) -> Dict[str, Any]:
        """
        Get trading signal for a symbol
        
        Returns:
            Dictionary with signal information
        """
        momentum = self.calculate_momentum(symbol)
        
        if abs(momentum) < self.threshold:
            return {
                "signal": "neutral",
                "momentum": momentum,
                "strength": 0
            }
        
        if momentum > 0:
            signal = "bullish"
            strength = min(momentum / (self.threshold * 3), 1.0)
        else:
            signal = "bearish"
            strength = min(abs(momentum) / (self.threshold * 3), 1.0)
        
        return {
            "signal": signal,
            "momentum": momentum,
            "strength": strength
        }
    
    def get_analysis(self, symbol: str) -> str:
        """
        Get human-readable analysis for a symbol
        
        Returns:
            Analysis string that can be fed to LLM
        """
        signal = self.get_signal(symbol)
        momentum = signal["momentum"]
        
        analysis = f"""
        Momentum Analysis for {symbol}:
        - Current momentum: {momentum * 100:.2f}%
        - Signal: {signal['signal'].upper()}
        - Strength: {signal['strength'] * 100:.0f}%
        - Lookback period: {self.lookback_period} intervals
        """
        
        return analysis.strip()

