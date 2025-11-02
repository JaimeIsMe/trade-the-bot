# Aster API Integration Checklist

Once you receive the Aster API documentation, update the following files:

## 1. API Client (`api/aster_client.py`)

### Authentication
- [ ] Update `_generate_signature()` method with actual Aster signature algorithm
- [ ] Verify header format (`X-ASTER-API-KEY`, etc.)
- [ ] Update timestamp format if different

### Endpoints to Verify/Update

#### Market Data
- [ ] `get_markets()` - endpoint and response format
- [ ] `get_orderbook()` - endpoint, parameters, response format
- [ ] `get_recent_trades()` - endpoint and data structure
- [ ] `get_funding_rates()` - endpoint and format

#### Account Data
- [ ] `get_balance()` - endpoint and response fields
- [ ] `get_positions()` - endpoint and position data structure
- [ ] `get_position()` - single position lookup
- [ ] `get_open_orders()` - orders endpoint

#### Trading
- [ ] `place_order()` - order placement endpoint and payload format
- [ ] Order types supported (market, limit, stop, etc.)
- [ ] `cancel_order()` - cancellation endpoint
- [ ] `close_position()` - position closing method
- [ ] `set_stop_loss()` - stop loss order format
- [ ] `set_take_profit()` - take profit order format

### WebSocket (if available)
- [ ] Add WebSocket connection for real-time data
- [ ] Subscribe to orderbook updates
- [ ] Subscribe to trade executions
- [ ] Subscribe to position updates

## 2. Configuration (`config/config.py`)

- [ ] Verify default API URL
- [ ] Add WebSocket URL if available
- [ ] Update any Aster-specific configuration parameters

## 3. Agent (`agent/trader.py`)

### Data Structure Mapping
- [ ] Update market data parsing in `_gather_market_data()`
- [ ] Update portfolio parsing in `_analyze_portfolio()`
- [ ] Verify position field names (size, side, entry_price, etc.)
- [ ] Update balance field access

### Order Execution
- [ ] Verify order parameters in `_execute_decision()`
- [ ] Update stop loss/take profit setting logic
- [ ] Add error handling for specific Aster error codes

## 4. Dashboard (`dashboard_api/server.py`)

- [ ] Update data structure for positions
- [ ] Update balance display fields
- [ ] Verify all API endpoints return correct format

## 5. Testing

After integration:

- [ ] Run `python scripts/test_connection.py`
- [ ] Verify all endpoints return data
- [ ] Test order placement on testnet
- [ ] Test position management
- [ ] Verify stop loss/take profit functionality
- [ ] Test error handling

## 6. Risk Management

- [ ] Verify leverage calculation with Aster's leverage system
- [ ] Update margin calculations if different from assumptions
- [ ] Test position size limits
- [ ] Verify liquidation price calculations

## Common API Fields to Look For

### Position Object
```python
{
    "symbol": str,
    "side": str,  # "long" or "short"
    "size": float,
    "entry_price": float,
    "mark_price": float,
    "liquidation_price": float,
    "unrealized_pnl": float,
    "leverage": float,
    # ... other fields
}
```

### Order Object
```python
{
    "order_id": str,
    "symbol": str,
    "side": str,  # "buy" or "sell"
    "type": str,  # "market", "limit", etc.
    "size": float,
    "price": float,  # for limit orders
    "status": str,  # "open", "filled", "cancelled"
    # ... other fields
}
```

### Balance Object
```python
{
    "total": float,
    "available": float,
    "used": float,
    "unrealized_pnl": float,
    # ... other fields
}
```

## Documentation to Request

If not in docs, ask Aster for:

1. **Rate Limits** - requests per second/minute
2. **Error Codes** - list of error codes and meanings
3. **Testnet URL** - separate endpoint for testing
4. **WebSocket API** - if available for real-time updates
5. **Leverage Settings** - how leverage is set and managed
6. **Fee Structure** - maker/taker fees, funding rate calculation
7. **Order Types** - all supported order types and parameters
8. **Position Modes** - hedge mode vs one-way mode

## Quick Start After Integration

1. Update `.env` with real API credentials
2. Run connection test: `python scripts/test_connection.py`
3. Place a small test order on testnet
4. Verify dashboard displays data correctly
5. Start with conservative risk parameters
6. Monitor logs for any API errors

## Notes

- Keep a copy of the original `aster_client.py` as reference
- Test each endpoint individually before running the full system
- Start with READ-ONLY operations (market data) before trading
- Use testnet extensively before going live

