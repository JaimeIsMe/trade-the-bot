# Aster Vibe Trader - Setup Guide

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Aster API Configuration (to be provided)
ASTER_API_KEY=your_api_key_here
ASTER_API_SECRET=your_api_secret_here
ASTER_API_URL=https://api.aster.exchange

# LLM Configuration
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Trading Configuration
TRADING_MODE=testnet
MAX_POSITION_SIZE=1000
RISK_PER_TRADE=0.02
MAX_OPEN_POSITIONS=5

# Dashboard Configuration
DASHBOARD_PORT=3000
API_PORT=8000
```

### 3. Install Dashboard Dependencies

```bash
cd dashboard
npm install
cd ..
```

### 4. Test API Connection

Before running the trader, test your API connection:

```bash
python scripts/test_connection.py
```

### 5. Run the System

#### Option A: Run Everything Together

```bash
python run.py
```

This will start:
- Trading agent
- Dashboard API server (port 8000)

Then in a separate terminal, start the dashboard UI:

```bash
cd dashboard
npm run dev
```

Dashboard will be available at: http://localhost:3000

#### Option B: Run Components Separately

**Terminal 1 - Trading Agent:**
```bash
python main.py
```

**Terminal 2 - Dashboard API:**
```bash
cd dashboard_api
uvicorn server:app --reload --port 8000
```

**Terminal 3 - Dashboard UI:**
```bash
cd dashboard
npm run dev
```

## Configuration

### LLM Provider

You can choose between OpenAI and Anthropic:

```python
# In config/config.py or via .env
LLM_PROVIDER=anthropic  # or "openai"
```

For Anthropic:
```env
ANTHROPIC_API_KEY=your_key
LLM_MODEL=claude-3-5-sonnet-20241022
```

For OpenAI:
```env
OPENAI_API_KEY=your_key
LLM_MODEL=gpt-4-turbo-preview
```

### Trading Parameters

Adjust risk parameters in `.env`:

```env
MAX_POSITION_SIZE=1000  # Maximum position size in USD
RISK_PER_TRADE=0.02     # Risk 2% per trade
MAX_OPEN_POSITIONS=5    # Maximum concurrent positions
```

### Update Interval

Change how often the agent makes decisions:

```python
# In config/config.py
update_interval: int = 60  # seconds between trading cycles
```

## Project Structure

```
aster_vibe_comp/
├── agent/              # AI trading agent
│   ├── trader.py       # Main trading logic
│   └── llm_client.py   # LLM integration
├── api/                # Aster API client
│   └── aster_client.py
├── dashboard/          # React dashboard
│   └── src/
│       ├── App.jsx
│       └── components/
├── dashboard_api/      # FastAPI backend
│   └── server.py
├── strategies/         # Trading strategies
│   └── momentum_strategy.py
├── config/             # Configuration
│   └── config.py
├── utils/              # Utilities
│   └── logger.py
├── scripts/            # Helper scripts
│   ├── test_connection.py
│   └── backtest.py
├── main.py            # Entry point
├── run.py             # Launch script
└── requirements.txt
```

## Troubleshooting

### API Connection Issues

If you get connection errors:

1. Verify your API credentials are correct
2. Check if you're using the correct API URL
3. Ensure you're on testnet if using test credentials
4. Run `python scripts/test_connection.py` for diagnostics

### Dashboard Not Loading

1. Ensure dashboard API is running on port 8000
2. Check browser console for errors
3. Verify proxy configuration in `dashboard/vite.config.js`

### LLM Errors

1. Verify your API key is set correctly
2. Check you have sufficient API credits
3. Ensure the model name is correct
4. Review logs in `logs/vibe_trader.log`

## Development

### Adding New Strategies

Create a new strategy in `strategies/`:

```python
class MyStrategy:
    def get_signal(self, market_data):
        # Your logic here
        return {"action": "long", "confidence": 0.8}
```

### Customizing the Agent

Modify prompts and decision logic in `agent/trader.py`:

```python
def _build_trading_prompt(self, market_data, portfolio_state):
    # Customize your prompt here
    pass
```

### Testing

```bash
# Run backtests
python scripts/backtest.py

# Test specific components
python -m pytest tests/
```

## Next Steps

1. ✅ Set up environment and dependencies
2. ✅ Configure API credentials
3. 🔄 Test API connection
4. 🔄 Run initial test with small position sizes
5. 🔄 Monitor performance on dashboard
6. 🔄 Iterate on strategy based on results
7. 🔄 Scale up position sizes gradually

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review Aster API documentation
- Test individual components with scripts in `scripts/`

Good luck in the competition! 🚀

