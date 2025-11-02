"""
Technical Indicators Module
Provides advanced market analysis indicators for aggressive trading
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from loguru import logger


class TechnicalIndicators:
    """
    Calculate technical indicators for trading decisions
    """
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        
        Args:
            prices: List of closing prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral if not enough data
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def calculate_macd(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: List of closing prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        if len(prices) < slow_period + signal_period:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        prices_array = np.array(prices)
        
        # Calculate EMAs
        fast_ema = TechnicalIndicators._calculate_ema(prices_array, fast_period)
        slow_ema = TechnicalIndicators._calculate_ema(prices_array, slow_period)
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Signal line (EMA of MACD)
        signal_line = TechnicalIndicators._calculate_ema(macd_line, signal_period)
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            "macd": float(macd_line[-1]),
            "signal": float(signal_line[-1]),
            "histogram": float(histogram[-1])
        }
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, float]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: List of closing prices
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dictionary with upper, middle, and lower bands
        """
        if len(prices) < period:
            current_price = prices[-1]
            return {
                "upper": current_price,
                "middle": current_price,
                "lower": current_price,
                "width": 0.0,
                "position": 0.5
            }
        
        prices_array = np.array(prices[-period:])
        sma = np.mean(prices_array)
        std = np.std(prices_array)
        
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        # Calculate band width (volatility measure)
        width = (upper - lower) / sma if sma > 0 else 0
        
        # Calculate price position within bands (0 = lower, 1 = upper)
        current_price = prices[-1]
        position = (current_price - lower) / (upper - lower) if upper > lower else 0.5
        
        return {
            "upper": float(upper),
            "middle": float(sma),
            "lower": float(lower),
            "width": float(width),
            "position": float(position)
        }
    
    @staticmethod
    def calculate_atr(
        highs: List[float],
        lows: List[float],
        closes: List[float],
        period: int = 14
    ) -> float:
        """
        Calculate Average True Range (volatility measure)
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ATR period
            
        Returns:
            ATR value
        """
        if len(highs) < period + 1:
            # Fallback to simple range
            return float(np.mean([h - l for h, l in zip(highs[-period:], lows[-period:])]))
        
        true_ranges = []
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        atr = np.mean(true_ranges[-period:])
        return float(atr)
    
    @staticmethod
    def calculate_volume_profile(
        volumes: List[float],
        period: int = 20
    ) -> Dict[str, float]:
        """
        Calculate volume profile metrics
        
        Args:
            volumes: List of volume values
            period: Lookback period
            
        Returns:
            Dictionary with volume metrics
        """
        if len(volumes) < period:
            return {
                "avg_volume": 0.0,
                "volume_ratio": 1.0,
                "volume_trend": 0.0
            }
        
        recent_volumes = np.array(volumes[-period:])
        avg_volume = np.mean(recent_volumes)
        current_volume = volumes[-1]
        
        # Volume ratio (current vs average)
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Volume trend (recent vs older)
        recent_avg = np.mean(volumes[-5:]) if len(volumes) >= 5 else avg_volume
        older_avg = np.mean(volumes[-period:-5]) if len(volumes) >= period else avg_volume
        volume_trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0.0
        
        return {
            "avg_volume": float(avg_volume),
            "volume_ratio": float(volume_ratio),
            "volume_trend": float(volume_trend)
        }
    
    @staticmethod
    def calculate_momentum(prices: List[float], period: int = 10) -> float:
        """
        Calculate momentum (rate of change)
        
        Args:
            prices: List of closing prices
            period: Lookback period
            
        Returns:
            Momentum percentage
        """
        if len(prices) < period + 1:
            return 0.0
        
        current = prices[-1]
        past = prices[-period-1]
        
        momentum = ((current - past) / past) * 100 if past > 0 else 0.0
        return float(momentum)
    
    @staticmethod
    def detect_trend(prices: List[float], short_period: int = 20, long_period: int = 50) -> Dict[str, Any]:
        """
        Detect trend using moving averages
        
        Args:
            prices: List of closing prices
            short_period: Short MA period
            long_period: Long MA period
            
        Returns:
            Dictionary with trend information
        """
        if len(prices) < long_period:
            return {
                "trend": "neutral",
                "strength": 0.0,
                "short_ma": prices[-1] if prices else 0,
                "long_ma": prices[-1] if prices else 0
            }
        
        short_ma = np.mean(prices[-short_period:])
        long_ma = np.mean(prices[-long_period:])
        
        # Determine trend
        if short_ma > long_ma * 1.01:  # 1% threshold
            trend = "bullish"
        elif short_ma < long_ma * 0.99:
            trend = "bearish"
        else:
            trend = "neutral"
        
        # Calculate trend strength
        strength = abs(short_ma - long_ma) / long_ma if long_ma > 0 else 0.0
        
        return {
            "trend": trend,
            "strength": float(strength),
            "short_ma": float(short_ma),
            "long_ma": float(long_ma)
        }
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> Dict[str, float]:
        """
        Calculate volatility metrics
        
        Args:
            prices: List of closing prices
            period: Lookback period
            
        Returns:
            Dictionary with volatility metrics
        """
        if len(prices) < period:
            return {
                "std_dev": 0.0,
                "coefficient_variation": 0.0,
                "volatility_percentile": 50.0
            }
        
        recent_prices = np.array(prices[-period:])
        returns = np.diff(recent_prices) / recent_prices[:-1]
        
        std_dev = np.std(returns) * 100  # As percentage
        mean_return = np.mean(returns)
        cv = std_dev / abs(mean_return) if mean_return != 0 else 0.0
        
        # Calculate volatility percentile (current vs historical)
        all_prices = np.array(prices)
        if len(all_prices) > period * 2:
            historical_vols = []
            for i in range(period, len(all_prices)):
                window = all_prices[i-period:i]
                window_returns = np.diff(window) / window[:-1]
                historical_vols.append(np.std(window_returns))
            
            current_vol = std_dev / 100
            percentile = np.percentile(historical_vols, 50)
            volatility_percentile = sum(1 for v in historical_vols if v < current_vol) / len(historical_vols) * 100
        else:
            volatility_percentile = 50.0
        
        return {
            "std_dev": float(std_dev),
            "coefficient_variation": float(cv),
            "volatility_percentile": float(volatility_percentile)
        }
    
    @staticmethod
    def _calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        
        return ema
    
    @staticmethod
    def analyze_market_structure(
        prices: List[float],
        highs: List[float],
        lows: List[float]
    ) -> Dict[str, Any]:
        """
        Analyze market structure for higher quality setups
        
        Args:
            prices: List of closing prices
            highs: List of high prices
            lows: List of low prices
            
        Returns:
            Dictionary with market structure analysis
        """
        if len(prices) < 20:
            return {
                "structure": "ranging",
                "support": prices[-1] if prices else 0,
                "resistance": prices[-1] if prices else 0,
                "breakout_probability": 0.5
            }
        
        recent_high = max(highs[-20:])
        recent_low = min(lows[-20:])
        current_price = prices[-1]
        
        # Determine if we're near support/resistance
        range_size = recent_high - recent_low
        distance_to_high = (recent_high - current_price) / range_size if range_size > 0 else 0.5
        distance_to_low = (current_price - recent_low) / range_size if range_size > 0 else 0.5
        
        # Detect higher highs / lower lows
        mid_point = len(prices) // 2
        first_half_high = max(highs[:mid_point])
        second_half_high = max(highs[mid_point:])
        first_half_low = min(lows[:mid_point])
        second_half_low = min(lows[mid_point:])
        
        if second_half_high > first_half_high and second_half_low > first_half_low:
            structure = "uptrend"
            breakout_prob = 0.7 if distance_to_high < 0.1 else 0.5
        elif second_half_high < first_half_high and second_half_low < first_half_low:
            structure = "downtrend"
            breakout_prob = 0.7 if distance_to_low < 0.1 else 0.5
        else:
            structure = "ranging"
            breakout_prob = 0.6 if (distance_to_high < 0.1 or distance_to_low < 0.1) else 0.3
        
        return {
            "structure": structure,
            "support": float(recent_low),
            "resistance": float(recent_high),
            "breakout_probability": float(breakout_prob),
            "distance_to_resistance": float(distance_to_high),
            "distance_to_support": float(distance_to_low)
        }


class MarketAnalyzer:
    """
    High-level market analysis combining multiple indicators
    """
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def analyze_full_market(self, candles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis
        
        Args:
            candles: List of candlestick data
            
        Returns:
            Dictionary with complete market analysis
        """
        if not candles or len(candles) < 2:
            return {}
        
        # Extract price data
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        volumes = [c['volume'] for c in candles]
        
        # Calculate all indicators
        rsi = self.indicators.calculate_rsi(closes)
        macd = self.indicators.calculate_macd(closes)
        bb = self.indicators.calculate_bollinger_bands(closes)
        atr = self.indicators.calculate_atr(highs, lows, closes)
        volume_profile = self.indicators.calculate_volume_profile(volumes)
        momentum = self.indicators.calculate_momentum(closes)
        trend = self.indicators.detect_trend(closes)
        volatility = self.indicators.calculate_volatility(closes)
        structure = self.indicators.analyze_market_structure(closes, highs, lows)
        
        # Calculate trade quality score (0-100)
        trade_quality = self._calculate_trade_quality(
            rsi, macd, bb, volume_profile, trend, structure
        )
        
        return {
            "rsi": rsi,
            "macd": macd,
            "bollinger_bands": bb,
            "atr": atr,
            "atr_percent": (atr / closes[-1] * 100) if closes[-1] > 0 else 0,
            "volume_profile": volume_profile,
            "momentum": momentum,
            "trend": trend,
            "volatility": volatility,
            "market_structure": structure,
            "trade_quality_score": trade_quality,
            "current_price": closes[-1]
        }
    
    def _calculate_trade_quality(
        self,
        rsi: float,
        macd: Dict[str, float],
        bb: Dict[str, float],
        volume: Dict[str, float],
        trend: Dict[str, Any],
        structure: Dict[str, Any]
    ) -> float:
        """
        Calculate overall trade quality score (0-100)
        Higher score = better setup
        """
        score = 50.0  # Start neutral
        
        # RSI signals
        if 30 <= rsi <= 40 or 60 <= rsi <= 70:  # Good entry zones
            score += 10
        elif rsi < 20 or rsi > 80:  # Extreme zones (risky)
            score -= 5
        
        # MACD signals
        if abs(macd['histogram']) > abs(macd['macd']) * 0.1:  # Strong momentum
            score += 10
        
        # Bollinger Bands
        if bb['position'] < 0.2 or bb['position'] > 0.8:  # Near bands (reversal setup)
            score += 5
        if bb['width'] > 0.05:  # High volatility (opportunity)
            score += 5
        
        # Volume
        if volume['volume_ratio'] > 1.5:  # High volume
            score += 10
        
        # Trend
        if trend['strength'] > 0.02:  # Strong trend
            score += 15
        
        # Structure
        if structure['breakout_probability'] > 0.6:
            score += 10
        
        return max(0, min(100, score))


