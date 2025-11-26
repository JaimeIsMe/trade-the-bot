"""
FastAPI server for dashboard backend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Tuple
import json
import asyncio
from datetime import datetime, timedelta
from loguru import logger
import websockets
import aiohttp
from collections import defaultdict

from config.config import config
from api.aster_client import AsterClient

app = FastAPI(title="Aster Vibe Trader Dashboard API")

# Global shared Aster client (reuse session to prevent leaks)
_shared_client = None
_client_lock = asyncio.Lock()

async def get_aster_client():
    """Get or create a dashboard-specific Aster client with proper session reuse"""
    global _shared_client
    async with _client_lock:
        if _shared_client is None:
            _shared_client = AsterClient()
            timeout = aiohttp.ClientTimeout(total=30)
            _shared_client.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("✅ Created shared Aster client with reusable session")
        return _shared_client

# Rate limiting and caching to prevent API bans - BALANCED SETTINGS (proven stable for 1 hour!)
_klines_cache: Dict[str, Tuple[Any, datetime]] = {}  # {cache_key: (data, timestamp)}
_general_cache: Dict[str, Tuple[Any, datetime]] = {}  # Cache for all endpoints
_klines_cache_duration = 180  # Cache klines for 3 MINUTES (reduced from 5 for fresher data)
_general_cache_duration = 120  # Cache other endpoints for 2 MINUTES (reduced from 3)
_request_timestamps: Dict[str, list] = defaultdict(list)  # Track request times per endpoint
_rate_limit_window = 60  # 60 seconds
_max_requests_per_window = 6  # Slightly increased to 6 requests per minute (was 3) - still conservative!

def check_rate_limit(endpoint: str) -> bool:
    """Check if request is within rate limit"""
    now = datetime.now()
    cutoff = now - timedelta(seconds=_rate_limit_window)
    
    # Remove old timestamps
    _request_timestamps[endpoint] = [
        ts for ts in _request_timestamps[endpoint] 
        if ts > cutoff
    ]
    
    # Check if under limit
    if len(_request_timestamps[endpoint]) >= _max_requests_per_window:
        logger.warning(f"⚠️ Rate limit exceeded for {endpoint}")
        return False
    
    _request_timestamps[endpoint].append(now)
    return True

def get_cached_or_fetch(cache_key: str, fetch_func, cache_duration: int = _general_cache_duration):
    """
    Get data from cache or fetch if expired. Returns cached data even if stale on rate limit.
    This is an async wrapper.
    """
    async def wrapper():
        # Check cache first
        if cache_key in _general_cache:
            cached_data, cached_time = _general_cache[cache_key]
            age = (datetime.now() - cached_time).total_seconds()
            if age < cache_duration:
                logger.debug(f"✅ Serving {cache_key} from cache (age: {age:.1f}s)")
                return cached_data
        
        # Check rate limit before fetching
        if not check_rate_limit(cache_key):
            logger.warning(f"⚠️ Rate limited {cache_key} - serving stale cache")
            if cache_key in _general_cache:
                cached_data, _ = _general_cache[cache_key]
                return cached_data
            return None
        
        # Fetch fresh data
        try:
            data = await fetch_func()
            _general_cache[cache_key] = (data, datetime.now())
            logger.info(f"✅ Fetched and cached {cache_key}")
            return data
        except Exception as e:
            logger.error(f"Error fetching {cache_key}: {e}")
            # Return stale cache on error
            if cache_key in _general_cache:
                cached_data, _ = _general_cache[cache_key]
                logger.info(f"Returning stale cache for {cache_key} due to error")
                return cached_data
            return None
    
    return wrapper()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown - close shared client session"""
    global _shared_client
    if _shared_client and _shared_client.session:
        await _shared_client.session.close()
        logger.info("✅ Closed shared Aster client session")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global reference to trader instances (multiple bots)
trader_instances = {}  # Changed to dict: {bot_name: trader_instance}
trader_list_ref = None  # Reference to the shared list

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


def set_trader_instances(traders):
    """Set the global trader instances (for multi-bot support)"""
    global trader_instances, trader_list_ref
    trader_list_ref = traders  # Keep reference to the list
    trader_instances = {trader.bot_name: trader for trader in traders if trader}


def register_trader_instance(trader):
    """Register a single trader instance with the dashboard"""
    global trader_instances
    if trader and hasattr(trader, 'bot_name'):
        trader_instances[trader.bot_name] = trader
        logger.info(f"Registered trader: {trader.bot_name}")


def get_trader_instance(bot_name: str = None):
    """Get a specific trader instance, or first available if bot_name is None"""
    if not trader_instances:
        return None
    if bot_name:
        return trader_instances.get(bot_name)
    # Return first available trader if no name specified
    return next(iter(trader_instances.values())) if trader_instances else None


@app.get("/")
async def root():
    """Health check"""
    return {"status": "online", "service": "Aster Vibe Trader API"}


@app.get("/api/bots")
async def get_bots():
    """Get list of all active bots"""
    global trader_list_ref
    
    # Update trader_instances from the shared list
    if trader_list_ref:
        trader_instances.update({trader.bot_name: trader for trader in trader_list_ref if trader})
    
    bots = []
    for bot_name, trader in trader_instances.items():
        bots.append({
            "name": bot_name,
            "symbol": trader.symbol if hasattr(trader, 'symbol') else 'N/A',
            "status": "running" if trader.running else "stopped"
        })
    return {"bots": bots}


@app.get("/api/status")
async def get_status(bot_name: str = None):
    """Get trader status for a specific bot or first available"""
    trader = get_trader_instance(bot_name)
    if not trader:
        return {"status": "offline"}
    
    return {
        "status": "running" if trader.running else "stopped",
        "bot_name": trader.bot_name if hasattr(trader, 'bot_name') else 'N/A',
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/decisions")
async def get_decisions(limit: int = 50, symbol: str = None, bot_name: str = None):
    """Get recent trading decisions, optionally filtered by symbol or bot"""
    all_decisions = []
    
    # Get decisions from all bots or specific bot
    if bot_name:
        trader = get_trader_instance(bot_name)
        if trader:
            all_decisions = trader.get_decision_log()
    else:
        # Get decisions from all bots
        for trader in trader_instances.values():
            all_decisions.extend(trader.get_decision_log())
        
        # Sort by timestamp (most recent first)
        all_decisions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    # Filter by symbol if provided
    if symbol:
        filtered = [d for d in all_decisions if d.get('decision', {}).get('symbol') == symbol]
        return filtered[:limit]
    
    return all_decisions[:limit]


# Track last known decision counts per bot to detect new decisions
last_decision_counts = {}

@app.websocket("/ws/decisions")
async def decisions_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI decisions
    Polls bot decision logs and pushes new decisions to frontend
    """
    global last_decision_counts
    
    try:
        await websocket.accept()
        logger.info("Frontend WebSocket connected to /ws/decisions")
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {e}")
        return
    
    try:
        while True:
            try:
                # Check all bots for new decisions
                all_decisions = []
                for bot_name, trader in trader_instances.items():
                    try:
                        decisions = trader.get_decision_log()
                        current_count = len(decisions)
                        
                        # Check if there are new decisions
                        last_count = last_decision_counts.get(bot_name, 0)
                        if current_count > last_count:
                            # New decisions detected
                            new_decisions = decisions[last_count:current_count]
                            logger.info(f"📊 New decisions detected for {bot_name}: {len(new_decisions)}")
                            
                            # Add bot symbol to each decision
                            for decision in new_decisions:
                                decision_with_meta = {
                                    **decision,
                                    'symbol': trader.symbol,
                                    'asset': trader.symbol.replace('USDT', '')
                                }
                                all_decisions.append(decision_with_meta)
                            
                            last_decision_counts[bot_name] = current_count
                        elif current_count == 0 and last_count > 0:
                            # Decision log was cleared - reset counter
                            last_decision_counts[bot_name] = 0
                        
                    except Exception as e:
                        logger.error(f"Error reading decisions from {bot_name}: {e}")
                
                # Send new decisions to frontend if any
                if all_decisions:
                    # Sort by timestamp (newest first)
                    all_decisions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                    
                    await websocket.send_json({
                        "type": "new_decisions",
                        "data": all_decisions
                    })
                
                # Check every 10 seconds for new decisions
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in decisions WebSocket loop: {e}")
                await asyncio.sleep(10)
                
    except WebSocketDisconnect:
        logger.info("Frontend WebSocket disconnected from /ws/decisions")
    except Exception as e:
        logger.error(f"Unexpected error in decisions WebSocket: {e}")
    finally:
        logger.info("Decisions WebSocket closed")


@app.get("/api/trades")
async def get_trades(limit: int = 100, symbol: str = None):
    """Get trade history from Aster transaction history with realized P&L (CACHED 3 MIN)"""
    cache_key = f"trades_{symbol or 'all'}_{limit}"
    
    async def fetch_trades():
        client = await get_aster_client()
        
        # Fetch income history (transaction history) to get realized P&L entries
        all_income = []
        try:
            # Fetch income records (max limit is 1000 per Aster API)
            income_data = await client.get_income_history(symbol=symbol, limit=1000)
            if isinstance(income_data, list):
                all_income = income_data
        except Exception as e:
            logger.warning(f"Could not fetch income history: {e}")
        
        # Process income records - we want REALIZED_PNL entries (these are completed trades)
        trades = []
        for income in all_income:
            if income.get('incomeType') == 'REALIZED_PNL':
                sym = income.get('symbol', '')
                
                # If symbol filter is set and doesn't match, skip
                if symbol and sym != symbol:
                    continue
                
                # Extract P&L and timestamp
                pnl = float(income.get('income', 0))
                timestamp = income.get('time', 0)
                trade_id = income.get('tradeId', '')
                
                # Determine if this was a winning or losing trade
                is_win = pnl > 0
                
                trades.append({
                    "timestamp": timestamp,
                    "time": timestamp,
                    "symbol": sym,
                    "pnl": pnl,
                    "realizedProfit": pnl,
                    "action": "close",  # These are all position closes
                    "side": "CLOSE",
                    "price": "0",  # Not available in income data
                    "qty": "0",  # Not available in income data
                    "isWin": is_win,
                    "order": {
                        "orderId": trade_id,
                        "symbol": sym,
                        "status": "FILLED",
                        "side": "CLOSE",
                        "type": "REALIZED_PNL",
                        "price": "0",
                        "avgPrice": "0",
                        "size": "0",
                        "executedQty": "0"
                    }
                })
        
        # Sort by timestamp (most recent first)
        trades.sort(key=lambda x: x['timestamp'], reverse=True)
        return trades[:limit]
    
    try:
        result = await get_cached_or_fetch(cache_key, fetch_trades, cache_duration=180)
        return result if result is not None else []
    except Exception as e:
        logger.error(f"Error in get_trades: {e}")
        return []


@app.get("/api/portfolio/summary")
async def get_portfolio_summary():
    """Get overall portfolio summary across all strategies (CACHED 3 MIN)"""
    cache_key = "portfolio_summary"
    
    async def fetch_portfolio():
        client = await get_aster_client()
        account = await client.get_account()
        
        # Get overall balance metrics
        # Calculate total equity across ALL assets (USDT + USDC + others)
        # This matches what Aster DEX website shows as "Account Equity"
        assets = account.get('assets', [])
        total_balance = 0.0
        
        for asset in assets:
            margin_bal = float(asset.get('marginBalance', 0))
            if margin_bal > 0:
                total_balance += margin_bal
        
        # If no assets found, fallback to totalMarginBalance
        if total_balance == 0:
            total_balance = float(account.get('totalMarginBalance', 0))
        
        available_balance = float(account.get('availableBalance', 0))
        total_unrealized_pnl = float(account.get('totalUnrealizedProfit', 0))
        total_margin_balance = float(account.get('totalMarginBalance', 0))
        total_maint_margin = float(account.get('totalMaintMargin', 0))
        
        # Calculate margin ratio
        margin_ratio = 0
        if total_maint_margin > 0:
            margin_ratio = (total_margin_balance / total_maint_margin) * 100
        
        # Get positions and calculate exposure per strategy
        # Use margin used instead of notional (which includes leverage multiplier)
        positions = account.get('positions', [])
        aster_exposure = sum(abs(float(p.get('initialMargin', 0))) for p in positions 
                           if p.get('symbol') == 'ASTERUSDT' and float(p.get('positionAmt', 0)) != 0)
        btc_exposure = sum(abs(float(p.get('initialMargin', 0))) for p in positions 
                         if p.get('symbol') == 'BTCUSDT' and float(p.get('positionAmt', 0)) != 0)
        eth_exposure = sum(abs(float(p.get('initialMargin', 0))) for p in positions 
                         if p.get('symbol') == 'ETHUSDT' and float(p.get('positionAmt', 0)) != 0)
        sol_exposure = sum(abs(float(p.get('initialMargin', 0))) for p in positions 
                         if p.get('symbol') == 'SOLUSDT' and float(p.get('positionAmt', 0)) != 0)
        bnb_exposure = sum(abs(float(p.get('initialMargin', 0))) for p in positions 
                         if p.get('symbol') == 'BNBUSDT' and float(p.get('positionAmt', 0)) != 0)
        total_exposure = aster_exposure + btc_exposure + eth_exposure + sol_exposure + bnb_exposure
        
        return {
            "total_balance": total_balance,
            "available_balance": available_balance,
            "total_unrealized_pnl": total_unrealized_pnl,
            "margin_balance": total_margin_balance,
            "margin_ratio": margin_ratio,
            "total_exposure": total_exposure,
            "aster_exposure": aster_exposure,
            "btc_exposure": btc_exposure,
            "eth_exposure": eth_exposure,
            "sol_exposure": sol_exposure,
            "bnb_exposure": bnb_exposure,
            "strategies_active": 5
        }
    
    default_response = {
            "total_balance": 0,
            "available_balance": 0,
            "total_unrealized_pnl": 0,
            "total_exposure": 0,
            "aster_exposure": 0,
            "btc_exposure": 0,
            "eth_exposure": 0,
            "sol_exposure": 0,
            "bnb_exposure": 0,
            "strategies_active": 0
        }
    
    try:
        result = await get_cached_or_fetch(cache_key, fetch_portfolio, cache_duration=180)
        return result if result is not None else default_response
    except Exception as e:
        logger.error(f"Error in get_portfolio_summary: {e}")
        return default_response


@app.get("/api/performance")
async def get_performance(symbol: str = None):
    """Get performance metrics from Aster history, optionally filtered by symbol (CACHED 3 MIN)"""
    cache_key = f"performance_{symbol or 'all'}"
    
    async def fetch_performance():
        client = await get_aster_client()
        account = await client.get_account()
        
        # Determine which symbols to fetch
        symbols_to_fetch = [symbol] if symbol else ["ASTERUSDT", "BTCUSDT"]
        
        all_orders = []
        all_income = []
        
        for sym in symbols_to_fetch:
            try:
                orders = await client.get_all_orders(sym, limit=1000)
                income = await client.get_income_history(symbol=sym, limit=1000)
                all_orders.extend(orders)
                all_income.extend(income)
            except Exception as e:
                logger.warning(f"Could not fetch performance data for {sym}: {e}")
        
        # Count filled orders
        filled_orders = [o for o in all_orders if o.get('status') == 'FILLED']
        total_trades = len(filled_orders)
        
        # Calculate total realized PNL from income history
        total_realized_pnl = sum(float(i.get('income', 0)) for i in all_income if i.get('incomeType') == 'REALIZED_PNL')
        
        # Get unrealized PNL from account (filter by symbol if specified)
        positions = account.get('positions', [])
        if symbol:
            unrealized_pnl = sum(float(p.get('unrealizedProfit', 0)) for p in positions 
                                if p.get('symbol') == symbol)
            open_positions = sum(1 for p in positions 
                               if p.get('symbol') == symbol and float(p.get('positionAmt', 0)) != 0)
            total_exposure = sum(abs(float(p.get('notional', 0))) for p in positions 
                               if p.get('symbol') == symbol and float(p.get('positionAmt', 0)) != 0)
        else:
            unrealized_pnl = float(account.get('totalUnrealizedProfit', 0))
            open_positions = sum(1 for p in positions if float(p.get('positionAmt', 0)) != 0)
            total_exposure = sum(abs(float(p.get('notional', 0))) for p in positions 
                               if float(p.get('positionAmt', 0)) != 0)
        
        total_pnl = total_realized_pnl + unrealized_pnl
        
        # Calculate win rate from realized PNL records
        profitable_trades = sum(1 for i in all_income if i.get('incomeType') == 'REALIZED_PNL' and float(i.get('income', 0)) > 0)
        total_closed_trades = sum(1 for i in all_income if i.get('incomeType') == 'REALIZED_PNL')
        win_rate = (profitable_trades / total_closed_trades) if total_closed_trades > 0 else 0
        
        # Calculate biggest win and loss
        realized_pnls = [float(i.get('income', 0)) for i in all_income if i.get('incomeType') == 'REALIZED_PNL']
        biggest_win = max(realized_pnls) if realized_pnls else 0
        biggest_loss = min(realized_pnls) if realized_pnls else 0
        
        # Calculate total fees
        total_fees = sum(float(i.get('income', 0)) for i in all_income if i.get('incomeType') in ['COMMISSION', 'TRANSFER'])
        
        # Calculate Sharpe ratio (simplified)
        if len(realized_pnls) > 1:
            avg_return = sum(realized_pnls) / len(realized_pnls)
            std_dev = (sum((x - avg_return) ** 2 for x in realized_pnls) / len(realized_pnls)) ** 0.5
            sharpe_ratio = (avg_return / std_dev) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            "symbol": symbol or "ALL",
            "total_trades": total_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "realized_pnl": total_realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "winning_trades": profitable_trades,
            "open_positions": open_positions,
            "total_exposure": total_exposure,
            "biggest_win": biggest_win,
            "biggest_loss": biggest_loss,
            "total_fees": abs(total_fees),
            "sharpe_ratio": sharpe_ratio
        }
    
    default_response = {
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "biggest_win": 0,
            "biggest_loss": 0,
            "total_fees": 0,
            "sharpe_ratio": 0
        }
    
    try:
        result = await get_cached_or_fetch(cache_key, fetch_performance, cache_duration=180)
        return result if result is not None else default_response
    except Exception as e:
        logger.error(f"Error in get_performance: {e}")
        return default_response


@app.get("/api/positions")
async def get_positions():
    """Get current open positions (CACHED 3 MIN)"""
    cache_key = "positions"
    
    async def fetch_positions():
        # Use dedicated client for dashboard
        client = await get_aster_client()
        account = await client.get_account()
        positions = account.get('positions', [])
        
        # Filter only open positions
        open_positions = []
        for pos in positions:
            pos_amt = float(pos.get('positionAmt', 0))
            if pos_amt != 0:
                open_positions.append({
                    "symbol": pos.get('symbol'),
                    "side": "long" if pos_amt > 0 else "short",
                    "size": abs(pos_amt),
                    "entry_price": float(pos.get('entryPrice', 0)),
                    "unrealized_pnl": float(pos.get('unrealizedProfit', 0)),
                    "notional": abs(float(pos.get('notional', 0))),
                    "leverage": int(pos.get('leverage', 1))
                })
        
        return open_positions
    
    try:
        result = await get_cached_or_fetch(cache_key, fetch_positions, cache_duration=60)  # 1 min cache for positions (more dynamic)
        return result if result is not None else []
    except Exception as e:
        logger.error(f"Error in get_positions: {e}")
        return []


@app.get("/api/balance")
async def get_balance():
    """Get account balance and equity (RATE LIMITED)"""
    # Check rate limit
    if not check_rate_limit("balance"):
        logger.warning(f"⚠️ Rate limit exceeded for balance endpoint")
        return {"available": 0, "total": 0, "pnl": 0, "margin_ratio": 0}
    
    try:
        # Use dedicated client for dashboard
        client = await get_aster_client()
        account = await client.get_account()
        
        # Extract key metrics
        total_balance = float(account.get('totalWalletBalance', 0))
        available_balance = float(account.get('availableBalance', 0))
        unrealized_pnl = float(account.get('totalUnrealizedProfit', 0))
        total_margin_balance = float(account.get('totalMarginBalance', 0))
        total_maint_margin = float(account.get('totalMaintMargin', 0))
        
        # Calculate margin ratio
        margin_ratio = 0
        if total_maint_margin > 0:
            margin_ratio = (total_margin_balance / total_maint_margin) * 100
        
        return {
            "total": total_balance,
            "available": available_balance,
            "pnl": unrealized_pnl,
            "margin_balance": total_margin_balance,
            "margin_ratio": margin_ratio
        }
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return {"available": 0, "total": 0, "pnl": 0, "margin_ratio": 0}


@app.get("/api/klines")
async def get_klines(symbol: str = "ASTERUSDT", interval: str = "5m", limit: int = 288):
    """
    Get candlestick data for charting (CACHED + RATE LIMITED to prevent API bans)
    
    Args:
        symbol: Trading symbol (default: ASTERUSDT)
        interval: Candle interval (1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d) (default: 5m)
        limit: Number of candles to fetch (default: 288 = 24 hours of 5m candles)
    """
    cache_key = f"{symbol}_{interval}_{limit}"
    
    # Check cache first
    if cache_key in _klines_cache:
        cached_data, cached_time = _klines_cache[cache_key]
        age = (datetime.now() - cached_time).total_seconds()
        if age < _klines_cache_duration:
            logger.debug(f"✅ Serving klines from cache (age: {age:.1f}s)")
            return cached_data
    
    # Check rate limit
    if not check_rate_limit(f"klines_{symbol}"):
        logger.warning(f"⚠️ Rate limit exceeded for klines {symbol} - serving stale cache")
        # Serve stale cache if available (better than nothing)
        if cache_key in _klines_cache:
            cached_data, _ = _klines_cache[cache_key]
            return cached_data
        return []
    
    try:
        client = await get_aster_client()
        klines = await client.get_klines(symbol, interval=interval, limit=limit)
        
        # Format for candlestick chart
        formatted_candles = []
        for k in klines:
            formatted_candles.append({
                "time": k[0],  # Timestamp
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        
        # Update cache
        _klines_cache[cache_key] = (formatted_candles, datetime.now())
        logger.info(f"✅ Fetched and cached {len(formatted_candles)} klines for {symbol}")
        
        return formatted_candles
    except Exception as e:
        logger.error(f"Error fetching klines: {e}")
        # Return stale cache if available
        if cache_key in _klines_cache:
            cached_data, _ = _klines_cache[cache_key]
            logger.info(f"Returning stale cache due to error")
            return cached_data
        return []


@app.get("/api/ticker/{symbol}")
async def get_ticker(symbol: str):
    """
    Get 24hr ticker data for a specific symbol
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT, ASTERUSDT)
    """
    try:
        client = await get_aster_client()
        ticker = await client.get_ticker(symbol)
        return ticker
    except Exception as e:
        logger.error(f"Error fetching ticker for {symbol}: {e}")
        return {"error": str(e)}


@app.websocket("/ws/tickers")
async def ticker_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time ticker prices from Aster
    Connects to Aster's WebSocket and proxies ticker data to frontend
    """
    try:
        await websocket.accept()
        logger.info("Frontend WebSocket connected to /ws/tickers")
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {e}")
        return
    
    aster_ws = None
    
    try:
        # Connect to Aster's WebSocket stream for all market mini tickers
        # Stream: !miniTicker@arr - updates every 1 second with all symbols
        aster_ws_url = "wss://fstream.asterdex.com/stream?streams=!miniTicker@arr"
        
        logger.info("Connecting to Aster WebSocket for ticker data...")
        try:
            # ping_interval=300 (5 min), ping_timeout=60 (1 min) - Aster sends ping every 5 min
            # Use context manager to ensure proper cleanup
            async with websockets.connect(aster_ws_url, ping_interval=300, ping_timeout=60) as aster_ws:
                logger.info("✅ Connected to Aster WebSocket")
                
                # When using /stream?streams=... URL format, streams are already active
                # No need to send SUBSCRIBE message - it's already subscribed via URL
                logger.info("Listening for ticker updates...")
                
                # Listen for messages from Aster and forward to frontend
                async for message in aster_ws:
                    try:
                        data = json.loads(message)
                    
                        # Handle subscription confirmation
                        if data.get('result') is not None:
                            logger.info("Subscribed to ticker stream")
                            continue
                        
                        # Forward ticker updates to frontend
                        # Combined stream format: {"stream": "<streamName>", "data": <rawPayload>}
                        if 'stream' in data and 'data' in data:
                            # Extract ticker data array
                            tickers = data.get('data', [])
                            
                            # Filter to only our 5 symbols
                            our_symbols = ['asterusdt', 'btcusdt', 'ethusdt', 'solusdt', 'bnbusdt']
                            filtered_tickers = [
                                t for t in tickers 
                                if isinstance(t, dict) and t.get('s', '').lower() in our_symbols
                            ]
                            
                            # Format for frontend
                            formatted_tickers = []
                            for ticker in filtered_tickers:
                                symbol = ticker.get('s', '').upper()
                                last_price = float(ticker.get('c', 0))
                                price_change = float(ticker.get('p', 0))
                                price_change_percent = float(ticker.get('P', 0))
                                
                                formatted_tickers.append({
                                    "symbol": symbol,
                                    "lastPrice": str(last_price),
                                    "priceChange": str(price_change),
                                    "priceChangePercent": str(price_change_percent),
                                    "highPrice": str(ticker.get('h', 0)),
                                    "lowPrice": str(ticker.get('l', 0)),
                                    "openPrice": str(ticker.get('o', 0)),
                                    "volume": str(ticker.get('v', 0))
                                })
                            
                            # Send to frontend
                            if formatted_tickers:
                                try:
                                    await websocket.send_json({
                                        "type": "tickers",
                                        "data": formatted_tickers
                                    })
                                except Exception as e:
                                    logger.error(f"Error sending to frontend: {e}")
                                    break  # Frontend disconnected
                        else:
                            # Log unexpected message format for debugging
                            logger.debug(f"Received unexpected message format: {list(data.keys())}")
                    
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                        continue
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Aster WebSocket connection closed")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Aster WebSocket: {e}", exc_info=True)
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Failed to connect to Aster: {str(e)}"
                })
            except:
                pass
            return
    
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}", exc_info=True)
    finally:
        try:
            await websocket.close()
            logger.info("Frontend WebSocket closed")
        except:
            pass


@app.websocket("/ws/account")
async def account_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time account data from Aster
    Connects to Aster's user data stream and proxies account updates to frontend
    """
    try:
        await websocket.accept()
        logger.info("Frontend WebSocket connected to /ws/account")
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {e}")
        return
    
    aster_ws = None
    listen_key = None
    keepalive_task = None
    client = None
    
    try:
        # Get Aster client and obtain listenKey
        client = await get_aster_client()
        listen_key = await client.start_user_data_stream()
        
        # Connect to Aster's user data stream
        aster_ws_url = f"wss://fstream.asterdex.com/ws/{listen_key}"
        
        logger.info("Connecting to Aster user data stream...")
        try:
            async with websockets.connect(aster_ws_url, ping_interval=300, ping_timeout=60) as aster_ws:
                logger.info("✅ Connected to Aster user data stream")
                
                # Start keepalive task (extend listenKey every 55 minutes)
                async def keepalive_loop():
                    try:
                        while True:
                            await asyncio.sleep(55 * 60)  # 55 minutes
                            try:
                                await client.keepalive_user_data_stream()
                                logger.info("✅ Extended listenKey validity")
                            except Exception as e:
                                logger.error(f"Error extending listenKey: {e}")
                    except asyncio.CancelledError:
                        logger.info("Keepalive task cancelled")
                        raise
                
                keepalive_task = asyncio.create_task(keepalive_loop())
                
                # Listen for messages from Aster and forward to frontend
                async for message in aster_ws:
                    try:
                        data = json.loads(message)
                        event_type = data.get('e')
                        
                        # Handle listenKey expiration
                        if event_type == 'listenKeyExpired':
                            logger.warning("⚠️ listenKey expired, reconnecting...")
                            # Get new listenKey and reconnect
                            try:
                                listen_key = await client.start_user_data_stream()
                                # Close current connection and reconnect
                                await aster_ws.close()
                                break  # Will reconnect in outer loop
                            except Exception as e:
                                logger.error(f"Failed to get new listenKey: {e}")
                                await websocket.send_json({
                                    "type": "error",
                                    "message": f"listenKey expired and failed to renew: {str(e)}"
                                })
                                return
                        
                        # Parse ACCOUNT_UPDATE events
                        elif event_type == 'ACCOUNT_UPDATE':
                            await handle_account_update(data, websocket)
                        
                        # Parse ORDER_TRADE_UPDATE events
                        elif event_type == 'ORDER_TRADE_UPDATE':
                            await handle_order_trade_update(data, websocket)
                        
                        # Handle other events (MARGIN_CALL, etc.)
                        elif event_type:
                            logger.debug(f"Received event: {event_type}")
                    
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                        continue
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Aster user data stream connection closed")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Aster user data stream: {e}", exc_info=True)
            try:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Failed to connect to Aster: {str(e)}"
                })
            except:
                pass
            return
    
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}", exc_info=True)
    finally:
        # Cleanup
        if keepalive_task:
            keepalive_task.cancel()
        if listen_key:
            try:
                await client.close_user_data_stream()
            except:
                pass
        try:
            await websocket.close()
            logger.info("Frontend WebSocket closed")
        except:
            pass


async def handle_account_update(data: dict, websocket: WebSocket):
    """
    Parse ACCOUNT_UPDATE event and send formatted data to frontend
    
    ACCOUNT_UPDATE contains:
    - Balances (B): wallet balance, cross wallet balance, balance changes
    - Positions (P): position amount, entry price, unrealized P&L, etc.
    """
    try:
        update_data = data.get('a', {})
        balances = update_data.get('B', [])
        positions = update_data.get('P', [])
        
        # Format balances
        formatted_balances = {}
        total_balance = 0.0
        for balance in balances:
            asset = balance.get('a', '')
            wallet_balance = float(balance.get('wb', 0))
            cross_wallet = float(balance.get('cw', 0))
            
            if wallet_balance > 0 or cross_wallet > 0:
                formatted_balances[asset] = {
                    "walletBalance": wallet_balance,
                    "crossWallet": cross_wallet,
                    "balanceChange": float(balance.get('bc', 0))
                }
                total_balance += wallet_balance
        
        # Format positions
        formatted_positions = []
        total_unrealized_pnl = 0.0
        
        for pos in positions:
            symbol = pos.get('s', '')
            position_amt = float(pos.get('pa', 0))
            
            if position_amt != 0:  # Only include open positions
                entry_price = float(pos.get('ep', 0))
                unrealized_pnl = float(pos.get('up', 0))
                realized_pnl = float(pos.get('cr', 0))
                margin_type = pos.get('mt', 'crossed')
                position_side = pos.get('ps', 'BOTH')
                
                formatted_positions.append({
                    "symbol": symbol,
                    "positionAmt": position_amt,
                    "entryPrice": entry_price,
                    "unrealizedPnl": unrealized_pnl,
                    "realizedPnl": realized_pnl,
                    "marginType": margin_type,
                    "positionSide": position_side
                })
                
                total_unrealized_pnl += unrealized_pnl
        
        # Send to frontend
        await websocket.send_json({
            "type": "account_update",
            "timestamp": data.get('E', 0),
            "data": {
                "balances": formatted_balances,
                "totalBalance": total_balance,
                "positions": formatted_positions,
                "totalUnrealizedPnl": total_unrealized_pnl
            }
        })
    
    except Exception as e:
        logger.error(f"Error handling ACCOUNT_UPDATE: {e}", exc_info=True)


async def handle_order_trade_update(data: dict, websocket: WebSocket):
    """
    Parse ORDER_TRADE_UPDATE event and send formatted data to frontend
    
    ORDER_TRADE_UPDATE contains:
    - Order details: symbol, side, type, status
    - Execution details: filled quantity, average price, realized profit
    """
    try:
        order_data = data.get('o', {})
        
        # Extract key fields
        symbol = order_data.get('s', '')
        order_status = order_data.get('X', '')
        execution_type = order_data.get('x', '')
        side = order_data.get('S', '')
        order_type = order_data.get('o', '')
        
        # Only send updates for filled orders (trade executions)
        if execution_type == 'TRADE' and order_status == 'FILLED':
            filled_qty = float(order_data.get('z', 0))  # Accumulated filled quantity
            avg_price = float(order_data.get('ap', 0))  # Average price
            realized_profit = float(order_data.get('rp', 0))  # Realized profit
            
            await websocket.send_json({
                "type": "trade_execution",
                "timestamp": data.get('E', 0),
                "data": {
                    "symbol": symbol,
                    "side": side,
                    "orderType": order_type,
                    "filledQuantity": filled_qty,
                    "averagePrice": avg_price,
                    "realizedProfit": realized_profit,
                    "orderId": order_data.get('i', 0)
                }
            })
    
    except Exception as e:
        logger.error(f"Error handling ORDER_TRADE_UPDATE: {e}", exc_info=True)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send updates every second
            trader_instance = get_trader_instance()
            if trader_instance:
                data = {
                    "type": "update",
                    "timestamp": datetime.now().isoformat(),
                    "status": "running" if trader_instance.running else "stopped",
                    "latest_decision": trader_instance.get_decision_log()[-1] if trader_instance.get_decision_log() else None
                }
                await websocket.send_json(data)
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.dashboard.api_port)

