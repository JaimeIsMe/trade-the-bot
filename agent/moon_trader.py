"""
Moon Phase Trader - Because crypto traders believe in the moon! 🌕
"Buy when moon wanes, sell when moon waxes" 
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger
import json
import math
import winsound
import re

from config.config import config
from agent.llm_client import LLMClient
from utils.logger import setup_logger
from utils.decision_store import DecisionStore


def strip_emojis(text: str) -> str:
    """Remove emojis from text to avoid Windows encoding errors"""
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()


class MoonPhaseTrader:
    """
    Trading bot that follows the moon phases
    Moon wanes -> BTC waxes (LONG)
    Moon waxes -> BTC wanes (SHORT)
    """
    
    def __init__(self, aster_client, symbol: str = "BTCUSDT", llm_client: Optional[LLMClient] = None):
        """
        Initialize the Moon Phase Trader
        
        Args:
            aster_client: Aster API client instance
            symbol: Trading symbol (default BTCUSDT)
            llm_client: LLM client (not used - moon bot is rule-based)
        """
        self.aster = aster_client
        self.symbol = symbol
        # No LLM needed - moon phases are deterministic!
        self.running = False
        self.positions = {}
        
        # Persistent decision storage
        self.decision_store = DecisionStore(filepath=f"logs/moon_decisions_{symbol}.json")
        
        self.trade_history = []
        self.decision_log = []
        
        setup_logger()
        logger.info(f"MOON Moon Phase Trader initialized for {symbol} (RULE-BASED - No OpenAI cost)")
    
    def get_moon_phase(self) -> Dict[str, Any]:
        """
        Calculate current moon phase
        Returns phase percentage (0 = new moon, 50 = full moon, 100 = new moon)
        """
        # Known new moon date
        known_new_moon = datetime(2000, 1, 6, 18, 14)
        
        # Moon cycle is approximately 29.53 days
        lunar_cycle = 29.530588853
        
        # Calculate days since known new moon
        now = datetime.now()
        days_since_new_moon = (now - known_new_moon).total_seconds() / (24 * 3600)
        
        # Calculate current phase in cycle
        phase_in_cycle = (days_since_new_moon % lunar_cycle) / lunar_cycle
        
        # Determine phase name and trend
        if phase_in_cycle < 0.03:
            phase_name = "New Moon 🌑"
            trend = "waxing_start"
        elif phase_in_cycle < 0.22:
            phase_name = "Waxing Crescent 🌒"
            trend = "waxing"
        elif phase_in_cycle < 0.28:
            phase_name = "First Quarter 🌓"
            trend = "waxing"
        elif phase_in_cycle < 0.47:
            phase_name = "Waxing Gibbous 🌔"
            trend = "waxing"
        elif phase_in_cycle < 0.53:
            phase_name = "Full Moon 🌕"
            trend = "waning_start"
        elif phase_in_cycle < 0.72:
            phase_name = "Waning Gibbous 🌖"
            trend = "waning"
        elif phase_in_cycle < 0.78:
            phase_name = "Last Quarter 🌗"
            trend = "waning"
        elif phase_in_cycle < 0.97:
            phase_name = "Waning Crescent 🌘"
            trend = "waning"
        else:
            phase_name = "New Moon 🌑"
            trend = "waxing_start"
        
        # Determine trading action based on moon phase
        # Moon wanes -> BTC waxes (bullish) -> LONG
        # Moon waxes -> BTC wanes (bearish) -> SHORT
        if trend == "waning":
            bias = "LONG"
            reasoning = "Moon is waning, BTC should wax (bullish)"
        elif trend == "waxing":
            bias = "SHORT"
            reasoning = "Moon is waxing, BTC should wane (bearish)"
        else:
            bias = "HOLD"
            reasoning = "Moon phase transition, wait for clear trend"
        
        return {
            "phase_name": phase_name,
            "phase_percentage": phase_in_cycle * 100,
            "trend": trend,
            "bias": bias,
            "reasoning": reasoning,
            "illumination": abs(math.sin(phase_in_cycle * math.pi)) * 100
        }
    
    async def start(self):
        """Start the moon phase trading agent"""
        self.running = True
        logger.info(f"MOON Starting Moon Phase Trader for {self.symbol}...")
        
        # Set leverage
        try:
            await self.aster.set_leverage(self.symbol, config.trading.leverage)
            logger.success(f"✅ Set leverage to {config.trading.leverage}x for {self.symbol}")
        except Exception as e:
            logger.warning(f"Could not set leverage: {e}. Using account default.")
        
        try:
            while self.running:
                # Get moon phase
                moon = self.get_moon_phase()
                logger.info(f"MOON Current Moon: {moon['phase_percentage']:.1f}% - Bias: {moon['bias']}")
                
                # Get market data
                market_data = await self._gather_market_data()
                
                # Get portfolio state
                portfolio_state = await self._analyze_portfolio()
                
                # Make trading decision with moon phase influence
                decision = await self._make_moon_decision(moon, market_data, portfolio_state)
                
                # Log decision
                self._log_decision(decision, market_data, portfolio_state, moon)
                
                # Execute decision
                await self._execute_decision(decision)
                
                # Wait before next cycle (5 minutes)
                await asyncio.sleep(config.trading.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Moon Phase Trader stopped by user")
        except Exception as e:
            logger.error(f"Error in moon phase trader: {e}")
            raise
        finally:
            self.running = False
    
    async def _gather_market_data(self) -> Dict[str, Any]:
        """Gather current market data"""
        try:
            ticker = await self.aster.get_ticker(self.symbol)
            klines = await self.aster.get_klines(self.symbol, interval="15m", limit=48)
            
            candles = []
            for k in klines:
                candles.append({
                    "time": datetime.fromtimestamp(int(k[0])/1000).strftime('%Y-%m-%d %H:%M'),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5])
                })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "ticker": ticker,
                "candles": candles
            }
        except Exception as e:
            logger.error(f"Error gathering market data: {e}")
            return {}
    
    async def _analyze_portfolio(self) -> Dict[str, Any]:
        """Analyze current portfolio state"""
        try:
            account = await self.aster.get_account()
            positions = account.get('positions', [])
            
            # Filter for our symbol
            symbol_positions = [p for p in positions if p.get('symbol') == self.symbol and float(p.get('positionAmt', 0)) != 0]
            
            return {
                "positions": symbol_positions,
                "has_position": len(symbol_positions) > 0
            }
        except Exception as e:
            logger.warning(f"Could not fetch positions: {e}")
            return {"positions": [], "has_position": False}
    
    async def _make_moon_decision(
        self,
        moon: Dict[str, Any],
        market_data: Dict[str, Any],
        portfolio_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make trading decision based on moon phase (RULE-BASED - NO AI COST)"""
        
        ticker = market_data.get('ticker', {})
        current_price = float(ticker.get('lastPrice', 0))
        change_24h = float(ticker.get('priceChangePercent', 0))
        
        has_position = portfolio_state.get('has_position', False)
        positions = portfolio_state.get('positions', [])
        
        # DETERMINISTIC RULES - No OpenAI needed!
        moon_bias = moon['bias']
        moon_trend = moon['trend']
        
        # Calculate stop loss and take profit based on current price
        stop_loss = round(current_price * 0.98, 1)  # 2% stop loss
        take_profit = round(current_price * 1.04, 1)  # 4% take profit
        
        # Rule 1: During transition periods (new/full moon), HOLD
        if moon_bias == "HOLD":
            return {
                "action": "hold",
                "symbol": self.symbol,
                "size_usd": 20,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reasoning": f"Moon phase transition ({strip_emojis(moon['phase_name'])}), waiting for clear signal",
                "confidence": 50,
                "moon_phase": moon['phase_name'],
                "moon_bias": moon_bias
            }
        
        # Rule 2: If we have a position, manage it
        if has_position:
            current_side = positions[0].get('side', 'long') if positions else 'long'
            
            # Check if moon bias aligns with current position
            if (moon_bias == "LONG" and current_side == "long") or \
               (moon_bias == "SHORT" and current_side == "short"):
                # Hold the position - moon still supports it
                return {
                    "action": "hold",
                    "symbol": self.symbol,
                    "size_usd": 20,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reasoning": f"Moon phase supports current position ({strip_emojis(moon['phase_name'])})",
                    "confidence": 75,
                    "moon_phase": moon['phase_name'],
                    "moon_bias": moon_bias
                }
            else:
                # Close position - moon has shifted
                return {
                    "action": "close",
                    "symbol": self.symbol,
                    "size_usd": 20,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reasoning": f"Moon phase shifted from {current_side}, closing position",
                    "confidence": 85,
                    "moon_phase": moon['phase_name'],
                    "moon_bias": moon_bias
                }
        
        # Rule 3: Open new position based on moon bias
        # Confirm with price action for higher confidence
        price_confirms = (moon_bias == "LONG" and change_24h > 0) or \
                        (moon_bias == "SHORT" and change_24h < 0)
        
        confidence = 80 if price_confirms else 65
        
        action = "long" if moon_bias == "LONG" else "short"
        
        return {
            "action": action,
            "symbol": self.symbol,
            "size_usd": 20,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "reasoning": f"Moon {moon_trend} = BTC {'bullish' if moon_bias == 'LONG' else 'bearish'} ({strip_emojis(moon['phase_name'])})" + 
                        (f", price confirms (+{change_24h:.1f}%)" if price_confirms else ""),
            "confidence": confidence,
            "moon_phase": moon['phase_name'],
            "moon_bias": moon_bias,
            "moon_aligned": price_confirms
        }
    
    async def _execute_decision(self, decision: Dict[str, Any]):
        """Execute trading decision"""
        action = decision.get('action', 'hold').lower()
        confidence = decision.get('confidence', 0)
        
        if confidence < 60:
            logger.info(f"MOON says {action} but confidence too low ({confidence}%), skipping")
            return
        
        try:
            if action == "long" or action == "short":
                logger.info(f"MOON Phase Signal: {action.upper()} {self.symbol}")
                
                # Get current price for calculations
                ticker = await self.aster.get_ticker(self.symbol)
                current_price = float(ticker.get('lastPrice', 0))
                
                # Calculate position size
                size_usd = decision.get('size_usd', 20)
                quantity = size_usd / current_price
                
                # Ensure minimum quantity (0.001 for BTC)
                if quantity < 0.001:
                    quantity = 0.001
                
                # Place order
                side = "BUY" if action == "long" else "SELL"
                order = await self.aster.place_order(
                    symbol=self.symbol,
                    side=side,
                    size=quantity,
                    order_type="MARKET"
                )
                
                logger.success(f"MOON trade executed: {side} {quantity:.3f} {self.symbol}")
                
                # Play sound notification
                try:
                    logger.info(f"MOON Playing {action.upper()} sound alert...")
                    if action == "long":
                        # Higher pitch for BUY/LONG
                        winsound.Beep(1000, 500)
                    else:
                        # Lower pitch for SELL/SHORT
                        winsound.Beep(500, 500)
                    logger.info(f"MOON Sound alert played successfully")
                except Exception as e:
                    logger.warning(f"MOON Could not play sound: {e}")
                
                # Set stop loss and take profit if provided
                stop_loss = decision.get('stop_loss')
                take_profit = decision.get('take_profit')
                
                if stop_loss:
                    sl_side = "SELL" if action == "long" else "BUY"
                    await self.aster.set_stop_loss(self.symbol, stop_loss, quantity, sl_side)
                    logger.info(f"MOON Stop Loss set at {stop_loss}")
                
                if take_profit:
                    tp_side = "SELL" if action == "long" else "BUY"
                    await self.aster.set_take_profit(self.symbol, take_profit, quantity, tp_side)
                    logger.info(f"MOON Take Profit set at {take_profit}")
                
            elif action == "close":
                logger.info(f"MOON Phase Signal: CLOSE {self.symbol}")
                await self.aster.close_position(self.symbol)
                logger.success(f"MOON Position closed on {self.symbol}")
                
                # Cancel all open orders (TP/SL) for this symbol
                try:
                    await self.aster.cancel_all_orders(self.symbol)
                    logger.success(f"MOON Canceled all open orders for {self.symbol}")
                except Exception as e:
                    logger.warning(f"MOON Could not cancel orders: {e}")
                
        except Exception as e:
            logger.error(f"Error executing moon decision: {e}")
    
    def _log_decision(
        self,
        decision: Dict[str, Any],
        market_data: Dict[str, Any],
        portfolio_state: Dict[str, Any],
        moon: Dict[str, Any]
    ):
        """Log trading decision with moon phase data"""
        self.decision_store.add_decision(decision, market_data, portfolio_state)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "moon_phase": moon,
            "market_snapshot": market_data,
            "portfolio_snapshot": portfolio_state
        }
        
        self.decision_log.append(log_entry)
        
        if len(self.decision_log) > 1000:
            self.decision_log = self.decision_log[-1000:]
        
        logger.info(f"MOON Decision: {decision['action']} - {decision.get('reasoning', 'N/A')}")
    
    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Get decision log for dashboard"""
        return self.decision_store.get_all_decisions()
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history for dashboard"""
        return self.trade_history

