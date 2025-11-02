# 🤖 Dual Trading Bot System

## Overview

You're now running **TWO** autonomous trading bots simultaneously on Aster DEX:

### Bot 1: ASTERUSDT Vibe Trader 🪙
- **Symbol**: ASTERUSDT (Aster token)
- **Strategy**: AI-driven analysis using GPT-4
- **Decision Making**: Technical analysis of price action, candles, and trends
- **Leverage**: 4x
- **Update Interval**: Every 5 minutes

### Bot 2: Moon Phase Trader 🌕  
- **Symbol**: BTCUSDT (Bitcoin)
- **Strategy**: Lunar cycle-based trading
- **Decision Making**: Follows moon phases
  - 🌘 **Moon Waning** → BTC Waxing → **LONG**
  - 🌒 **Moon Waxing** → BTC Waning → **SHORT**
  - 🌑 **New Moon / 🌕 Full Moon** → **HOLD** (transition periods)
- **Leverage**: 4x  
- **Update Interval**: Every 5 minutes

---

## Current Status

### Moon Phase Today
- **Phase**: New Moon (99.0%)
- **Illumination**: 3.1%
- **Trend**: Waxing Start (transition)
- **Trading Bias**: HOLD (waiting for clear trend)

The moon bot will start taking positions once the moon enters a clear waxing or waning phase!

---

## How to Use

### Start Both Bots
```bash
python main_dual.py
```

### Check Moon Phase
```bash
python scripts/check_moon.py
```

### View Dashboard
Open: http://localhost:3001

The dashboard shows combined data from both bots.

### Check Individual Bot Logs
- **Main Log**: `logs/vibe_trader.log`
- **Moon Decisions**: `logs/moon_decisions_BTCUSDT.json`
- **Aster Decisions**: `logs/decisions.json`

---

## Trading Philosophy

### ASTERUSDT Bot
Uses AI to analyze:
- Historical candles (15m intervals, 12 hours)
- Price trends (2h, 4h)
- 24h price change
- Current positions
- Risk management (stop loss, take profit)

### Moon Phase Bot
Based on crypto folklore:
> "Buy when the moon wanes, sell when it waxes"

The moon completes a cycle every ~29.5 days:
- **Days 1-14**: Moon Waxing → BTC tends to correct → **SHORT bias**
- **Days 15-29**: Moon Waning → BTC tends to rally → **LONG bias**

---

## Files Created

1. `agent/moon_trader.py` - Moon phase trading logic
2. `main_dual.py` - Dual bot launcher
3. `scripts/check_moon.py` - Moon phase checker
4. `DUAL_BOT_README.md` - This file!

---

## Configuration

Both bots share the same config from `.env`:

```env
# Trading Configuration
TRADING_MODE=mainnet
TRADING_SYMBOL=ASTERUSDT   # Only for single bot mode
LEVERAGE=4

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Aster Wallet
ASTER_USER_ADDRESS=0x...
ASTER_SIGNER_ADDRESS=0x...
ASTER_PRIVATE_KEY=0x...
```

---

## Risk Management

Each bot independently manages:
- ✅ Position sizing ($20 USD per trade by default)
- ✅ Automatic stop losses
- ✅ Automatic take profits
- ✅ Confidence thresholds (only trade if confidence > 60%)
- ✅ Leverage control (4x)

**Important**: Both bots share the same Aster account balance. Total exposure = ASTERUSDT position + BTCUSDT position.

---

## Next Steps

1. **Monitor the moon**: As the phase changes, the moon bot will start trading BTC
2. **Watch both positions**: Dashboard shows both ASTER and BTC trades
3. **Compare strategies**: See which performs better - AI analysis or lunar cycles! 😄

---

## Fun Facts

- The "trade the moon" strategy is a real (though controversial) thing in crypto Twitter
- Studies have shown weak correlations between lunar cycles and financial markets
- Bitcoin's price movement during full moons has been analyzed multiple times
- This is the MOST meta way to compete in Aster Trading Arena - trading ASTER token with AI while trading BTC with moon phases! 🚀🌕

---

## Troubleshooting

### Both bots not showing decisions?
- Wait 5 minutes for the next update cycle
- Check `logs/vibe_trader.log` for errors
- Moon bot waits for clear moon phases (not transitions)

### Dashboard not updating?
- Ensure `main_dual.py` is running (not just `main.py`)
- Check http://localhost:8000/api/status
- Refresh browser

### Want to run just one bot?
- ASTERUSDT only: `python main.py`
- Both: `python main_dual.py`

---

Made with 🌙 and ⚡ for the Aster Trading Arena Competition


