"""
Trade Outcome Tracker - Label AI decisions with actual results
This builds a dataset for future model improvements
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger


class TradeTracker:
    """
    Tracks trades from decision → execution → outcome
    Labels each AI decision with actual P&L and correctness
    """
    
    def __init__(self, filepath: str = "logs/trade_outcomes.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.trades = self._load()
        
    def _load(self) -> Dict[str, Any]:
        """Load existing trade outcomes"""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data.get('trades', []))} tracked trades from {self.filepath}")
                    return data
            except Exception as e:
                logger.error(f"Error loading trade tracker: {e}")
                return {"trades": [], "stats": {}}
        return {"trades": [], "stats": {}}
    
    def _save(self):
        """Save trade outcomes to disk"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.trades, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving trade tracker: {e}")
    
    def start_trade(
        self,
        symbol: str,
        decision: Dict[str, Any],
        market_data: Dict[str, Any],
        entry_price: float,
        position_size: float
    ) -> str:
        """
        Record when a trade is opened
        Returns trade_id for later reference
        """
        trade_id = f"{symbol}_{datetime.now().timestamp()}"
        
        trade = {
            "trade_id": trade_id,
            "symbol": symbol,
            "timestamp_open": datetime.now().isoformat(),
            "timestamp_close": None,
            
            # AI Decision
            "decision": {
                "action": decision.get("action"),
                "reasoning": decision.get("reasoning"),
                "confidence": decision.get("confidence", 0),
                "predicted_direction": "up" if decision.get("action") == "long" else "down",
                "stop_loss": decision.get("stop_loss"),
                "take_profit": decision.get("take_profit")
            },
            
            # Market Context
            "market_snapshot": {
                "entry_price": entry_price,
                "price_24h_change": market_data.get("ticker", {}).get("priceChangePercent"),
                "last_candle": market_data.get("candles", [])[-1] if market_data.get("candles") else None
            },
            
            # Position Info
            "position": {
                "size": position_size,
                "leverage": 4,  # From config
                "entry_price": entry_price
            },
            
            # Outcome (filled later)
            "outcome": {
                "exit_price": None,
                "pnl_usd": None,
                "pnl_percent": None,
                "actual_direction": None,
                "was_correct": None,
                "exit_reason": None,  # "tp_hit", "sl_hit", "ai_close", "manual"
                "duration_minutes": None
            },
            
            # Performance Label (for ML)
            "label": {
                "quality": None,  # "excellent", "good", "neutral", "bad", "terrible"
                "should_repeat": None,  # True/False
                "lessons": []
            }
        }
        
        self.trades["trades"].append(trade)
        self._save()
        
        logger.info(f"Started tracking trade {trade_id}: {decision.get('action')} @ ${entry_price}")
        return trade_id
    
    def close_trade(
        self,
        symbol: str,
        exit_price: float,
        exit_reason: str = "ai_close"
    ):
        """
        Record when a trade is closed
        Calculate outcome and label quality
        """
        # Find most recent open trade for this symbol
        open_trades = [t for t in self.trades["trades"] 
                      if t["symbol"] == symbol and t["outcome"]["exit_price"] is None]
        
        if not open_trades:
            logger.warning(f"No open trade found for {symbol} to close")
            return
        
        trade = open_trades[-1]  # Most recent
        
        # Calculate outcome
        entry_price = trade["position"]["entry_price"]
        position_size = trade["position"]["size"]
        predicted_direction = trade["decision"]["predicted_direction"]
        
        # P&L calculation
        if predicted_direction == "up":  # LONG
            pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        else:  # SHORT
            pnl_percent = ((entry_price - exit_price) / entry_price) * 100
        
        pnl_usd = (pnl_percent / 100) * position_size * trade["position"]["leverage"]
        
        # Actual price direction
        actual_direction = "up" if exit_price > entry_price else "down"
        was_correct = (predicted_direction == actual_direction)
        
        # Duration
        time_open = datetime.fromisoformat(trade["timestamp_open"])
        time_close = datetime.now()
        duration_minutes = (time_close - time_open).total_seconds() / 60
        
        # Update outcome
        trade["timestamp_close"] = time_close.isoformat()
        trade["outcome"] = {
            "exit_price": exit_price,
            "pnl_usd": round(pnl_usd, 2),
            "pnl_percent": round(pnl_percent, 2),
            "actual_direction": actual_direction,
            "was_correct": was_correct,
            "exit_reason": exit_reason,
            "duration_minutes": round(duration_minutes, 1)
        }
        
        # Label quality for ML
        trade["label"] = self._label_quality(trade)
        
        self._save()
        self._update_stats()
        
        logger.info(f"Closed trade {trade['trade_id']}: "
                   f"{'✓' if was_correct else '✗'} "
                   f"P&L: ${pnl_usd:.2f} ({pnl_percent:+.2f}%) "
                   f"Quality: {trade['label']['quality']}")
    
    def _label_quality(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Label trade quality for machine learning
        This is what we'll use to train future models
        """
        pnl = trade["outcome"]["pnl_percent"]
        was_correct = trade["outcome"]["was_correct"]
        confidence = trade["decision"]["confidence"]
        
        lessons = []
        
        # Determine quality label
        if pnl > 2:
            quality = "excellent"
            should_repeat = True
            lessons.append("Strong profitable trade")
        elif pnl > 0.5:
            quality = "good"
            should_repeat = True
            lessons.append("Profitable trade")
        elif pnl > -0.5:
            quality = "neutral"
            should_repeat = False
            lessons.append("Small loss/break-even")
        elif pnl > -2:
            quality = "bad"
            should_repeat = False
            lessons.append("Significant loss")
        else:
            quality = "terrible"
            should_repeat = False
            lessons.append("Major loss - avoid this pattern")
        
        # Add context-specific lessons
        if was_correct and pnl < 0:
            lessons.append("Right direction but exit too early")
        elif not was_correct and confidence > 80:
            lessons.append("Overconfident wrong prediction")
        elif was_correct and confidence < 60:
            lessons.append("Underconfident correct prediction")
        
        return {
            "quality": quality,
            "should_repeat": should_repeat,
            "lessons": lessons
        }
    
    def _update_stats(self):
        """Calculate overall performance statistics"""
        closed_trades = [t for t in self.trades["trades"] 
                        if t["outcome"]["exit_price"] is not None]
        
        if not closed_trades:
            return
        
        total_trades = len(closed_trades)
        correct_trades = sum(1 for t in closed_trades if t["outcome"]["was_correct"])
        total_pnl = sum(t["outcome"]["pnl_usd"] for t in closed_trades)
        
        # Win rate
        win_rate = (correct_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Quality distribution
        quality_counts = {}
        for t in closed_trades:
            q = t["label"]["quality"]
            quality_counts[q] = quality_counts.get(q, 0) + 1
        
        self.trades["stats"] = {
            "total_trades": total_trades,
            "correct_predictions": correct_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl_usd": round(total_pnl, 2),
            "avg_pnl_per_trade": round(total_pnl / total_trades, 2) if total_trades > 0 else 0,
            "quality_distribution": quality_counts,
            "last_updated": datetime.now().isoformat()
        }
        
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.trades.get("stats", {})
    
    def get_training_data(self, quality_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get labeled trades for ML training
        
        Args:
            quality_filter: Only return trades with these quality labels
                           e.g., ["excellent", "good"] for positive examples
        """
        closed_trades = [t for t in self.trades["trades"] 
                        if t["outcome"]["exit_price"] is not None]
        
        if quality_filter:
            closed_trades = [t for t in closed_trades 
                           if t["label"]["quality"] in quality_filter]
        
        return closed_trades



