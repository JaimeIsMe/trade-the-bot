"""
Performance metrics calculation
"""
from typing import List, Dict, Any
from datetime import datetime
import numpy as np


class PerformanceMetrics:
    """Calculate trading performance metrics"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: List of returns
            risk_free_rate: Risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0
        
        excess_returns = np.array(returns) - risk_free_rate
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0.0
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Maximum drawdown as decimal
        """
        if len(equity_curve) < 2:
            return 0.0
        
        equity = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max
        return abs(np.min(drawdown))
    
    @staticmethod
    def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate win rate
        
        Args:
            trades: List of trade records
            
        Returns:
            Win rate as decimal
        """
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
        return winning_trades / len(trades)
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate profit factor (gross profit / gross loss)
        
        Args:
            trades: List of trade records
            
        Returns:
            Profit factor
        """
        if not trades:
            return 0.0
        
        gross_profit = sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0)
        gross_loss = abs(sum(t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    @staticmethod
    def calculate_average_trade(trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average trade metrics
        
        Args:
            trades: List of trade records
            
        Returns:
            Dictionary with average metrics
        """
        if not trades:
            return {"avg_win": 0.0, "avg_loss": 0.0, "avg_trade": 0.0}
        
        winning_trades = [t.get("pnl", 0) for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t.get("pnl", 0) for t in trades if t.get("pnl", 0) < 0]
        
        return {
            "avg_win": np.mean(winning_trades) if winning_trades else 0.0,
            "avg_loss": np.mean(losing_trades) if losing_trades else 0.0,
            "avg_trade": np.mean([t.get("pnl", 0) for t in trades])
        }
    
    @staticmethod
    def calculate_expectancy(trades: List[Dict[str, Any]]) -> float:
        """
        Calculate expectancy (average $ per trade)
        
        Args:
            trades: List of trade records
            
        Returns:
            Expectancy value
        """
        if not trades:
            return 0.0
        
        win_rate = PerformanceMetrics.calculate_win_rate(trades)
        avg_metrics = PerformanceMetrics.calculate_average_trade(trades)
        
        expectancy = (win_rate * avg_metrics["avg_win"]) + ((1 - win_rate) * avg_metrics["avg_loss"])
        return expectancy
    
    @staticmethod
    def generate_report(trades: List[Dict[str, Any]], equity_curve: List[float]) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        
        Args:
            trades: List of trade records
            equity_curve: List of equity values
            
        Returns:
            Performance report dictionary
        """
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "expectancy": 0.0,
                "avg_metrics": {}
            }
        
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        
        return {
            "total_trades": len(trades),
            "win_rate": PerformanceMetrics.calculate_win_rate(trades),
            "profit_factor": PerformanceMetrics.calculate_profit_factor(trades),
            "max_drawdown": PerformanceMetrics.calculate_max_drawdown(equity_curve),
            "sharpe_ratio": PerformanceMetrics.calculate_sharpe_ratio(returns),
            "expectancy": PerformanceMetrics.calculate_expectancy(trades),
            "avg_metrics": PerformanceMetrics.calculate_average_trade(trades),
            "total_pnl": sum(t.get("pnl", 0) for t in trades),
            "largest_win": max((t.get("pnl", 0) for t in trades), default=0),
            "largest_loss": min((t.get("pnl", 0) for t in trades), default=0)
        }

