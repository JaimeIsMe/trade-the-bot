# ⚡ Quick Start - Copy & Paste Commands

## Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Keys

```bash
# Copy the example environment file
copy .env.example .env

# Open it in your editor
notepad .env
```

Add your credentials:
```env
ASTER_API_KEY=your_actual_key_here
ASTER_API_SECRET=your_actual_secret_here
ANTHROPIC_API_KEY=sk-ant-your_key_here
TRADING_MODE=testnet
```

## Step 3: Install Dashboard

```bash
cd dashboard
npm install
cd ..
```

## Step 4: Test API Connection

```bash
# Discover available endpoints
python scripts/fetch_api_spec.py

# Test your API credentials
python scripts/test_connection.py
```

## Step 5: Run the System

**Terminal 1 - Trading Agent & API:**
```bash
python run.py
```

**Terminal 2 - Dashboard UI:**
```bash
cd dashboard
npm run dev
```

**Open Dashboard:**
```
http://localhost:3000
```

## Step 6: Monitor Logs

**Real-time logs:**
```bash
# Windows
Get-Content logs\vibe_trader.log -Wait -Tail 50

# Mac/Linux
# tail -f logs/vibe_trader.log
```

## Alternative: Docker (Optional)

```bash
# Build and run with Docker
docker-compose up --build

# Dashboard will be at:
# http://localhost:3000
```

## Useful Commands

### Check System Status
```bash
# View recent logs
type logs\vibe_trader.log | more

# View errors only
type logs\errors.log | more

# View trades
type logs\trades.log | more
```

### Development

```bash
# Run tests (when implemented)
pytest tests/

# Run backtest
python scripts/backtest.py

# Format code
black .
```

### Troubleshooting

```bash
# Kill any stuck processes
# Windows:
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Reinstall dependencies
pip install -r requirements.txt --upgrade
cd dashboard && npm install && cd ..
```

## Configuration Changes

### Adjust Trading Parameters

Edit `.env`:
```env
MAX_POSITION_SIZE=1000      # Increase/decrease position size
RISK_PER_TRADE=0.02         # Adjust risk percentage
MAX_OPEN_POSITIONS=5        # Max concurrent positions
```

### Change Update Frequency

Edit `config/config.py`:
```python
update_interval: int = 60  # Change to 30 for more frequent updates
```

### Switch LLM Provider

Edit `.env`:
```env
# For Anthropic (recommended)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# For OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

## Competition Submission

Before submitting:

1. ✅ System running smoothly
2. ✅ Dashboard shows clear decision logic
3. ✅ Performance metrics are positive
4. ✅ All logs are clean (no errors)
5. ✅ Risk management working correctly

## Getting Help

- **Logs**: Check `logs/` directory
- **Docs**: Read `docs/` folder
- **API Issues**: See `docs/ASTER_API_NOTES.md`
- **Strategy**: Read `docs/COMPETITION_STRATEGY.md`

## Success Checklist

- [ ] API credentials configured
- [ ] Test connection successful
- [ ] Dashboard loads and displays data
- [ ] AI making decisions every minute
- [ ] Trades executing correctly
- [ ] Stop losses being set
- [ ] Performance metrics updating
- [ ] No errors in logs

## Competition Timeline

- **Now - Nov 3**: Build, test, optimize
- **Nov 3**: Final submission
- **Nov 21**: Winners announced

**You're ready to compete! Good luck! 🚀**

