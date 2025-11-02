# 🎯 Dual Strategy Dashboard

## Overview

The dashboard now displays **two autonomous trading strategies side-by-side**, making it crystal clear that you're running multiple AI-powered bots simultaneously!

## Dashboard Layout

### 🔝 **Top Section: Portfolio Summary** (Full Width)
- **Total Portfolio Value**: Combined balance across all strategies
- **Total Unrealized PNL**: Real-time profit/loss
- **Total Exposure**: Combined position sizes (ASTER + BTC)
- **Active Strategies**: Number of bots running (2)

### 📊 **Two-Column Strategy View**

#### Left Column: **ASTER Strategy** 🟦 (Cyan Border)
- **Strategy**: AI-Powered Technical Analysis
- **Symbol**: ASTERUSDT
- **Candles**: 5-minute intervals
- **Components**:
  - Performance metrics (trades, win rate, PNL)
  - Current exposure
  - Open positions (compact view)
  - AI decision log
  - Trade history

#### Right Column: **MOON Strategy** 🟪 (Purple Border)
- **Strategy**: Lunar Phase Trading
- **Symbol**: BTCUSDT
- **Basis**: Moon phases (waning/waxing cycles)
- **Components**:
  - Performance metrics (trades, win rate, PNL)
  - Current exposure
  - Open positions (compact view)
  - AI decision log
  - Trade history

---

## Backend API Endpoints

### New Endpoints

#### 1. `/api/portfolio/summary`
Returns overall portfolio metrics across all strategies:
```json
{
  "total_balance": 119.50,
  "available_balance": 82.13,
  "total_unrealized_pnl": 0.0277,
  "total_exposure": 0.00,
  "aster_exposure": 0.00,
  "btc_exposure": 0.00,
  "strategies_active": 2
}
```

#### 2. `/api/performance?symbol=ASTERUSDT` or `?symbol=BTCUSDT`
Strategy-specific performance metrics:
```json
{
  "symbol": "ASTERUSDT",
  "total_trades": 5,
  "win_rate": 0.60,
  "total_pnl": 2.50,
  "realized_pnl": 1.25,
  "unrealized_pnl": 1.25,
  "winning_trades": 3,
  "open_positions": 1,
  "total_exposure": 20.00
}
```

#### 3. `/api/decisions?symbol=X&limit=N`
Filter decisions by strategy:
- `?symbol=ASTERUSDT` - Only ASTER bot decisions
- `?symbol=BTCUSDT` - Only MOON bot decisions
- No symbol parameter - All decisions

#### 4. `/api/trades?symbol=X&limit=N`
Filter trades by strategy:
- `?symbol=ASTERUSDT` - Only ASTER trades
- `?symbol=BTCUSDT` - Only MOON trades
- No symbol parameter - All trades

---

## Visual Design

### Color Coding
- **ASTER Bot**: Cyan/Blue theme 🟦
- **MOON Bot**: Purple/Pink theme 🟪
- **Portfolio Summary**: Purple gradient banner
- **Profit**: Green text
- **Loss**: Red text

### Borders
- ASTER section: `border-cyan-500/30`
- MOON section: `border-purple-500/30`
- Compact positions: Smaller, cleaner cards

### Icons
- **ASTER**: Brain icon (AI intelligence)
- **MOON**: Zap/Lightning icon (quick lunar cycles)
- **Portfolio**: Brain with gradient background

---

## Component Updates

### `App.jsx` (Dual Strategy Version)
- Fetches data separately for each symbol
- Filters positions by symbol
- Two-column responsive grid layout
- Portfolio summary banner at top

### `PositionsPanel.jsx`
- Added **`compact` mode** for dual strategy view
- Compact cards show: side, notional, PNL (smaller)
- Full cards show: entry price, size, leverage, notional

### Backend: `dashboard_api/server.py`
- New endpoint: `/api/portfolio/summary`
- Symbol filtering for all major endpoints
- Fetches data for both ASTERUSDT and BTCUSDT
- Calculates exposure per strategy

---

## How It Works

1. **Dashboard Frontend** (`App.jsx`):
   - Polls API every 3 seconds
   - Makes parallel requests for:
     - Portfolio summary
     - ASTER performance, decisions, trades, positions
     - MOON performance, decisions, trades, positions
   - Displays in two separate columns

2. **Backend API** (`server.py`):
   - Dedicated `AsterClient` for dashboard
   - Fetches data from Aster API for both symbols
   - Aggregates portfolio metrics
   - Filters and returns symbol-specific data

3. **Trading Bots** (`main_dual.py`):
   - Both bots run concurrently via `asyncio.gather`
   - Share the same account but trade different symbols
   - Log decisions separately to different files

---

## Files Modified/Created

### Backend
- ✅ `dashboard_api/server.py` - Added portfolio summary and symbol filtering
  
### Frontend
- ✅ `dashboard/src/App_dual.jsx` - New dual strategy layout
- ✅ `dashboard/src/App.jsx` - Replaced with dual version (backup saved as `App_old.jsx`)
- ✅ `dashboard/src/components/PositionsPanel.jsx` - Added compact mode

---

## Quick Start

### Start Dual Bot System
```bash
python main_dual.py
```

### Access Dashboard
Open: **http://localhost:3001**

### Check Portfolio Summary
```bash
curl http://localhost:8000/api/portfolio/summary
```

### Check ASTER Performance
```bash
curl http://localhost:8000/api/performance?symbol=ASTERUSDT
```

### Check MOON Performance
```bash
curl http://localhost:8000/api/performance?symbol=BTCUSDT
```

---

## Benefits of Dual Dashboard

1. ✅ **Clear Strategy Separation**: Visually distinct sections
2. ✅ **Performance Comparison**: See which strategy performs better
3. ✅ **Portfolio Overview**: Total exposure and health at a glance
4. ✅ **Strategy-Specific Metrics**: Track each bot independently
5. ✅ **Real-Time Updates**: All data refreshes every 3 seconds
6. ✅ **Color-Coded**: Easy to distinguish strategies
7. ✅ **Compact Design**: Fits both strategies on one screen

---

## Configuration

Both bots share the same configuration from `.env`:

```env
# Trading symbols are automatic:
# - ASTER bot: ASTERUSDT
# - MOON bot: BTCUSDT

TRADING_MODE=mainnet
LEVERAGE=4
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Aster Wallet
ASTER_USER_ADDRESS=0x...
ASTER_SIGNER_ADDRESS=0x...
ASTER_PRIVATE_KEY=0x...
```

---

## Screenshots (Text Representation)

```
┌────────────────────────────────────────────────────────────────────┐
│  [👁️] PORTFOLIO SUMMARY                                            │
│  Total: $119  |  PNL: +$0.03  |  Exposure: $40  |  Strategies: 2  │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐  ┌──────────────────────────────┐
│ 🟦 ASTER STRATEGY           │  │ 🟪 MOON STRATEGY             │
│ AI Technical • 5min candles │  │ Lunar Phases • BTC Only      │
├─────────────────────────────┤  ├──────────────────────────────┤
│ Trades: 5  |  Win: 60%      │  │ Trades: 2  |  Win: 50%       │
│ PNL: +$2.50                 │  │ PNL: -$0.50                  │
│ Exposure: $20               │  │ Exposure: $20                │
├─────────────────────────────┤  ├──────────────────────────────┤
│ Open Positions:             │  │ Open Positions:              │
│ [LONG $20 +$1.25]           │  │ [No positions]               │
├─────────────────────────────┤  ├──────────────────────────────┤
│ AI Decisions:               │  │ AI Decisions:                │
│ • HOLD (conf: 65%)          │  │ • HOLD (moon transition)     │
│ • LONG (conf: 75%)          │  │ • HOLD (new moon phase)      │
├─────────────────────────────┤  ├──────────────────────────────┤
│ Trade History:              │  │ Trade History:               │
│ • LONG ASTERUSDT +$1.25     │  │ • SHORT BTCUSDT -$0.50       │
│ • SHORT ASTERUSDT +$0.80    │  │ • LONG BTCUSDT +$0.00        │
└─────────────────────────────┘  └──────────────────────────────┘
```

---

## Troubleshooting

### Dashboard not updating?
- Ensure `main_dual.py` is running (not just `main.py`)
- Check http://localhost:8000/api/status
- Refresh browser (Ctrl+F5)

### Seeing only one strategy?
- Both bots need to have made at least one decision
- MOON bot may be in HOLD if moon phase is transitioning
- Check logs: `logs/vibe_trader.log`

### Data shows $0 everywhere?
- Bot just started, wait for first update cycle (5 minutes)
- No positions open yet
- Check API: `curl http://localhost:8000/api/portfolio/summary`

---

## Next Steps

1. ✅ Monitor both strategies in real-time
2. ✅ Compare performance: AI vs Moon phases
3. ✅ Adjust position sizes per strategy
4. ✅ Track which strategy works better in different market conditions
5. ✅ Submit to Aster Trading Arena competition!

---

Made with 🧠 AI + 🌙 Moon Phases for the **Aster Vibe Trading Arena**


