# Getting Started with Aster Vibe Trader

## Quick Start Guide

### Step 1: Review the API Documentation

The Aster API documentation is available at:
- **GitHub**: https://github.com/asterdex/api-docs/blob/master/README.md
- **Hypereth Docs**: https://docs.hypereth.io/api-reference/introduction

Read through these to understand:
- Authentication methods
- Available endpoints
- Request/response formats
- Rate limits
- Error codes

### Step 2: Get API Credentials

1. Visit the Aster platform
2. Create an account or log in
3. Generate API credentials (API Key and Secret)
4. **Important**: Start with testnet credentials if available

### Step 3: Configure Environment

1. Copy the environment template:
```bash
copy .env.example .env
```

2. Edit `.env` with your credentials:
```env
# Aster API (already configured with correct URLs)
ASTER_API_KEY=your_actual_api_key_here
ASTER_API_SECRET=your_actual_api_secret_here

# Choose your LLM provider
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...

# Start with testnet!
TRADING_MODE=testnet
```

### Step 4: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install dashboard
cd dashboard
npm install
cd ..
```

### Step 5: Discover API Endpoints

Run our endpoint discovery script:
```bash
python scripts/fetch_api_spec.py
```

This will help you understand what endpoints are available.

### Step 6: Test API Connection

Once you have credentials, test the connection:
```bash
python scripts/test_connection.py
```

This will verify:
- ✓ Authentication works
- ✓ Market data endpoints respond
- ✓ Account endpoints are accessible

### Step 7: Update API Client (If Needed)

Based on the actual API documentation, you may need to update `api/aster_client.py`:

1. **Authentication signature** - Update `_generate_signature()` method
2. **Endpoint paths** - Verify all endpoint URLs
3. **Response parsing** - Match actual response structure
4. **Error handling** - Add Aster-specific error codes

See `API_INTEGRATION_CHECKLIST.md` for detailed steps.

### Step 8: Run the System

Start all components:

**Terminal 1 - Backend & Agent:**
```bash
python run.py
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard
npm run dev
```

Then open your browser to: http://localhost:3000

### Step 9: Monitor Initial Behavior

When first starting:
1. Watch the logs in `logs/vibe_trader.log`
2. Monitor the dashboard for AI decisions
3. Start with small position sizes
4. Verify trades execute correctly

### Step 10: Iterate and Optimize

1. Monitor performance metrics
2. Adjust trading parameters in `.env`
3. Customize AI prompts in `agent/trader.py`
4. Add new strategies in `strategies/`

## Configuration Options

### Trading Parameters

```env
MAX_POSITION_SIZE=1000      # Max position in USD
RISK_PER_TRADE=0.02         # Risk 2% per trade
MAX_OPEN_POSITIONS=5        # Max concurrent positions
```

### LLM Configuration

```python
# In config/config.py
provider: "anthropic" or "openai"
model: "claude-3-5-sonnet-20241022" or "gpt-4-turbo-preview"
temperature: 0.7  # Lower = more conservative
```

### Update Interval

```python
# In config/config.py
update_interval: 60  # Seconds between decisions
```

## Troubleshooting

### API Connection Fails
- Verify API key and secret are correct
- Check you're using the right environment (testnet vs mainnet)
- Ensure API base URL is correct
- Check rate limits aren't exceeded

### LLM Errors
- Verify API key is valid
- Check you have sufficient credits
- Try reducing `max_tokens` if hitting limits

### Dashboard Not Loading
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in `dashboard_api/server.py`

### No Trades Executing
- Check logs for decision reasoning
- Verify risk parameters aren't too restrictive
- Ensure sufficient account balance
- Check market conditions (may be no opportunities)

## Competition Timeline

- **Submissions**: Oct 21 - Nov 3, 2025
- **Winners Announced**: By Nov 21, 2025

## Success Metrics

The competition will likely evaluate:
1. **Total P&L** - Overall profitability
2. **Risk-Adjusted Returns** - Sharpe ratio, max drawdown
3. **AI Innovation** - Quality of AI decision-making
4. **Dashboard Quality** - Clarity of logic and transparency

## Tips for Success

1. **Start Conservative**: Small positions, low risk
2. **Monitor Closely**: Watch first 24 hours carefully
3. **Iterate Quickly**: Adjust based on performance
4. **Document Everything**: Keep notes on strategy changes
5. **Risk Management**: Never risk more than you can afford to lose
6. **Diversify**: Don't put all capital in one position
7. **Use Stop Losses**: Always protect your downside

## Resources

- **Aster API Docs**: https://github.com/asterdex/api-docs
- **Hypereth Docs**: https://docs.hypereth.io
- **Competition Info**: Check Aster's official announcement
- **Our Docs**: See `docs/` folder for detailed guides

## Next Steps

1. ✅ Project structure created
2. ✅ AI agent implemented
3. ✅ Dashboard built
4. 🔄 Review API documentation
5. 🔄 Get API credentials
6. 🔄 Test connection
7. 🔄 Run on testnet
8. 🔄 Monitor and optimize
9. 🔄 Deploy for competition

Good luck! 🚀

