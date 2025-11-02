# 🤖 Multi-Bot Trading System Setup

## 🎯 What This Does

Run **multiple trading bots simultaneously**, each with:
- ✅ Different LLM models (GPT-4o-mini, DeepSeek, Claude)
- ✅ Different trading strategies (aggressive, contrarian, trend-following)
- ✅ Different wallet credentials (separate accounts)
- ✅ Same or different symbols (ASTERUSDT, BTCUSDT, etc.)

Perfect for **A/B testing strategies** and comparing model performance!

---

## 📋 Setup Instructions

### Step 1: Get Your Second Wallet Credentials

You mentioned you have new credentials for Bot 2:
- User Address
- Signer Address  
- Private Key

### Step 2: Get DeepSeek API Key

1. Go to: https://platform.deepseek.com/
2. Sign up / Login
3. Create API key
4. Copy it (starts with `sk-...`)

### Step 3: Configure Your .env File

Copy the template and fill in your details:

```bash
# BOT 1: GPT-4o-mini (Your current bot)
ASTER_USER_ADDRESS=0xYourCurrentUserAddress
ASTER_SIGNER_ADDRESS=0xYourCurrentSignerAddress
ASTER_PRIVATE_KEY=0xYourCurrentPrivateKey
OPENAI_API_KEY=sk-your-openai-key

# BOT 2: DeepSeek (Your new bot)
BOT2_ENABLED=true
BOT2_USER_ADDRESS=0xYourNewUserAddress
BOT2_SIGNER_ADDRESS=0xYourNewSignerAddress
BOT2_PRIVATE_KEY=0xYourNewPrivateKey
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Bot 2 Settings
BOT2_SYMBOL=ASTERUSDT
BOT2_STRATEGY=contrarian
```

### Step 4: Run the Multi-Bot System

```bash
python main_multi_bot.py
```

---

## 🤖 Bot Configurations

### BOT 1: GPT-4o-mini - "Aggressive Alpha Seeker"
**Strategy:** Aggressive trend/breakout trading
- Uses advanced multi-timeframe analysis
- Dynamic position sizing
- ATR-based stops
- Looks for high-quality setups

**Personality:**
- Elite trader, 10+ years experience
- Aggressive when edge is clear
- Patient when edge is unclear
- Focus on asymmetric risk/reward

### BOT 2: DeepSeek - "Contrarian Mean Reverter"
**Strategy:** Mean reversion / Contrarian
- Fades RSI extremes
- Bollinger Band reversions
- Counter-trend entries
- Quick scalps with tight stops

**Personality:**
- Contrarian specialist
- Buys fear, sells greed
- RSI <30 = LONG, RSI >70 = SHORT
- Quick in, quick out

---

## 🎨 Available Strategies

You can set `BOT2_STRATEGY` to any of these:

### 1. `aggressive` (Default for Bot 1)
- Multi-timeframe trend following
- High-quality setups only
- Larger positions on conviction
- 2:1 R/R minimum

### 2. `contrarian` (Recommended for Bot 2)
- Fade RSI extremes (<30 or >70)
- Bollinger Band reversions
- Counter-trend entries
- Quick exits

### 3. `trend_following`
- Only trade with 4+ timeframes aligned
- Enter on pullbacks
- Hold for larger moves
- Never counter-trend

### 4. `breakout`
- Wait for Bollinger Band squeezes
- Trade volume breakouts
- Large move targets (>3%)
- Tight initial stops

### 5. `scalper`
- Quick 0.5-1% targets
- Hold <30 minutes
- Very tight stops
- High frequency

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  MULTI-BOT SYSTEM                                           │
└─────────────────────────────────────────────────────────────┘

BOT 1 (GPT-4o-mini)                BOT 2 (DeepSeek)
      │                                    │
      ├─ Wallet 1                          ├─ Wallet 2
      ├─ ASTERUSDT                         ├─ ASTERUSDT (or other)
      ├─ Aggressive strategy               ├─ Contrarian strategy
      ├─ Every 60s                         ├─ Every 60s
      │                                    │
      ├─► Analyzes market                  ├─► Analyzes market
      ├─► Makes decision                   ├─► Makes decision
      ├─► Executes trade                   ├─► Executes trade
      ├─► Logs to decisions_GPT4o.json     ├─► Logs to decisions_DEEPSEEK.json
      │                                    │
      └─► Both visible on dashboard        └─► Both visible on dashboard
```

---

## 🔍 Monitoring Both Bots

### Logs
Each bot has separate log files:
- `logs/decisions_GPT4o.json` - Bot 1 decisions
- `logs/decisions_DEEPSEEK.json` - Bot 2 decisions
- `logs/trade_outcomes_GPT4o.json` - Bot 1 trades
- `logs/trade_outcomes_DEEPSEEK.json` - Bot 2 trades

### Dashboard
**http://localhost:3000**

Currently shows Bot 1 (primary). Can be enhanced to show both bots side-by-side.

### Console Output
```
[GPT4o] Opening LONG: $45 @ $1.09
[DEEPSEEK] Opening SHORT: $30 @ $1.10 (contrarian play)
[GPT4o] Decision: hold - Letting position ride
[DEEPSEEK] Decision: close - Taking quick profit
```

---

## 💰 Cost Comparison

### Running Both Bots (60-second intervals):

**Bot 1 (GPT-4o-mini):**
- ~$27/month

**Bot 2 (DeepSeek):**
- ~$19/month (with cache hits)

**Total: ~$46/month for 2 bots**

### What You Get:
- 2x the trading opportunities
- 2x different strategies
- Compare performance directly
- Hedge strategies (one trend, one counter-trend)
- Diversify model risk

---

## 🎯 Quick Start Checklist

When you return with the info:

- [ ] Paste Bot 2 wallet credentials
- [ ] Paste DeepSeek API key
- [ ] Choose Bot 2 symbol (ASTERUSDT or different?)
- [ ] Choose Bot 2 strategy (contrarian recommended)
- [ ] Update .env file
- [ ] Run: `python main_multi_bot.py`
- [ ] Monitor both bots on dashboard

---

## 🔧 Advanced: Adding More Bots

Want Bot 3, 4, 5? Just edit `main_multi_bot.py`:

```python
# BOT 3: Claude Haiku - Swing Trader
bot3 = BotConfig(
    name="CLAUDE",
    user_address=os.getenv("BOT3_USER_ADDRESS"),
    signer_address=os.getenv("BOT3_SIGNER_ADDRESS"),
    private_key=os.getenv("BOT3_PRIVATE_KEY"),
    llm_provider="anthropic",
    llm_model="claude-3-5-haiku-20241022",
    llm_api_key=os.getenv("ANTHROPIC_API_KEY"),
    symbol="BTCUSDT",
    strategy_name="swing_trader"
)
bots_config.append(bot3)
```

---

## 🚀 Ready When You Are!

Once you provide:
1. ✅ Bot 2 User Address
2. ✅ Bot 2 Signer Address
3. ✅ Bot 2 Private Key
4. ✅ DeepSeek API Key

I'll help you configure and launch both bots simultaneously! 🎯

---

## 💡 Strategy Recommendations

**Complementary Pair (Recommended):**
- **Bot 1:** Aggressive trend-following (GPT-4o-mini)
- **Bot 2:** Contrarian mean-reversion (DeepSeek)

This way:
- When market trends → Bot 1 profits
- When market reverses → Bot 2 profits
- Natural hedge between strategies
- Compare which strategy performs better

**Same Strategy (Benchmark Test):**
- **Bot 1:** Aggressive (GPT-4o-mini)
- **Bot 2:** Aggressive (DeepSeek)

This way:
- Compare GPT vs DeepSeek directly
- Same strategy, different model
- See which AI makes better decisions
- Pure model comparison

Your choice! 🎲

