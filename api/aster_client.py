"""
Aster API Client - Wallet-based Authentication
Based on official Aster API V3 specification
"""
import aiohttp
import json
import math
import time
from typing import Dict, Any, Optional, List
from loguru import logger

from eth_abi import encode
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

from config.config import config


class AsterClient:
    """
    Client for interacting with Aster decentralized perpetuals exchange API
    Uses Ethereum wallet-based authentication
    """
    
    def __init__(self):
        # Ensure addresses are in proper checksum format for eth-abi
        # Strip any trailing whitespace and validate length
        user_addr = config.aster.user_address.strip()
        signer_addr = config.aster.signer_address.strip()
        
        # Validate address length (should be 42 chars: 0x + 40 hex digits)
        if len(user_addr) != 42:
            raise ValueError(f"Invalid user address length: {len(user_addr)} (expected 42). Address: '{user_addr}'")
        if len(signer_addr) != 42:
            raise ValueError(f"Invalid signer address length: {len(signer_addr)} (expected 42). Address: '{signer_addr}'")
        
        self.user_address = Web3.to_checksum_address(user_addr)
        self.signer_address = Web3.to_checksum_address(signer_addr)
        self.private_key = config.aster.private_key.strip()
        self.base_url = config.aster.api_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("Aster API Client initialized (wallet-based auth)")
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _sign_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign request using Ethereum wallet signature
        
        Args:
            params: Request parameters
            
        Returns:
            Parameters with signature added
        """
        # Generate nonce (microsecond timestamp)
        nonce = math.trunc(time.time() * 1000000)
        
        # Add required fields
        params = {key: value for key, value in params.items() if value is not None}
        params['recvWindow'] = 50000
        params['timestamp'] = int(round(time.time() * 1000))
        
        # Create message to sign
        msg_hash = self._create_message_hash(params, nonce)
        
        # Sign the message
        signable_msg = encode_defunct(hexstr=msg_hash)
        signed_message = Account.sign_message(
            signable_message=signable_msg, 
            private_key=self.private_key
        )
        
        # Add signature fields
        params['nonce'] = nonce
        params['user'] = self.user_address
        params['signer'] = self.signer_address
        params['signature'] = '0x' + signed_message.signature.hex()
        
        return params
    
    def _create_message_hash(self, params: Dict[str, Any], nonce: int) -> str:
        """
        Create message hash for signing
        
        Args:
            params: Request parameters
            nonce: Unique nonce value
            
        Returns:
            Keccak hash of encoded message
        """
        # Trim and convert all values to strings
        trimmed_params = self._trim_dict(params.copy())
        
        # Create JSON string (sorted keys, no spaces)
        json_str = json.dumps(trimmed_params, sort_keys=True).replace(' ', '').replace("'", '"')
        
        # Encode message
        encoded = encode(
            ['string', 'address', 'address', 'uint256'],
            [json_str, self.user_address, self.signer_address, nonce]
        )
        
        # Return keccak hash
        return Web3.keccak(encoded).hex()
    
    def _trim_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert all values in dict to strings (required by Aster API)
        
        Args:
            data: Dictionary to process
            
        Returns:
            Dictionary with all values as strings
        """
        for key in data:
            value = data[key]
            if isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, dict):
                        new_value.append(json.dumps(self._trim_dict(item)))
                    else:
                        new_value.append(str(item))
                data[key] = json.dumps(new_value)
                continue
            if isinstance(value, dict):
                data[key] = json.dumps(self._trim_dict(value))
                continue
            data[key] = str(value)
        
        return data
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        # Sign the request
        signed_params = self._sign_request(params)
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'AsterVibeTrader/1.0'
        }
        
        try:
            if method == "GET":
                async with self.session.get(url, params=signed_params, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                    response.raise_for_status()
                    return await response.json()
            elif method == "POST":
                # POST requests - always send params as form data in body (even if empty)
                async with self.session.post(url, data=signed_params, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                    response.raise_for_status()
                    return await response.json()
            elif method == "PUT":
                # PUT requests - send params as form data in body
                async with self.session.put(url, data=signed_params, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                    response.raise_for_status()
                    return await response.json()
            elif method == "DELETE":
                # DELETE requests - send params as form data in body
                async with self.session.delete(url, data=signed_params, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"API Error {response.status}: {error_text}")
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    # ========== Market Data Methods ==========
    
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get list of available markets"""
        return await self._request("GET", "/fapi/v3/exchangeInfo", {})
    
    async def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 20) -> Dict[str, Any]:
        """Get orderbook for a symbol"""
        return await self._request("GET", "/fapi/v3/depth", {"symbol": symbol, "limit": limit})
    
    async def get_recent_trades(self, symbol: str = "BTCUSDT", limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades for a symbol"""
        return await self._request("GET", "/fapi/v3/trades", {"symbol": symbol, "limit": limit})
    
    async def get_funding_rates(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get current funding rate"""
        return await self._request("GET", "/fapi/v3/premiumIndex", {"symbol": symbol})
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get 24hr ticker"""
        return await self._request("GET", "/fapi/v3/ticker/24hr", {"symbol": symbol})
    
    async def get_klines(
        self, 
        symbol: str = "BTCUSDT", 
        interval: str = "1h", 
        limit: int = 24
    ) -> List[List]:
        """
        Get historical candlestick data
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            interval: Candlestick interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles to fetch (default 24 for 24 hours of 1h data)
        
        Returns:
            List of candlesticks, each containing:
            [timestamp, open, high, low, close, volume, ...]
        """
        return await self._request("GET", "/fapi/v1/klines", {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })
    
    # ========== Account Methods ==========
    
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        return await self._request("GET", "/fapi/v3/balance", {})
    
    async def get_account(self) -> Dict[str, Any]:
        """Get account information including equity, margin, PNL"""
        return await self._request("GET", "/fapi/v3/account", {})
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        account = await self.get_account()
        return account.get("positions", [])
    
    async def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get specific position"""
        positions = await self.get_positions()
        for pos in positions:
            if pos.get("symbol") == symbol and float(pos.get("positionAmt", 0)) != 0:
                return pos
        return None
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/fapi/v3/openOrders", params)
    
    async def get_all_orders(
        self, 
        symbol: str = "BTCUSDT", 
        limit: int = 500,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all orders (historical)
        
        Args:
            symbol: Trading symbol
            limit: Number of orders to fetch (max 1000)
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        
        Returns:
            List of all orders
        """
        params = {"symbol": symbol, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._request("GET", "/fapi/v3/allOrders", params)
    
    async def get_user_trades(
        self,
        symbol: str = "BTCUSDT",
        limit: int = 500,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's trade history
        
        Args:
            symbol: Trading symbol
            limit: Number of trades to fetch
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        
        Returns:
            List of user trades
        """
        params = {"symbol": symbol, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._request("GET", "/fapi/v3/userTrades", params)
    
    async def get_income_history(
        self,
        symbol: Optional[str] = None,
        income_type: Optional[str] = None,
        limit: int = 1000,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get income history (realized PNL, funding fees, etc.)
        
        Args:
            symbol: Trading symbol (optional)
            income_type: Type of income (REALIZED_PNL, FUNDING_FEE, etc.)
            limit: Number of records to fetch
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
        
        Returns:
            List of income records
        """
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol
        if income_type:
            params["incomeType"] = income_type
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._request("GET", "/fapi/v3/income", params)
    
    # ========== Trading Methods ==========
    
    def _format_quantity(self, symbol: str, quantity: float) -> str:
        """
        Format quantity to match symbol's precision requirements
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "ASTERUSDT")
            quantity: Raw quantity value
            
        Returns:
            Formatted quantity string with correct precision
        """
        symbol_upper = symbol.upper()
        # Precision map derived from Aster lot size filters
        precision_map = {
            "ASTERUSDT": 0,   # whole numbers only
            "BTCUSDT": 3,
            "ETHUSDT": 3,
            "SOLUSDT": 2,     # step size 0.01 on Aster
            "BNBUSDT": 2      # step size 0.01 on Aster (API error if 3 decimals)
        }
        precision = precision_map.get(symbol_upper, 3)
        
        # Round to specified precision
        quantity_rounded = round(quantity, precision)
        
        # Handle floating point precision issues by converting to string with exact precision
        if precision == 0:
            # For whole numbers, ensure we return an integer string
            return str(int(quantity_rounded))
        else:
            # For decimals, format with exact precision and remove trailing zeros
            # Use format to ensure exact precision, then strip trailing zeros
            formatted = f"{quantity_rounded:.{precision}f}"
            return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
    
    def _format_price(self, symbol: str, price: float) -> str:
        """
        Format price to match symbol's precision requirements
        
        Args:
            symbol: Trading symbol
            price: Raw price value
            
        Returns:
            Formatted price string with correct precision
        """
        # Round based on price level (more precise for lower prices)
        if price >= 1000:
            precision = 1  # BTC (~$100k)
        elif price >= 100:
            precision = 2  # SOL, BNB (~$200-$1k)
        elif price >= 10:
            precision = 3  # ETH (~$4k)
        else:
            precision = 4  # ASTER and low-priced assets (~$1)
        
        price_rounded = round(price, precision)
        
        # Handle floating point precision issues by converting to string with exact precision
        if precision == 0 or price_rounded == int(price_rounded):
            return str(int(price_rounded))
        else:
            # Format with exact precision and remove trailing zeros
            formatted = f"{price_rounded:.{precision}f}"
            return formatted.rstrip('0').rstrip('.') if '.' in formatted else formatted
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        position_side: str = "BOTH",
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place an order
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            side: "BUY" or "SELL"
            size: Order size (quantity)
            order_type: "MARKET" or "LIMIT"
            price: Limit price (required for LIMIT orders)
            position_side: "BOTH", "LONG", or "SHORT"
            reduce_only: Whether order should only reduce position
            
        Returns:
            Order response
        """
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "positionSide": position_side,
            "quantity": self._format_quantity(symbol, size),
            "reduceOnly": "true" if reduce_only else "false"  # API expects string "true"/"false"
        }
        
        if order_type.upper() == "LIMIT":
            if not price:
                raise ValueError("Price is required for LIMIT orders")
            params["price"] = self._format_price(symbol, price)
            params["timeInForce"] = "GTC"
        
        return await self._request("POST", "/fapi/v3/order", params)
    
    async def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order"""
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        return await self._request("DELETE", "/fapi/v3/order", params)
    
    async def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """Cancel all open orders for a symbol"""
        params = {"symbol": symbol}
        return await self._request("DELETE", "/fapi/v3/allOpenOrders", params)
    
    async def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close a position"""
        position = await self.get_position(symbol)
        if not position:
            raise ValueError(f"No open position for {symbol}")
        
        position_amt = float(position.get("positionAmt", 0))
        if position_amt == 0:
            raise ValueError(f"Position for {symbol} has 0 size")
        
        # Determine side for closing
        side = "SELL" if position_amt > 0 else "BUY"
        size = abs(position_amt)
        
        return await self.place_order(
            symbol=symbol,
            side=side,
            size=size,
            order_type="MARKET",
            reduce_only=True
        )
    
    async def set_stop_loss(self, symbol: str, stop_price: float, size: float, side: str = "SELL") -> Dict[str, Any]:
        """
        Set stop loss for a position
        
        Args:
            symbol: Trading symbol
            stop_price: Stop loss trigger price
            size: Position size
            side: "SELL" for LONG positions, "BUY" for SHORT positions
        """
        # Format price and quantity with proper precision
        stop_price_rounded = self._format_price(symbol, stop_price)
        quantity_formatted = self._format_quantity(symbol, size)
        
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "STOP_MARKET",
            "stopPrice": stop_price_rounded,
            "quantity": quantity_formatted,
            "positionSide": "BOTH",
            "reduceOnly": "true"
        }
        
        return await self._request("POST", "/fapi/v3/order", params)
    
    async def set_take_profit(self, symbol: str, target_price: float, size: float, side: str = "SELL") -> Dict[str, Any]:
        """
        Set take profit for a position
        
        Args:
            symbol: Trading symbol
            target_price: Take profit trigger price
            size: Position size
            side: "SELL" for LONG positions, "BUY" for SHORT positions
        """
        # Format price and quantity with proper precision
        target_price_rounded = self._format_price(symbol, target_price)
        quantity_formatted = self._format_quantity(symbol, size)
        
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "TAKE_PROFIT_MARKET",
            "stopPrice": target_price_rounded,
            "quantity": quantity_formatted,
            "positionSide": "BOTH",
            "reduceOnly": "true"
        }
        
        return await self._request("POST", "/fapi/v3/order", params)
    
    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage for a symbol"""
        params = {
            "symbol": symbol,
            "leverage": leverage
        }
        return await self._request("POST", "/fapi/v3/leverage", params)
    
    # ========== User Data Stream Methods ==========
    
    async def start_user_data_stream(self) -> str:
        """
        Start a user data stream and get listenKey
        
        Returns:
            listenKey string for WebSocket connection
        """
        # POST /fapi/v1/listenKey - requires USER_STREAM authentication
        result = await self._request("POST", "/fapi/v1/listenKey", {})
        listen_key = result.get("listenKey")
        if not listen_key:
            raise ValueError("Failed to get listenKey from Aster API")
        logger.info(f"✅ Obtained listenKey for user data stream (valid for 60 minutes)")
        return listen_key
    
    async def keepalive_user_data_stream(self) -> Dict[str, Any]:
        """
        Keepalive user data stream to prevent timeout
        Extends listenKey validity for 60 minutes
        """
        return await self._request("PUT", "/fapi/v1/listenKey", {})
    
    async def close_user_data_stream(self) -> Dict[str, Any]:
        """Close user data stream"""
        return await self._request("DELETE", "/fapi/v1/listenKey", {})
