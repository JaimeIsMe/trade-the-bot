"""
AI Vibe Trader - Main trading agent with LLM integration
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger
import json
import winsound

from config.config import config
from agent.llm_client import LLMClient
from utils.logger import setup_logger
from utils.decision_store import DecisionStore
from utils.trade_tracker import TradeTracker
from strategies.indicators import MarketAnalyzer
from utils.shared_account_cache import SharedAccountCache


class VibeTrader:
    """
    Autonomous AI trading agent that uses LLM for decision making
    """
    
    def __init__(
        self, 
        aster_client, 
        llm_client: Optional[LLMClient] = None,
        bot_name: str = "VIBE",
        symbol: str = None,
        decision_log_path: str = None
    ):
        """
        Initialize the Vibe Trader
        
        Args:
            aster_client: Aster API client instance
            llm_client: LLM client for AI decision making (if None, creates default)
            bot_name: Name for this bot instance (for logging)
            symbol: Trading symbol (if None, uses config default)
            decision_log_path: Custom path for decision log (if None, uses default)
        """
        self.aster = aster_client
        self.llm = llm_client or LLMClient()
        self.running = False
        self.positions = {}
        self.bot_name = bot_name
        self.symbol = symbol or config.trading.symbol
        
        # Track when we last opened a position (prevent overtrading)
        self.last_trade_time = None
        self.min_hold_time = getattr(config.trading, "min_hold_time_seconds", 300)
        self.close_confidence_threshold = getattr(config.trading, "close_confidence_threshold", 75)
        self.close_confidence_min = getattr(config.trading, "close_confidence_min_threshold", 60)
        self.close_confidence_decay_minutes = getattr(config.trading, "close_confidence_decay_minutes", 30)
        self.pnl_lock_percent = getattr(config.trading, "pnl_lock_percent", 0.01)
        
        # Persistent decision storage (separate file per bot)
        log_path = decision_log_path or f"logs/decisions_{bot_name}.json"
        self.decision_store = DecisionStore(filepath=log_path)
        
        # Trade outcome tracking for ML (separate file per bot)
        self.trade_tracker = TradeTracker(filepath=f"logs/trade_outcomes_{bot_name}.json")
        
        # Market analysis engine
        self.market_analyzer = MarketAnalyzer()
        
        # Shared account cache (singleton across all bots)
        self.account_cache = SharedAccountCache()
        
        # Trade history is fetched from Aster now, but keep in-memory for compatibility
        self.trade_history = []
        self.decision_log = []
        
        setup_logger()
        logger.info(f"🚀 [{bot_name}] Aggressive Vibe Trader initialized with advanced indicators")
    
    def _calculate_dynamic_position_size(
        self,
        confidence: float,
        volatility: float,
        trade_quality: float,
        portfolio_state: Dict[str, Any]
    ) -> float:
        """
        Calculate dynamic position size based on multiple factors
        
        Args:
            confidence: AI confidence (0-100)
            volatility: Market volatility (ATR %)
            trade_quality: Trade setup quality score (0-100)
            portfolio_state: Current portfolio state
            
        Returns:
            Position size in USD
        """
        # Base size from config (AGGRESSIVE for selective trading)
        account_balance = portfolio_state.get("balance", {}).get("total", 100)
        # If AI is selective, use MORE capital when it DOES trade
        # Increased to 1.0/0.6 for better capital utilization with $2k account
        base_size = min(config.trading.max_position_size * 1.0, account_balance * 0.6)  # 100% of max OR 60% of balance
        
        # Confidence multiplier (60-100% confidence -> 0.7x to 2.5x)
        # Higher confidence = larger position
        # Since we're selective, even marginal setups get decent size
        conf_multiplier = max(0.7, (confidence - 60) / 40 * 1.8 + 0.7)
        
        # Volatility adjustment (higher vol = smaller size for risk control)
        # ATR% typically 1-5% for crypto
        vol_multiplier = 1.0 / (1.0 + volatility / 2.0)
        
        # Trade quality multiplier (0-100 score -> 0.5x to 1.5x)
        quality_multiplier = 0.5 + (trade_quality / 100)
        
        # Performance-based adjustment (adaptive sizing)
        performance = portfolio_state.get("performance", {})
        win_rate = performance.get("win_rate", 0.5)
        recent_pnl = performance.get("recent_pnl", 0.0)
        
        # If winning, size up. If losing, size down
        performance_multiplier = 1.0
        if win_rate > 0.55 and recent_pnl > 0:
            performance_multiplier = 1.3  # 30% larger after wins
        elif win_rate < 0.45 or recent_pnl < -50:
            performance_multiplier = 0.7  # 30% smaller after losses
        
        # Kelly Criterion component (if we have enough trade history)
        kelly_multiplier = 1.0
        if performance.get("total_trades", 0) > 10:
            avg_win = performance.get("avg_win", 0.0)
            avg_loss = abs(performance.get("avg_loss", -1.0))
            if avg_loss > 0:
                kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                kelly_multiplier = max(0.5, min(1.5, kelly_fraction))
        
        # Calculate final size
        size = (base_size * 
                conf_multiplier * 
                vol_multiplier * 
                quality_multiplier * 
                performance_multiplier * 
                kelly_multiplier)
        
        # Enforce hard limits
        min_size = config.trading.max_position_size * 0.25  # At least 25% of max ($300 with $1200 max)
        max_size = config.trading.max_position_size  # Never exceed max
        
        # Check available margin
        available = portfolio_state.get("available_margin", max_size)
        size = min(size, available * 0.8)  # Use max 80% of available margin
        
        final_size = max(min_size, min(max_size, size))
        
        logger.info(f"[{self.bot_name}] Dynamic sizing: Base=${base_size:.0f} -> Final=${final_size:.0f} "
                   f"(conf={conf_multiplier:.2f}x, vol={vol_multiplier:.2f}x, "
                   f"quality={quality_multiplier:.2f}x, perf={performance_multiplier:.2f}x)")
        
        return final_size
    
    def _get_required_close_confidence(self, time_in_position_seconds: float = None) -> float:
        """
        Dynamically adjust required close confidence based on time in position
        """
        base = self.close_confidence_threshold
        minimum = self.close_confidence_min
        decay_seconds = max(self.close_confidence_decay_minutes * 60, 1)
        
        if time_in_position_seconds is None:
            return base
        
        decay_ratio = min(time_in_position_seconds / decay_seconds, 1.0)
        required = base - (base - minimum) * decay_ratio
        return max(minimum, required)
    
    async def start(self):
        """Start the trading agent"""
        self.running = True
        logger.info("Starting Vibe Trader...")
        
        # Set leverage for the symbol before trading
        try:
            await self.aster.set_leverage(self.symbol, config.trading.leverage)
            logger.success(f"✅ [{self.bot_name}] Set leverage to {config.trading.leverage}x for {self.symbol}")
        except Exception as e:
            logger.warning(f"[{self.bot_name}] Could not set leverage: {e}. Using account default.")
        
        try:
            while self.running:
                await self._trading_cycle()
                await asyncio.sleep(config.trading.update_interval)
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
            raise
    
    def stop(self):
        """Stop the trading agent"""
        self.running = False
        logger.info("Stopping Vibe Trader...")
    
    async def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # 1. Gather market data
            market_data = await self._gather_market_data()
            
            # 2. Analyze current positions
            portfolio_state = await self._analyze_portfolio()
            
            # 🛡️ 2.5. Check for missing protective orders and fix them
            await self._ensure_protective_orders(portfolio_state, market_data)
            
            # 3. Get AI decision
            decision = await self._get_ai_decision(market_data, portfolio_state)
            
            # 4. Execute trades if needed
            if decision.get("action") != "hold":
                await self._execute_decision(decision, market_data)
            
            # 5. Log decision
            self._log_decision(decision, market_data, portfolio_state)
            
        except ValueError as e:
            # Balance unavailable - skip this cycle safely
            if "balance" in str(e).lower() or "usdt" in str(e).lower():
                logger.warning(f"[{self.bot_name}] Skipping trading cycle - balance unavailable. Will retry next cycle.")
            else:
                logger.error(f"[{self.bot_name}] ValueError in trading cycle: {e}")
        except Exception as e:
            logger.error(f"[{self.bot_name}] Error in trading cycle: {e}")
    
    async def _gather_market_data(self) -> Dict[str, Any]:
        """
        Gather comprehensive market data with multiple timeframes and technical analysis
        
        Returns:
            Dictionary containing market data with indicators
        """
        try:
            symbol = self.symbol
            
            # Get ticker for current price
            ticker = await self.aster.get_ticker(symbol)
            
            # Gather multiple timeframes for comprehensive analysis
            # Reduced to 3 timeframes to prevent API bans (was 5)
            timeframes = {
                "1m": {"limit": 360, "label": "Last 6h (1m)"},      # 6 hours - primary for entries
                "5m": {"limit": 288, "label": "Last 24h (5m)"},     # 24 hours - trend confirmation
                "15m": {"limit": 96, "label": "Last 24h (15m)"}     # 24 hours - structure
            }
            
            multi_timeframe_data = {}
            
            # Fetch all timeframes
            for interval, config_data in timeframes.items():
                try:
                    klines = await self.aster.get_klines(
                        symbol, 
                        interval=interval, 
                        limit=config_data["limit"]
                    )
                    
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
                    
                    # Perform technical analysis on this timeframe
                    analysis = self.market_analyzer.analyze_full_market(candles)
                    
                    multi_timeframe_data[interval] = {
                        "candles": candles,
                        "analysis": analysis,
                        "label": config_data["label"]
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not fetch {interval} data: {e}")
            
            # Primary timeframe for main analysis (1m for aggressive trading)
            primary_tf = "1m"
            primary_candles = multi_timeframe_data.get(primary_tf, {}).get("candles", [])
            primary_analysis = multi_timeframe_data.get(primary_tf, {}).get("analysis", {})
            
            return {
                "timestamp": datetime.now().isoformat(),
                "ticker": ticker,
                "candles": primary_candles,  # Keep for backward compatibility
                "analysis": primary_analysis,  # Primary timeframe analysis
                "multi_timeframe": multi_timeframe_data,  # All timeframes
                "current_price": float(ticker.get('lastPrice', 0))
            }
        except Exception as e:
            logger.error(f"Error gathering market data: {e}")
            return {}
    
    async def _ensure_protective_orders(
        self, 
        portfolio_state: Dict[str, Any],
        market_data: Dict[str, Any]
    ):
        """
        Ensure all positions have proper stop loss and take profit orders
        Auto-fix if missing!
        Also cleans up orphaned orders when no position exists.
        """
        try:
            positions = portfolio_state.get('positions', [])
            open_orders = portfolio_state.get('open_orders', [])
            
            # Check if we have a position for this symbol
            has_position = False
            for pos in positions:
                if pos.get('symbol') == self.symbol and float(pos.get('positionAmt', 0)) != 0:
                    has_position = True
                    break
            
            # 🧹 CLEANUP: If NO position but we have orders, cancel them (orphaned orders)
            if not has_position and open_orders:
                logger.warning(f"🧹 [{self.bot_name}] Found {len(open_orders)} ORPHANED orders with no position!")
                logger.warning(f"🧹 [{self.bot_name}] Cleaning up old orders...")
                
                try:
                    await self.aster.cancel_all_orders(self.symbol)
                    logger.success(f"✅ [{self.bot_name}] Cancelled {len(open_orders)} orphaned orders")
                except Exception as e:
                    logger.error(f"Could not cancel orphaned orders: {e}")
                
                return  # Nothing more to do
            
            # If no position and no orders, we're clean
            if not has_position:
                return
            
            # 🛡️ POSITION PROTECTION: Ensure SL and TP are set
            # Check each position for this symbol
            for pos in positions:
                if pos.get('symbol') != self.symbol:
                    continue
                    
                pos_amt = float(pos.get('positionAmt', 0))
                if pos_amt == 0:
                    continue
                
                # We have a position! Check if we have SL and TP
                entry_price = float(pos.get('entryPrice', 0))
                position_side = "long" if pos_amt > 0 else "short"
                quantity = abs(pos_amt)
                
                # Check what orders we have
                has_stop_loss = any('STOP' in order.get('type', '') for order in open_orders)
                has_take_profit = any(
                    'TAKE_PROFIT' in order.get('type', '') or 
                    ('LIMIT' in order.get('type', '') and order.get('side') != ('BUY' if pos_amt > 0 else 'SELL'))
                    for order in open_orders
                )
                
                # Get ATR for calculations
                analysis = market_data.get('analysis', {})
                current_price = market_data.get('current_price', entry_price)
                atr = analysis.get('atr', current_price * 0.02)
                
                # 🛡️ Missing Stop Loss - SET IT!
                if not has_stop_loss:
                    logger.warning(f"⚠️ [{self.bot_name}] MISSING STOP LOSS! Setting protective stop...")
                    
                    if position_side == "long":
                        stop_price = entry_price - (atr * 2.0)
                        close_side = "SELL"
                    else:
                        stop_price = entry_price + (atr * 2.0)
                        close_side = "BUY"
                    
                    try:
                        await self.aster.set_stop_loss(
                            self.symbol, 
                            stop_price, 
                            quantity,
                            side=close_side
                        )
                        logger.success(f"✅ [{self.bot_name}] Emergency stop loss set at ${stop_price:.4f}")
                    except Exception as e:
                        logger.error(f"Could not set emergency stop loss: {e}")
                
                # 🎯 Missing Take Profit - SET IT INTELLIGENTLY!
                if not has_take_profit:
                    logger.warning(f"⚠️ [{self.bot_name}] MISSING TAKE PROFIT! Calculating smart target...")
                    
                    # IMPORTANT: Calculate TP based on CURRENT price (not entry)
                    # This ensures TP is always ahead of the market
                    
                    # Also check if we're already in profit
                    if position_side == "long":
                        current_pnl_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        # If already profitable, lock in gains with TP above current
                        # If at loss, set TP at target profit level
                        if current_price > entry_price:
                            # LONG in profit (price rose)
                            tp_price = current_price + (atr * 1.5)  # 1.5x ATR from CURRENT
                            logger.info(f"[{self.bot_name}] LONG in profit ({current_pnl_pct:+.2f}%)")
                            logger.info(f"[{self.bot_name}] Setting TP from current: ${current_price:.4f} + 1.5xATR = ${tp_price:.4f}")
                        else:
                            # LONG at breakeven or loss (price dropped or flat)
                            tp_price = entry_price + (atr * 3.0)  # 3x ATR from ENTRY  
                            logger.info(f"[{self.bot_name}] LONG at breakeven/loss ({current_pnl_pct:+.2f}%)")
                            logger.info(f"[{self.bot_name}] Setting TP from entry: ${entry_price:.4f} + 3xATR = ${tp_price:.4f}")
                        
                        close_side = "SELL"
                    else:
                        # SHORT position logic
                        current_pnl_pct = ((entry_price - current_price) / entry_price) * 100
                        
                        if current_price < entry_price:
                            # SHORT in profit (price dropped)
                            # Set TP between current and entry to lock in gains
                            # Don't go too aggressive or it'll trigger immediately
                            midpoint = (entry_price + current_price) / 2
                            tp_price = midpoint - (atr * 0.5)  # Slightly below midpoint
                            logger.info(f"[{self.bot_name}] SHORT in profit ({current_pnl_pct:+.2f}%)")
                            logger.info(f"[{self.bot_name}] Setting TP to lock gains: ${tp_price:.4f} (between entry ${entry_price:.4f} and current ${current_price:.4f})")
                        else:
                            # SHORT at breakeven or loss (price rose)
                            tp_price = entry_price - (atr * 3.0)  # 3x ATR below entry
                            logger.info(f"[{self.bot_name}] SHORT at loss ({current_pnl_pct:+.2f}%)")
                            logger.info(f"[{self.bot_name}] Setting TP from entry: ${entry_price:.4f} - 3xATR = ${tp_price:.4f}")
                        
                        close_side = "BUY"
                    
                    try:
                        await self.aster.set_take_profit(
                            self.symbol,
                            tp_price,
                            quantity,
                            side=close_side
                        )
                        logger.success(f"✅ [{self.bot_name}] Auto-set take profit at ${tp_price:.4f}")
                    except Exception as e:
                        logger.error(f"Could not set take profit: {e}")
                
                # Log protective orders status
                if has_stop_loss and has_take_profit:
                    logger.debug(f"✅ [{self.bot_name}] Position fully protected (SL + TP active)")
                
        except Exception as e:
            logger.error(f"Error checking protective orders: {e}")
    
    async def _analyze_portfolio(self) -> Dict[str, Any]:
        """
        Analyze current portfolio state with risk metrics
        
        Returns:
            Dictionary containing portfolio analysis
        """
        try:
            # Try to get positions (might work even if balance doesn't)
            positions = []
            total_pnl = 0.0
            total_exposure = 0.0
            
            try:
                # Use shared account cache to get positions (already fetched for balance)
                account = await self.account_cache.get_account_data()
                if account:
                    positions = account.get("positions", [])
                
                # Calculate total exposure and PnL
                for pos in positions:
                    if float(pos.get("positionAmt", 0)) != 0:
                        notional = abs(float(pos.get("notional", 0)))
                        total_exposure += notional
                        total_pnl += float(pos.get("unrealizedProfit", 0))
            except Exception as e:
                logger.warning(f"Could not fetch positions: {e}, continuing with empty portfolio")
            
            # Get open orders (including stop loss and take profit)
            open_orders = []
            try:
                open_orders = await self.aster.get_open_orders(self.symbol)
                logger.debug(f"[{self.bot_name}] Found {len(open_orders)} open orders for {self.symbol}")
            except Exception as e:
                logger.warning(f"Could not fetch open orders: {e}")
            
            # Get recent trade performance for adaptive sizing
            trade_stats = self.trade_tracker.get_stats()
            win_rate = trade_stats.get("win_rate", 0.0)
            avg_win = trade_stats.get("avg_win_pct", 0.0)
            avg_loss = trade_stats.get("avg_loss_pct", 0.0)
            recent_pnl = trade_stats.get("total_pnl_usd", 0.0)
            daily_performance = self.trade_tracker.get_recent_performance(hours=24)
            
            # Get actual balance using shared cache - CRITICAL for safe position sizing
            try:
                # Use shared account cache to reduce API calls (all bots share one fetch)
                account = await self.account_cache.get_account_data()
                if not account:
                    raise ValueError("Shared account cache returned no data")
                
                # Extract USDT balance from account data
                usdt_balance = 0.0
                assets = account.get('assets', [])
                for asset in assets:
                    if asset.get('asset') == 'USDT':
                        usdt_balance = float(asset.get('walletBalance', 0))
                        break
                
                # Fallback to availableBalance if assets array is empty
                if usdt_balance == 0:
                    usdt_balance = float(account.get('availableBalance', 0))
                
                # CRITICAL: Don't trade if we can't determine balance
                if usdt_balance <= 0:
                    logger.error(f"[{self.bot_name}] ⚠️ CRITICAL: No USDT balance found! Skipping trade for safety.")
                    raise ValueError("No valid USDT balance available - cannot safely size positions")
                
                estimated_balance = usdt_balance
                logger.debug(f"[{self.bot_name}] Balance fetched from shared cache: ${estimated_balance:.2f} USDT (cache age: {self.account_cache.get_cache_age():.1f}s)")
            except Exception as e:
                logger.error(f"[{self.bot_name}] ⚠️ CRITICAL: Could not fetch balance: {e}")
                logger.error(f"[{self.bot_name}] Skipping trading cycle - balance unavailable is unsafe!")
                raise ValueError(f"Cannot fetch balance: {e}") from e
            
            return {
                "balance": {
                    "available": estimated_balance,
                    "total": estimated_balance
                },
                "positions": positions,
                "open_orders": open_orders,
                "total_exposure": total_exposure,
                "available_margin": max(0, estimated_balance - total_exposure),
                "performance": {
                    "win_rate": win_rate,
                    "avg_win": avg_win,
                    "avg_loss": avg_loss,
                    "recent_pnl": recent_pnl,
                    "total_trades": trade_stats.get("total_trades", 0),
                    "daily": daily_performance
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return {
                "balance": {"available": 0, "total": 0},
                "positions": [],
                "open_orders": [],
                "total_exposure": 0,
                "available_margin": 0,
                "performance": {
                    "win_rate": 0.0,
                    "avg_win": 0.0,
                    "avg_loss": 0.0,
                    "recent_pnl": 0.0,
                    "total_trades": 0,
                    "daily": {
                        "trades": 0,
                        "pnl_usd": 0.0,
                        "win_rate": 0.0,
                        "hours": 24
                    }
                }
            }
    
    async def _get_ai_decision(
        self, 
        market_data: Dict[str, Any], 
        portfolio_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get trading decision from LLM
        
        Args:
            market_data: Current market data
            portfolio_state: Current portfolio state
            
        Returns:
            Trading decision dictionary
        """
        prompt = self._build_trading_prompt(market_data, portfolio_state)
        
        try:
            response = await self.llm.get_completion(
                prompt=prompt,
                system_message=self._get_system_message()
            )
            
            # Parse LLM response into structured decision
            decision = self._parse_llm_response(response)
            decision["raw_response"] = response
            decision["timestamp"] = datetime.now().isoformat()
            
            return decision
            
        except Exception as e:
            logger.error(f"Error getting AI decision: {e}")
            return {"action": "hold", "reason": f"Error: {e}"}
    
    def _build_trading_prompt(
        self, 
        market_data: Dict[str, Any], 
        portfolio_state: Dict[str, Any]
    ) -> str:
        """Build sophisticated trading prompt with multi-timeframe analysis"""
        
        # Get current price and 24h data
        ticker = market_data.get('ticker', {})
        current_price = float(ticker.get('lastPrice', 0))
        change_24h = ticker.get('priceChangePercent', 'N/A')
        
        # Primary timeframe analysis (1m for aggressive trading)
        analysis = market_data.get('analysis', {})
        
        # Build technical indicators summary
        indicators_summary = f"""
TECHNICAL INDICATORS (1m timeframe):
═══════════════════════════════════════════════════════════
RSI (14): {analysis.get('rsi', 50):.1f} {'🔥 OVERSOLD' if analysis.get('rsi', 50) < 30 else '❄️ OVERBOUGHT' if analysis.get('rsi', 50) > 70 else '⚖️ NEUTRAL'}
MACD: Line={analysis.get('macd', {}).get('macd', 0):.2f}, Signal={analysis.get('macd', {}).get('signal', 0):.2f}, 
      Histogram={analysis.get('macd', {}).get('histogram', 0):.2f} {'📈 BULLISH' if analysis.get('macd', {}).get('histogram', 0) > 0 else '📉 BEARISH'}
      
Bollinger Bands:
  Upper: ${analysis.get('bollinger_bands', {}).get('upper', 0):.2f}
  Middle: ${analysis.get('bollinger_bands', {}).get('middle', 0):.2f}
  Lower: ${analysis.get('bollinger_bands', {}).get('lower', 0):.2f}
  Position: {analysis.get('bollinger_bands', {}).get('position', 0.5)*100:.0f}% {'⚠️ Near upper band' if analysis.get('bollinger_bands', {}).get('position', 0.5) > 0.8 else '⚠️ Near lower band' if analysis.get('bollinger_bands', {}).get('position', 0.5) < 0.2 else ''}
  Width: {analysis.get('bollinger_bands', {}).get('width', 0)*100:.2f}% {'🌊 HIGH VOLATILITY' if analysis.get('bollinger_bands', {}).get('width', 0) > 0.05 else '😴 LOW VOLATILITY'}

ATR (14): ${analysis.get('atr', 0):.2f} ({analysis.get('atr_percent', 0):.2f}% of price)

Momentum (10): {analysis.get('momentum', 0):+.2f}%

Volume:
  Avg Volume: {analysis.get('volume_profile', {}).get('avg_volume', 0):.0f}
  Current vs Avg: {analysis.get('volume_profile', {}).get('volume_ratio', 1):.2f}x {'🚀 SURGE' if analysis.get('volume_profile', {}).get('volume_ratio', 1) > 1.5 else '💤 LOW' if analysis.get('volume_profile', {}).get('volume_ratio', 1) < 0.5 else ''}
  Trend: {analysis.get('volume_profile', {}).get('volume_trend', 0)*100:+.1f}%

Volatility:
  Std Dev: {analysis.get('volatility', {}).get('std_dev', 0):.2f}%
  Percentile: {analysis.get('volatility', {}).get('volatility_percentile', 50):.0f}th percentile

Trend Analysis:
  Trend: {analysis.get('trend', {}).get('trend', 'neutral').upper()} 
  Strength: {analysis.get('trend', {}).get('strength', 0)*100:.2f}%
  
Market Structure:
  Structure: {analysis.get('market_structure', {}).get('structure', 'ranging').upper()}
  Support: ${analysis.get('market_structure', {}).get('support', 0):.2f}
  Resistance: ${analysis.get('market_structure', {}).get('resistance', 0):.2f}
  Breakout Probability: {analysis.get('market_structure', {}).get('breakout_probability', 0)*100:.0f}%

⭐ TRADE QUALITY SCORE: {analysis.get('trade_quality_score', 50):.0f}/100
"""
        
        # Multi-timeframe alignment
        mtf_data = market_data.get('multi_timeframe', {})
        mtf_summary = "\nMULTI-TIMEFRAME ANALYSIS:\n═══════════════════════════════════════════════════════════\n"
        
        for tf in ['5m', '15m', '1h', '4h']:
            if tf in mtf_data:
                tf_analysis = mtf_data[tf].get('analysis', {})
                tf_trend = tf_analysis.get('trend', {}).get('trend', 'neutral')
                tf_rsi = tf_analysis.get('rsi', 50)
                tf_macd_hist = tf_analysis.get('macd', {}).get('histogram', 0)
                
                mtf_summary += f"{tf.upper():>4}: {tf_trend.upper():>8} | RSI={tf_rsi:.0f} | MACD={'🟢' if tf_macd_hist > 0 else '🔴'}\n"
        
        # Account balance and capital info
        balance_info = portfolio_state.get('balance', {})
        total_balance = balance_info.get('total', 0)
        available_balance = balance_info.get('available', 0)
        total_exposure = portfolio_state.get('total_exposure', 0)
        
        account_summary = f"""
ACCOUNT STATUS:
═══════════════════════════════════════════════════════════
Total Balance: ${total_balance:.2f}
Available Margin: ${available_balance:.2f}
Current Exposure: ${total_exposure:.2f} ({total_exposure/total_balance*100 if total_balance > 0 else 0:.1f}% of capital)
Max Position Size: ${config.trading.max_position_size:.2f}
Recommended Size Range: ${total_balance * 0.2:.2f} - ${total_balance * 0.5:.2f} (20-50% of balance)
"""
        
        # Performance feedback (learning loop)
        performance = portfolio_state.get('performance', {})
        perf_summary = f"""
YOUR RECENT PERFORMANCE:
═══════════════════════════════════════════════════════════
Total Trades: {performance.get('total_trades', 0)}
Win Rate: {performance.get('win_rate', 0)*100:.1f}%
Avg Win: {performance.get('avg_win', 0):+.2f}%
Avg Loss: {performance.get('avg_loss', 0):+.2f}%
Recent P&L: ${performance.get('recent_pnl', 0):+.2f}
"""
        daily_perf = performance.get('daily', {})
        daily_pnl = daily_perf.get('pnl_usd', 0.0)
        daily_trades = daily_perf.get('trades', 0)
        daily_win_rate = daily_perf.get('win_rate', 0.0)
        daily_hours = daily_perf.get('hours', 24)
        daily_target_pct = config.trading.daily_target_percent * 100
        equity_pct = (daily_pnl / total_balance * 100) if total_balance else 0.0
        daily_target_value = total_balance * config.trading.daily_target_percent
        daily_summary = f"""
DAILY PERFORMANCE (Last {daily_hours}h):
═══════════════════════════════════════════════════════════
Realized P&L: ${daily_pnl:+.2f} ({equity_pct:+.2f}% of equity)
Trades Closed: {daily_trades} | Win Rate: {daily_win_rate:.1f}%
Daily Target: +{daily_target_pct:.2f}% (≈ ${daily_target_value:.2f})
Progress Toward Target: {equity_pct / daily_target_pct * 100 if daily_target_pct else 0:.1f}%"""
        
        # Position and orders info
        positions = portfolio_state.get('positions', [])
        open_orders = portfolio_state.get('open_orders', [])
        
        # Check if we have an ACTUAL position (non-zero amount for our symbol)
        has_position = any(
            pos.get('symbol') == self.symbol and float(pos.get('positionAmt', 0)) != 0 
            for pos in positions
        )
        
        # Format position info with protective orders
        if has_position:
            position_info = f"⚠️ OPEN POSITION:\n"
            for pos in positions:
                if float(pos.get('positionAmt', 0)) != 0:
                    side = "LONG" if float(pos.get('positionAmt', 0)) > 0 else "SHORT"
                    entry = float(pos.get('entryPrice', 0))
                    pnl = float(pos.get('unrealizedProfit', 0))
                    pnl_pct = (pnl / abs(float(pos.get('notional', 1)))) * 100 if pos.get('notional') else 0
                    
                    position_info += f"  {side} {abs(float(pos.get('positionAmt', 0)))} @ ${entry:.4f}\n"
                    position_info += f"  Entry Price: ${entry:.4f}\n"
                    position_info += f"  Current Price: ${current_price:.4f}\n"
                    position_info += f"  Unrealized P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)\n"
            
            # Show protective orders (SL/TP)
            has_sl = False
            has_tp = False
            
            if open_orders:
                position_info += f"\n📋 PROTECTIVE ORDERS ({len(open_orders)}):\n"
                for order in open_orders:
                    order_type = order.get('type', 'UNKNOWN')
                    side = order.get('side', '')
                    price = float(order.get('stopPrice', order.get('price', 0)))
                    qty = float(order.get('origQty', 0))
                    
                    if 'STOP' in order_type and 'TAKE_PROFIT' not in order_type:
                        position_info += f"  🛡️ STOP LOSS: {side} {qty} @ ${price:.4f}\n"
                        has_sl = True
                    elif 'TAKE_PROFIT' in order_type:
                        position_info += f"  🎯 TAKE PROFIT: {side} {qty} @ ${price:.4f}\n"
                        has_tp = True
                    elif 'LIMIT' in order_type:
                        position_info += f"  🎯 TAKE PROFIT: {side} {qty} @ ${price:.4f}\n"
                        has_tp = True
                    else:
                        position_info += f"  📌 {order_type}: {side} {qty} @ ${price:.4f}\n"
            
            # Warn if missing protection
            if not has_sl:
                position_info += f"\n  ⚠️ WARNING: NO STOP LOSS SET! Position is UNPROTECTED!\n"
            if not has_tp:
                position_info += f"  ⚠️ WARNING: NO TAKE PROFIT SET! No exit target!\n"
            
            position_status = position_info.strip()
        else:
            position_status = "✅ NO OPEN POSITION - Looking for HIGH QUALITY setups"
        
        # Build the aggressive prompt
        prompt = f"""
🎯 AGGRESSIVE ALPHA-SEEKING CRYPTO TRADER

You are an elite futures trader on Aster DEX. Your mission: GENERATE ALPHA.
Find edges, time entries perfectly, size positions optimally.

MARKET: {self.symbol}
Current Price: ${current_price:.2f}
24h Change: {change_24h}%

{indicators_summary}

{mtf_summary}

{account_summary}

{perf_summary}

{daily_summary}

POSITION STATUS: {position_status}

═══════════════════════════════════════════════════════════
🎲 DECISION FRAMEWORK:
═══════════════════════════════════════════════════════════

1. IDENTIFY THE EDGE:
   - What patterns do you see? (trend, reversal, breakout, range)
   - Do multiple timeframes align?
   - Is volume confirming the move?
   - What's the trade quality score telling you?

2. POSITION SIZING STRATEGY:
   - Your account: ${total_balance:.2f} total
   - Recommended range: ${total_balance * 0.2:.2f} - ${total_balance * 0.5:.2f} (20-50% of YOUR balance)
   - Since you're PATIENT and SELECTIVE, use BIGGER positions when you do trade
   - Scale UP if: High confidence (>75), strong setup, aligned timeframes
   - Scale DOWN if: High volatility, conflicting signals, low quality score
   - Consider your available margin (${available_balance:.2f}) when sizing
   - DO NOT specify exact size_usd - the system will calculate dynamically based on your confidence and trade quality

3. RISK MANAGEMENT:
   - ATR-based stops: Set stop_loss using current ATR (${analysis.get('atr', 0):.2f})
   - Risk/Reward: Minimum 2:1 RR ratio
   - Stop distance: Use 1.5-2x ATR for breathing room
   - Take profit: 3-4x ATR or at key resistance/support

4. TIMING:
   - Enter on confirmation (volume surge, breakout, reversal signal)
   - Avoid chop (low volume, tight BB, ranging)
   - Best setups: Trend + RSI extreme + MACD cross + Volume

5. CONFIDENCE CALIBRATION:
   - FOR OPENING: 95-100: Perfect setup, all signals aligned → BIG size
   - FOR OPENING: 85-94: Strong setup, most signals aligned → LARGE size
   - FOR OPENING: 75-84: Good setup, mixed signals but edge present → MEDIUM size
   - FOR OPENING: 60-74: Marginal setup, small edge → SMALL size
   - FOR OPENING: <60: No trade (HOLD)
   
   - FOR CLOSING: Need 75%+ confidence (strong reversal signal required)
   - FOR CLOSING: <75%: Keep holding, trust your stop loss

═══════════════════════════════════════════════════════════
🚀 YOUR MISSION:
═══════════════════════════════════════════════════════════

Analyze EVERYTHING above. Think like a pro:
- What's the dominant force? (Bulls or bears)
- Where's the smart money? (volume, structure)
- What's the highest probability move?
- Is this a trade worth taking?

🚨 CRITICAL POSITION RULES:
═══════════════════════════════════════════════════════════
If NO position: You can go LONG, SHORT, or HOLD (trade at >60 confidence)
  - "long" = Open bullish position
  - "short" = Open bearish position  
  - "hold" = Wait for better setup (only if confidence <60%)

If HAVE position: You can ONLY use "hold" or "close"
  - "hold" = Keep current position open (DEFAULT - be patient!)
  - "close" = Exit current position NOW (only if strong reversal signal)
  - ❌ NEVER use "long" or "short" when you have a position!
  - ❌ If you want to reverse (long→short), say "close" first
  
🛡️ ANTI-OVERTRADING RULES:
  - DON'T close positions just because price moved 0.5%
  - DON'T panic exit on small indicator changes
  - DO let positions breathe (minimum 5 minutes)
  - DO close only on STRONG reversal signals (RSI flip, MACD cross, volume divergence)
  - Your stop loss will protect you - trust it!
  - Better to HOLD and let the trade develop than flip-flop

⚠️ PROTECTIVE ORDERS (CRITICAL):
  - YOU determine optimal stop_loss and take_profit based on YOUR analysis
  - Use support/resistance levels, volatility (ATR), and market structure
  - stop_loss: Position where market would invalidate your thesis
  - take_profit: Target based on Fibonacci, resistance levels, or risk/reward
  - AIM for at least 2:1 risk/reward ratio (reward > 2x risk)
  - Be SMART: tighter stops in volatile conditions, wider in stable trends
  - If market structure is unclear, use ATR-based: SL at -2x ATR, TP at +3-4x ATR

Respond with JSON ONLY (no markdown, no explanation outside JSON):
{{
    "action": "long" | "short" | "close" | "hold",
    "symbol": "{self.symbol}",
    "stop_loss": <exact_price_level_you_decide>,
    "take_profit": <exact_price_level_you_decide>,
    "reasoning": "Technical analysis with specific indicators cited",
    "confidence": <0-100>,
    "edge_identified": "Brief description of your edge",
    "timeframe_alignment": "bullish" | "bearish" | "mixed" | "neutral",
    "expected_rr": <expected_risk_reward_ratio>
}}

NOTE: Do NOT include "size_usd" field - sizing is handled automatically based on your confidence and market conditions.

🎯 TRADE SMART. TRADE AGGRESSIVE. FIND ALPHA.
"""
        
        return prompt
    
    def _get_system_message(self) -> str:
        """Get system message for LLM"""
        return """You are an ELITE cryptocurrency futures trader and market maker with 10+ years experience.

🧠 YOUR EXPERTISE:
- Advanced technical analysis (price action, market structure, order flow)
- Multi-timeframe correlation and trend identification
- Volatility trading and options market insights
- Statistical arbitrage and mean reversion strategies
- Momentum and breakout trading with precision entries
- Risk management: Kelly Criterion, position sizing, portfolio heat
- Trading psychology: discipline, patience, objective decision-making

🎯 YOUR EDGE:
You identify asymmetric risk/reward opportunities where probability and payoff align.
You recognize when markets offer genuine alpha vs random noise.
You understand that NOT trading is often the best trade.

⚡ YOUR MINDSET:
- AGGRESSIVE when edge is clear (high quality setups)
- PATIENT when edge is unclear (wait for A+ setups)
- DISCIPLINED with stops (cut losses fast, let winners run)
- ADAPTIVE to changing market regimes (trend vs range vs breakout)

📊 YOUR PROCESS:
1. Analyze ALL provided indicators and timeframes
2. Synthesize information into a coherent market view
3. Identify specific technical triggers for entry/exit
4. Assess trade quality and confidence honestly
5. Express conviction through confidence score (not position size)

🚀 YOUR MISSION: Generate consistent positive returns through skilled pattern recognition,
disciplined risk management, and high-quality trade selection. Every decision must be
backed by technical evidence. Trade like your career depends on it - because it does."""
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured decision"""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            decision = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["action", "reasoning", "confidence"]
            if not all(field in decision for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.debug(f"Raw response: {response}")
            return {
                "action": "hold",
                "reasoning": f"Failed to parse LLM response: {e}",
                "confidence": 0
            }
    
    async def _execute_decision(self, decision: Dict[str, Any], market_data: Dict[str, Any]):
        """
        Execute trading decision with dynamic sizing and ATR-based stops
        
        Args:
            decision: Trading decision from LLM
            market_data: Current market data for price conversion
        """
        action = decision.get("action")
        symbol = decision.get("symbol")
        confidence = decision.get("confidence", 0)
        
        # Only trade if confidence is high enough
        if confidence < 60:
            logger.info(f"⏸️ [{self.bot_name}] Skipping trade - confidence too low: {confidence}% (need ≥60%)")
            return
        
        # Get portfolio state for dynamic sizing
        portfolio_state = await self._analyze_portfolio()
        
        # 🛡️ CRITICAL: Prevent conflicting positions!
        # Check if we already have a position for this symbol
        positions = portfolio_state.get('positions', [])
        total_balance = portfolio_state.get('balance', {}).get('total', 0)
        has_position = any(
            p.get('symbol') == symbol and float(p.get('positionAmt', 0)) != 0 
            for p in positions
        )
        
        # Track current position P&L for profit-protection logic
        position_profit = 0.0
        profit_lock_active = False
        if has_position and total_balance:
            for pos in positions:
                if pos.get('symbol') == symbol and float(pos.get('positionAmt', 0)) != 0:
                    position_profit = float(pos.get('unrealizedProfit', 0))
                    break
            profit_ratio = position_profit / total_balance
            profit_lock_active = profit_ratio >= self.pnl_lock_percent
            if profit_lock_active:
                logger.info(f"💰 [{self.bot_name}] Profit lock active: unrealized ${position_profit:.2f} "
                            f"({profit_ratio*100:.2f}% of equity)")
        
        time_in_position = None
        if self.last_trade_time:
            time_in_position = (datetime.now() - self.last_trade_time).total_seconds()
        
        if has_position:
            # If we have a position, only allow HOLD or CLOSE actions
            if action in ["long", "short"]:
                logger.warning(f"⚠️ [{self.bot_name}] AI tried to open {action.upper()} but we already have a position!")
                logger.warning(f"⚠️ [{self.bot_name}] Converting to CLOSE action instead (AI wants to reverse direction)")
                action = "close"
                decision["action"] = "close"  # Update the decision
            
            # 🛡️ ANTI-OVERTRADING: Require minimum hold time before closing
            if action == "close" and time_in_position is not None and not profit_lock_active:
                if time_in_position < self.min_hold_time:
                    time_remaining = int(self.min_hold_time - time_in_position)
                    logger.info(f"🕐 [{self.bot_name}] Position too new! Held for {int(time_in_position)}s, "
                               f"need {self.min_hold_time}s. Waiting {time_remaining}s more...")
                    logger.info(f"🛡️ [{self.bot_name}] Converting CLOSE to HOLD (anti-overtrading protection)")
                    action = "hold"
                    decision["action"] = "hold"
                    return  # Don't execute, just log
            
            # 🎯 RAISE THE BAR: Need higher confidence to close (prevent panic exits)
            required_confidence = self._get_required_close_confidence(time_in_position)
            if action == "close" and not profit_lock_active and confidence < required_confidence:
                logger.info(f"🤔 [{self.bot_name}] AI wants to CLOSE but confidence only {confidence}% "
                            f"(need {required_confidence:.1f}%+). Holding position.")
                action = "hold"
                decision["action"] = "hold"
                return  # Don't execute
        
        try:
            if action in ["long", "short"]:
                # Get current market analysis
                analysis = market_data.get('analysis', {})
                current_price = float(market_data.get('ticker', {}).get('lastPrice', 0))
                atr = analysis.get('atr', current_price * 0.02)  # Fallback to 2% of price
                atr_percent = analysis.get('atr_percent', 2.0)
                trade_quality = analysis.get('trade_quality_score', 50)
                
                if current_price == 0:
                    logger.error("Cannot execute trade - no valid price")
                    return
                
                # 🎯 DYNAMIC POSITION SIZING
                size_usd = self._calculate_dynamic_position_size(
                    confidence=confidence,
                    volatility=atr_percent,
                    trade_quality=trade_quality,
                    portfolio_state=portfolio_state
                )
                
                # Calculate asset quantity from dynamically calculated USD notional
                quantity = size_usd / current_price
                
                # For ASTERUSDT, round to whole number. For BTCUSDT, use 3 decimals
                if "ASTER" in symbol:
                    quantity = round(quantity, 0)  # Whole numbers for ASTER
                    min_qty = 1
                else:
                    quantity = round(quantity, 3)  # 3 decimals for BTC
                    min_qty = 0.001
                
                if quantity < min_qty:
                    logger.warning(f"Position size too small: {quantity}, increasing to minimum {min_qty}")
                    quantity = min_qty
                
                # 🎯 ATR-BASED DYNAMIC STOPS
                # Calculate stop loss if not provided or improve it with ATR
                atr_multiplier_stop = 2.0  # 2x ATR for stop loss
                atr_multiplier_tp = 4.0    # 4x ATR for take profit (2:1 RR)
                
                if action == "long":
                    # For longs: stop below, target above
                    calculated_stop = current_price - (atr * atr_multiplier_stop)
                    calculated_tp = current_price + (atr * atr_multiplier_tp)
                else:
                    # For shorts: stop above, target below
                    calculated_stop = current_price + (atr * atr_multiplier_stop)
                    calculated_tp = current_price - (atr * atr_multiplier_tp)
                
                # Use AI's stop/tp if provided and reasonable, otherwise use ATR-based
                ai_stop_loss = decision.get("stop_loss")
                ai_take_profit = decision.get("take_profit")
                
                if ai_stop_loss and ai_take_profit:
                    logger.info(f"[{self.bot_name}] 🤖 AI provided TP/SL: SL=${ai_stop_loss:.4f}, TP=${ai_take_profit:.4f}")
                    stop_loss = ai_stop_loss
                    take_profit = ai_take_profit
                else:
                    logger.info(f"[{self.bot_name}] 📊 Using ATR-based TP/SL: SL=${calculated_stop:.4f}, TP=${calculated_tp:.4f}")
                    stop_loss = calculated_stop
                    take_profit = calculated_tp
                
                # Validate stops make sense
                if action == "long":
                    if stop_loss >= current_price:
                        logger.warning(f"Invalid stop for LONG ({stop_loss} >= {current_price}), using ATR-based")
                        stop_loss = calculated_stop
                    if take_profit <= current_price:
                        logger.warning(f"Invalid TP for LONG ({take_profit} <= {current_price}), using ATR-based")
                        take_profit = calculated_tp
                else:
                    if stop_loss <= current_price:
                        logger.warning(f"Invalid stop for SHORT ({stop_loss} <= {current_price}), using ATR-based")
                        stop_loss = calculated_stop
                    if take_profit >= current_price:
                        logger.warning(f"Invalid TP for SHORT ({take_profit} >= {current_price}), using ATR-based")
                        take_profit = calculated_tp
                
                # Calculate risk/reward
                if action == "long":
                    risk = current_price - stop_loss
                    reward = take_profit - current_price
                else:
                    risk = stop_loss - current_price
                    reward = current_price - take_profit
                
                rr_ratio = reward / risk if risk > 0 else 0
                
                logger.info(f"[{self.bot_name}] Opening {action.upper()} position:")
                logger.info(f"[{self.bot_name}]   Size: ${size_usd:.2f} USD = {quantity:.4f} {symbol.replace('USDT', '')}")
                logger.info(f"[{self.bot_name}]   Entry: ${current_price:.2f}")
                logger.info(f"[{self.bot_name}]   Stop Loss: ${stop_loss:.2f} ({atr_multiplier_stop:.1f}x ATR)")
                logger.info(f"[{self.bot_name}]   Take Profit: ${take_profit:.2f} ({atr_multiplier_tp:.1f}x ATR)")
                logger.info(f"[{self.bot_name}]   Risk/Reward: {rr_ratio:.2f}:1")
                logger.info(f"[{self.bot_name}]   Confidence: {confidence}% | Quality: {trade_quality:.0f}/100")
                
                # Open new position
                side = "buy" if action == "long" else "sell"
                order = await self.aster.place_order(
                    symbol=symbol,
                    side=side,
                    size=quantity,
                    order_type="market"
                )
                logger.success(f"[{self.bot_name}] {action.upper()} position opened: {order}")
                
                # Track when we opened this position (for anti-overtrading)
                self.last_trade_time = datetime.now()
                
                # Track trade for ML dataset
                try:
                    trade_id = self.trade_tracker.start_trade(
                        symbol=symbol,
                        decision=decision,
                        market_data=market_data,
                        entry_price=current_price,
                        position_size=size_usd
                    )
                    logger.info(f"📊 Tracking trade: {trade_id}")
                except Exception as e:
                    logger.warning(f"Could not start trade tracking: {e}")
                
                # Play sound notification
                try:
                    logger.info(f"Playing {action.upper()} sound alert...")
                    if action == "long":
                        # Higher pitch for BUY/LONG
                        winsound.Beep(1000, 500)
                    else:
                        # Lower pitch for SELL/SHORT
                        winsound.Beep(500, 500)
                    logger.info(f"Sound alert played successfully")
                except Exception as e:
                    logger.warning(f"Could not play sound: {e}")
                
                # Determine the closing side: SELL for longs, BUY for shorts
                close_side = "SELL" if action == "long" else "BUY"
                
                # Set stop loss and take profit
                try:
                    sl_order = await self.aster.set_stop_loss(
                        symbol, 
                        stop_loss, 
                        quantity,
                        side=close_side
                    )
                    logger.success(f"[{self.bot_name}] Stop loss set at ${stop_loss:.2f}")
                except Exception as e:
                    logger.warning(f"Could not set stop loss: {e}")
                    
                try:
                    tp_order = await self.aster.set_take_profit(
                        symbol, 
                        take_profit, 
                        quantity,
                        side=close_side
                    )
                    logger.success(f"[{self.bot_name}] Take profit set at ${take_profit:.2f}")
                except Exception as e:
                    logger.warning(f"Could not set take profit: {e}")
                
                self.trade_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": action,
                    "order": order,
                    "decision": decision
                })
                
            elif action == "close":
                # Close existing position
                position = await self.aster.get_position(symbol)
                if position:
                    # Get current price for tracking
                    ticker = await self.aster.get_ticker(symbol)
                    exit_price = float(ticker.get('lastPrice', 0))
                    
                    close_order = await self.aster.close_position(symbol)
                    logger.info(f"Closed position: {close_order}")
                    
                    # Track outcome for ML dataset
                    try:
                        self.trade_tracker.close_trade(
                            symbol=symbol,
                            exit_price=exit_price,
                            exit_reason="ai_close"
                        )
                        # Log stats
                        stats = self.trade_tracker.get_stats()
                        logger.info(f"📊 Trade Stats: Win Rate: {stats.get('win_rate', 0):.1f}% | "
                                   f"Total P&L: ${stats.get('total_pnl_usd', 0):.2f}")
                    except Exception as e:
                        logger.warning(f"Could not track trade outcome: {e}")
                    
                    # Cancel all open orders (TP/SL) for this symbol
                    try:
                        await self.aster.cancel_all_orders(symbol)
                        logger.success(f"Canceled all open orders for {symbol}")
                    except Exception as e:
                        logger.warning(f"Could not cancel orders: {e}")
                    
                    self.trade_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "action": "close",
                        "order": close_order,
                        "decision": decision
                    })
            
        except Exception as e:
            logger.error(f"Error executing decision: {e}")
    
    def _log_decision(
        self, 
        decision: Dict[str, Any], 
        market_data: Dict[str, Any],
        portfolio_state: Dict[str, Any]
    ):
        """Log trading decision for dashboard"""
        # Save to persistent storage
        self.decision_store.add_decision(decision, market_data, portfolio_state)
        
        # Also keep in memory for backward compatibility
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "market_snapshot": market_data,
            "portfolio_snapshot": portfolio_state
        }
        
        self.decision_log.append(log_entry)
        
        # Keep only last 1000 decisions in memory
        if len(self.decision_log) > 1000:
            self.decision_log = self.decision_log[-1000:]
        
        logger.info(f"Decision: {decision['action']} - {decision.get('reasoning', 'N/A')}")
    
    def get_decision_log(self) -> List[Dict[str, Any]]:
        """Get decision log for dashboard (from persistent storage)"""
        return self.decision_store.get_all_decisions()
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history for dashboard"""
        return self.trade_history
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate and return performance metrics"""
        try:
            portfolio = await self._analyze_portfolio()
            
            total_trades = len(self.trade_history)
            winning_trades = sum(1 for t in self.trade_history 
                               if t.get("pnl", 0) > 0)
            
            return {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
                "total_pnl": portfolio.get("balance", {}).get("total_pnl", 0),
                "current_balance": portfolio.get("balance", {}).get("total", 0),
                "open_positions": len(portfolio.get("positions", {})),
                "total_exposure": portfolio.get("total_exposure", 0)
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}

