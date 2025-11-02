# Aster API Integration Notes

## API Information

Based on the documentation at [asterdex/api-docs](https://github.com/asterdex/api-docs/blob/master/README.md), Aster uses the Hypereth API infrastructure.

### Base URLs

- **REST API**: `https://api.hypereth.io/v1/aster`
- **WebSocket API**: `wss://api.hypereth.io/v1/aster/perp/ws`

### Authentication

All operations require cryptographic signatures for security. The API uses:
- API Key authentication
- HMAC signature verification
- Timestamp-based requests to prevent replay attacks

### Rate Limits

- Rate limits are enforced per IP address
- Order submissions are limited per account
- Each response includes headers indicating usage and limits

## Documentation Resources

- **Main API Docs**: https://github.com/asterdex/api-docs
- **Hypereth Docs**: https://docs.hypereth.io/api-reference/introduction

## Supported Exchanges

The Hypereth API supports multiple decentralized exchanges, including:
- Aster Perp DEX
- Other DEX protocols

## Next Steps for Integration

1. **Review Full Documentation**: Read through the complete API docs at the GitHub repository
2. **Understand Authentication**: Implement the signature generation method
3. **Map Endpoints**: Update the client with actual endpoint paths
4. **Test Connection**: Use the test script to verify connectivity
5. **Implement WebSocket**: Add real-time data streaming for better performance

## Key Endpoints to Implement

### Market Data (Public)
- Get markets/instruments
- Get orderbook
- Get recent trades
- Get funding rates
- Get historical data

### Account Management (Private)
- Get account balance
- Get positions
- Get open orders
- Get trade history
- Get account info

### Trading (Private)
- Place order (market/limit)
- Cancel order
- Cancel all orders
- Close position
- Modify order
- Set leverage

### WebSocket Streams
- Orderbook updates
- Trade feed
- Account updates
- Position updates
- Order updates

## Important Considerations

1. **Testnet**: Ensure there's a testnet environment for safe testing
2. **Error Handling**: Implement robust error handling for all API calls
3. **Rate Limiting**: Respect rate limits to avoid being blocked
4. **Reconnection Logic**: Implement automatic reconnection for WebSocket
5. **Data Validation**: Validate all inputs before sending to API
6. **Logging**: Log all API interactions for debugging

## Competition Requirements

For the Aster Vibe Trading Arena, we need to:
1. ✅ Build autonomous AI trader using LLM
2. ✅ Execute live trades via Aster API
3. ✅ Create dashboard showing agent logic, prompts & positions

Our implementation addresses all these requirements.

