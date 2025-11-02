"""
Risk Management Module - AGGRESSIVE EDITION
Advanced risk controls with portfolio heat monitoring and adaptive sizing
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from config.config import config
from datetime import datetime, timedelta


class RiskManager:
    """
    Advanced risk management for aggressive trading
    - Portfolio heat monitoring (total risk exposure)
    - Adaptive position sizing based on performance
    - ATR-based dynamic stops
    - Correlation-aware position limits
    """
    
    def __init__(self):
        self.max_position_size = config.trading.max_position_size
        self.risk_per_trade = config.trading.risk_per_trade
        self.max_open_positions = config.trading.max_open_positions
        self.max_portfolio_heat = config.trading.max_portfolio_heat
        
        # Track recent performance for adaptive risk
        self.recent_trades = []
        self.current_drawdown = 0.0
        self.peak_balance = 0.0
    
    def validate_trade(
        self,
        decision: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if a trade meets risk requirements
        
        Args:
            decision: Trading decision from AI
            portfolio: Current portfolio state
            
        Returns:
            (is_valid, reason)
        """
        action = decision.get("action")
        
        if action == "hold" or action == "close":
            return True, None
        
        # Check position count limit
        current_positions = len(portfolio.get("positions", {}))
        if current_positions >= self.max_open_positions:
            return False, f"Maximum open positions ({self.max_open_positions}) reached"
        
        # Check position size
        size = decision.get("size", 0)
        if size > self.max_position_size:
            return False, f"Position size ${size} exceeds maximum ${self.max_position_size}"
        
        # Check available margin
        available_margin = portfolio.get("available_margin", 0)
        required_margin = self._calculate_required_margin(decision)
        
        if required_margin > available_margin:
            return False, f"Insufficient margin: need ${required_margin}, have ${available_margin}"
        
        # Check stop loss is set
        if not decision.get("stop_loss"):
            return False, "Stop loss is required for all positions"
        
        # Validate stop loss distance
        if not self._validate_stop_loss(decision):
            return False, "Stop loss too far from entry (exceeds risk per trade)"
        
        return True, None
    
    def _calculate_required_margin(self, decision: Dict[str, Any]) -> float:
        """Calculate required margin for a trade"""
        size = decision.get("size", 0)
        # Assuming 10x leverage by default
        # Adjust based on actual Aster leverage settings
        leverage = decision.get("leverage", 10)
        return size / leverage
    
    def _validate_stop_loss(self, decision: Dict[str, Any]) -> bool:
        """Validate stop loss is within risk parameters"""
        size = decision.get("size", 0)
        stop_loss = decision.get("stop_loss")
        
        if not stop_loss:
            return False
        
        # For limit orders, use the price; for market orders, estimate current price
        entry_price = decision.get("price") or decision.get("estimated_price", 0)
        
        if entry_price == 0:
            return True  # Can't validate without price, allow it
        
        action = decision.get("action")
        if action == "long":
            stop_distance = entry_price - stop_loss
            risk_amount = (stop_distance / entry_price) * size
        else:  # short
            stop_distance = stop_loss - entry_price
            risk_amount = (stop_distance / entry_price) * size
        
        # Risk should not exceed risk_per_trade percentage of size
        max_risk = size * self.risk_per_trade
        
        return risk_amount <= max_risk
    
    def adjust_position_size(
        self,
        decision: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> float:
        """
        Adjust position size to fit risk parameters
        
        Args:
            decision: Trading decision
            portfolio: Current portfolio state
            
        Returns:
            Adjusted position size
        """
        requested_size = decision.get("size", 0)
        available_margin = portfolio.get("available_margin", 0)
        
        # Limit to max position size
        size = min(requested_size, self.max_position_size)
        
        # Limit to available margin (with leverage)
        leverage = decision.get("leverage", 10)
        max_size_by_margin = available_margin * leverage
        size = min(size, max_size_by_margin)
        
        # Apply risk per trade limit
        total_balance = portfolio.get("balance", {}).get("total", 0)
        max_size_by_risk = total_balance * self.risk_per_trade * leverage
        size = min(size, max_size_by_risk)
        
        logger.info(f"Adjusted position size from ${requested_size} to ${size}")
        
        return size
    
    def calculate_position_size_by_stop(
        self,
        balance: float,
        entry_price: float,
        stop_price: float,
        leverage: float = 10
    ) -> float:
        """
        Calculate position size based on stop loss and risk per trade
        
        Args:
            balance: Account balance
            entry_price: Entry price
            stop_price: Stop loss price
            leverage: Trading leverage
            
        Returns:
            Position size in USD
        """
        risk_amount = balance * self.risk_per_trade
        price_distance = abs(entry_price - stop_price)
        price_distance_pct = price_distance / entry_price
        
        # Position size that would lose risk_amount if stop is hit
        position_size = risk_amount / price_distance_pct
        
        # Apply leverage
        position_size = position_size * leverage
        
        # Cap at max position size
        position_size = min(position_size, self.max_position_size)
        
        return position_size
    
    def calculate_portfolio_heat(self, positions: List[Dict[str, Any]], balance: float) -> float:
        """
        Calculate total portfolio heat (percentage of capital at risk)
        
        Args:
            positions: List of open positions with stop losses
            balance: Account balance
            
        Returns:
            Portfolio heat as percentage (0.0 to 1.0)
        """
        if balance <= 0:
            return 0.0
        
        total_risk = 0.0
        
        for pos in positions:
            try:
                entry_price = float(pos.get('entryPrice', 0))
                position_amt = float(pos.get('positionAmt', 0))
                notional = abs(float(pos.get('notional', 0)))
                
                # Estimate risk as position size * expected stop distance
                # Assuming 2% stop distance on average (will be more accurate with actual stops)
                estimated_risk = notional * 0.02
                total_risk += estimated_risk
                
            except Exception as e:
                logger.warning(f"Could not calculate risk for position: {e}")
        
        portfolio_heat = total_risk / balance if balance > 0 else 0.0
        return portfolio_heat
    
    def check_portfolio_heat(
        self, 
        positions: List[Dict[str, Any]], 
        new_position_size: float,
        balance: float
    ) -> tuple[bool, str]:
        """
        Check if adding a new position would exceed portfolio heat limit
        
        Args:
            positions: Current open positions
            new_position_size: Size of proposed new position
            balance: Account balance
            
        Returns:
            (is_allowed, reason)
        """
        current_heat = self.calculate_portfolio_heat(positions, balance)
        
        # Estimate additional risk from new position (assuming 2% stop)
        additional_risk = new_position_size * 0.02
        projected_heat = (current_heat * balance + additional_risk) / balance if balance > 0 else 0
        
        if projected_heat > self.max_portfolio_heat:
            return False, f"Portfolio heat too high: {projected_heat*100:.1f}% > {self.max_portfolio_heat*100:.1f}%"
        
        logger.info(f"📊 Portfolio Heat: Current={current_heat*100:.1f}%, Projected={projected_heat*100:.1f}%, Max={self.max_portfolio_heat*100:.1f}%")
        return True, "Portfolio heat acceptable"
    
    def get_adaptive_risk_multiplier(self, win_rate: float, recent_pnl: float) -> float:
        """
        Calculate adaptive risk multiplier based on recent performance
        
        Args:
            win_rate: Recent win rate (0.0 to 1.0)
            recent_pnl: Recent P&L in USD
            
        Returns:
            Risk multiplier (0.5 to 1.5)
        """
        # Start at 1.0 (no adjustment)
        multiplier = 1.0
        
        # Winning streak: increase risk
        if win_rate > 0.60 and recent_pnl > 50:
            multiplier = 1.3  # 30% larger positions
        elif win_rate > 0.55 and recent_pnl > 0:
            multiplier = 1.15  # 15% larger positions
        
        # Losing streak: decrease risk
        elif win_rate < 0.40 or recent_pnl < -100:
            multiplier = 0.5  # 50% smaller positions
        elif win_rate < 0.45 or recent_pnl < -50:
            multiplier = 0.7  # 30% smaller positions
        
        logger.info(f"🎲 Adaptive Risk: WR={win_rate*100:.1f}%, P&L=${recent_pnl:+.2f} -> {multiplier:.2f}x")
        return multiplier
    
    def validate_trade_quality(
        self,
        decision: Dict[str, Any],
        market_analysis: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Validate trade quality before execution
        
        Args:
            decision: Trading decision
            market_analysis: Technical analysis data
            
        Returns:
            (is_valid, reason)
        """
        confidence = decision.get('confidence', 0)
        trade_quality = market_analysis.get('trade_quality_score', 0)
        
        # Confidence check
        if confidence < config.trading.confidence_threshold:
            return False, f"Confidence too low: {confidence}% < {config.trading.confidence_threshold}%"
        
        # Trade quality check
        if trade_quality < 40:
            return False, f"Trade quality too low: {trade_quality}/100"
        
        # Risk/Reward check
        expected_rr = decision.get('expected_rr', 0)
        if expected_rr > 0 and expected_rr < 1.5:
            return False, f"Risk/Reward too low: {expected_rr:.2f}:1 (need ≥1.5:1)"
        
        return True, "Trade quality acceptable"
    
    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        position_type: str,
        atr: float
    ) -> Optional[float]:
        """
        Calculate trailing stop price based on ATR
        
        Args:
            entry_price: Position entry price
            current_price: Current market price
            position_type: "long" or "short"
            atr: Average True Range
            
        Returns:
            Trailing stop price or None if not activated
        """
        # Check if position is in profit enough to activate trailing stop
        if position_type == "long":
            profit_pct = (current_price - entry_price) / entry_price
            if profit_pct > config.trading.trailing_stop_activation:
                # Trail below current price by ATR distance
                trailing_stop = current_price - (atr * 1.5)
                return trailing_stop
        else:  # short
            profit_pct = (entry_price - current_price) / entry_price
            if profit_pct > config.trading.trailing_stop_activation:
                # Trail above current price by ATR distance
                trailing_stop = current_price + (atr * 1.5)
                return trailing_stop
        
        return None
    
    def should_reduce_exposure(
        self,
        portfolio_state: Dict[str, Any],
        market_volatility: float
    ) -> tuple[bool, str]:
        """
        Determine if exposure should be reduced due to adverse conditions
        
        Args:
            portfolio_state: Current portfolio state
            market_volatility: Current market volatility percentile
            
        Returns:
            (should_reduce, reason)
        """
        # Check if in drawdown
        performance = portfolio_state.get('performance', {})
        recent_pnl = performance.get('recent_pnl', 0)
        win_rate = performance.get('win_rate', 0.5)
        
        # Significant drawdown
        if recent_pnl < -200:
            return True, f"Significant drawdown: ${recent_pnl:.2f}"
        
        # Low win rate
        if win_rate < 0.35 and performance.get('total_trades', 0) > 10:
            return True, f"Low win rate: {win_rate*100:.1f}%"
        
        # Extreme volatility
        if market_volatility > 90:
            return True, f"Extreme volatility: {market_volatility:.0f}th percentile"
        
        return False, "Exposure levels acceptable"

