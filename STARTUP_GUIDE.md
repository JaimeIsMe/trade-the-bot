# 🚀 Aster Vibe Trading Bot - Startup Guide

Complete guide to get your dual-strategy trading bot system up and running!

---

## 📋 System Overview

Your trading system consists of **3 main components**:

1. **Trading Bots** (Python) - ASTER Bot + MOON Bot
2. **Backend API** (FastAPI) - Serves data to dashboard
3. **Dashboard Frontend** (React/Vite) - Visual interface

---

## ⚡ Quick Start (TL;DR)

```powershell
# Terminal 1: Start Trading Bots + Backend API
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp
python main_dual.py

# Terminal 2: Start Dashboard Frontend
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp\dashboard
npm run dev

# Open browser to: http://localhost:3000
```

---

## 🔧 Detailed Startup Instructions

### **Step 1: Start Trading Bots + Backend API**

Open PowerShell in the project root:

```powershell
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp
python main_dual.py
```

**What this does:**
- ✅ Initializes ASTER Bot (AI-powered, ASTERUSDT)
- ✅ Initializes MOON Bot (rule-based, BTCUSDT)
- ✅ Starts FastAPI backend on `http://localhost:8000`
- ✅ Connects to Aster DEX API
- ✅ Begins trading loop (10-minute intervals)

**You should see:**
```
======================================================================
DUAL TRADING BOT SYSTEM
======================================================================
Bot 1: ASTERUSDT Vibe Trader (AI-driven)
Bot 2: BTCUSDT Moon Phase Trader (Lunar cycles)
Trading Mode: mainnet
Update Interval: 600s
======================================================================
ASTER Initializing ASTERUSDT Vibe Trader...
MOON Moon Phase Trader initialized for BTCUSDT (RULE-BASED - No OpenAI cost)
Starting both trading bots!
Starting Dashboard API on http://localhost:8000
```

**Keep this terminal open!** The bots will continue running.

---

### **Step 2: Start Dashboard Frontend**

Open a **new** PowerShell window:

```powershell
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp\dashboard
npm run dev
```

**What this does:**
- ✅ Starts Vite dev server
- ✅ Serves React dashboard on `http://localhost:3000`
- ✅ Connects to backend API at port 8000

**You should see:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**Keep this terminal open too!**

---

### **Step 3: Access Dashboard**

Open your browser and navigate to:

```
http://localhost:3000
```

**You should see:**
- 🟢 "Online" indicator (top right)
- 📊 Portfolio summary banner (total value, PNL, exposure)
- 🟦 ASTER Bot section (left column)
- 🟪 MOON Bot section (right column)
- 📈 Charts, positions, and AI decisions

---

## 🔍 Verification Checklist

### ✅ Backend API Running
```powershell
# Test the API status endpoint
Invoke-RestRequest http://localhost:8000/api/status
```

**Expected response:**
```json
{
  "status": "running",
  "bots": {
    "aster": "active",
    "moon": "active"
  }
}
```

### ✅ Dashboard Frontend Running
```powershell
# Check if port 3000 is listening
netstat -ano | Select-String -Pattern "3000.*LISTENING"
```

**Expected output:**
```
TCP    [::1]:3000    [::]:0    LISTENING    <PID>
```

### ✅ Bots Trading
Check the Python terminal for activity:
- Every 10 minutes, you should see market data fetching
- AI decisions logged to `logs/decisions.json`
- Moon phase calculations logged to `logs/moon_decisions_BTCUSDT.json`

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│               Browser (localhost:3000)          │
│                   Dashboard UI                  │
└────────────────────┬────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────┐
│         FastAPI Backend (localhost:8000)        │
│                                                 │
│  Endpoints:                                     │
│  - /api/status                                  │
│  - /api/balance                                 │
│  - /api/positions                               │
│  - /api/decisions                               │
│  - /api/trades                                  │
│  - /api/performance                             │
│  - /api/portfolio/summary                       │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────────┐   ┌───────────────────┐
│   ASTER Bot       │   │    MOON Bot       │
│   (AI-Powered)    │   │   (Rule-Based)    │
├───────────────────┤   ├───────────────────┤
│ Symbol: ASTERUSDT │   │ Symbol: BTCUSDT   │
│ Interval: 10 min  │   │ Interval: 10 min  │
│ Uses: GPT-4       │   │ Uses: Pure Math   │
│ Cost: ~$5/day     │   │ Cost: $0/day      │
└─────────┬─────────┘   └─────────┬─────────┘
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │   Aster DEX API       │
          │ (fapi.asterdex.com)   │
          └───────────────────────┘
```

---

## 📁 Important Files & Directories

### **Configuration**
```
.env                      # API keys, wallet addresses
config/config.py          # Bot settings (interval, leverage, etc.)
```

### **Trading Bots**
```
main_dual.py              # Launcher for both bots
agent/trader.py           # ASTER Bot (AI-powered)
agent/moon_trader.py      # MOON Bot (rule-based)
agent/llm_client.py       # OpenAI GPT-4 integration
```

### **Backend API**
```
dashboard_api/server.py   # FastAPI endpoints
api/aster_client.py       # Aster DEX API wrapper
```

### **Frontend Dashboard**
```
dashboard/src/App.jsx                 # Main dashboard component
dashboard/src/components/             # UI components
```

### **Logs & Data**
```
logs/vibe_trader.log                  # Bot activity logs
logs/decisions.json                   # ASTER Bot AI decisions
logs/moon_decisions_BTCUSDT.json      # MOON Bot decisions
```

---

## 🛠️ Troubleshooting

### **Dashboard shows "Offline"**

**Problem:** Frontend can't connect to backend API

**Solution:**
```powershell
# Check if backend is running
Invoke-RestMethod http://localhost:8000/api/status

# If not, restart bots:
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp
python main_dual.py
```

---

### **"No module named 'X'" error**

**Problem:** Missing Python dependencies

**Solution:**
```powershell
pip install -r requirements.txt
```

---

### **"Port 8000 already in use"**

**Problem:** Another process using port 8000

**Solution:**
```powershell
# Find the process
netstat -ano | Select-String -Pattern "8000.*LISTENING"

# Kill it (replace <PID> with the Process ID)
Stop-Process -Id <PID> -Force

# Restart bots
python main_dual.py
```

---

### **Dashboard shows no data**

**Problem:** Bots haven't made any trades yet

**Solution:**
- Wait 10 minutes for first trading cycle
- Check `logs/decisions.json` to see if AI is making decisions
- Verify wallet has sufficient USDC balance

---

### **"UnicodeEncodeError" in logs**

**Problem:** Emoji encoding on Windows

**Solution:** Already fixed! All emojis removed from log messages. If you still see this, update:
- `agent/trader.py`
- `agent/moon_trader.py`
- `main_dual.py`

Remove any emoji characters from `logger.info()` calls.

---

## 💰 Cost Management

### **Current Configuration:**
- **ASTER Bot**: 144 OpenAI calls/day (~$5/day)
- **MOON Bot**: 0 OpenAI calls/day ($0/day)
- **Total**: ~$5/day (~$151/month)

### **To Reduce Costs Further:**

Edit `config/config.py`:

```python
# Increase interval to 15 minutes (saves $1.50/day)
update_interval: int = 900

# Or 20 minutes (saves $2.50/day)
update_interval: int = 1200
```

**Trade-off:** Slower reaction to market changes

---

## 🔐 Security Notes

### **Never commit these files:**
```
.env                    # Contains private keys!
logs/                   # May contain sensitive data
*.log                   # May contain wallet addresses
```

### **Keep secure:**
- `ASTER_SIGNER_PRIVATE_KEY` - Used to sign API requests
- `OPENAI_API_KEY` - Costs money if leaked
- `ASTER_USER_ADDRESS` - Your trading wallet

---

## 📊 Monitoring Your Bots

### **Live Dashboard:**
- Open: `http://localhost:3000`
- Shows: Real-time positions, balance, PNL, AI decisions

### **Logs:**
```powershell
# Watch bot activity
Get-Content logs\vibe_trader.log -Wait -Tail 20

# View AI decisions
Get-Content logs\decisions.json | ConvertFrom-Json | Select-Object -Last 5

# View Moon decisions
Get-Content logs\moon_decisions_BTCUSDT.json | ConvertFrom-Json | Select-Object -Last 5
```

### **Aster DEX:**
- Live positions: https://fapi.asterdex.com/portfolio
- Trade history: Check "Orders" and "Trades" tabs
- Your trading wallet: `0x0CDCF4287070b99e28C2Ba318236bA82977111b4`

---

## 🔄 Stopping the System

### **Graceful Shutdown:**

1. **Stop Dashboard** (Terminal 2):
   - Press `Ctrl + C`
   - Or close the terminal window

2. **Stop Bots** (Terminal 1):
   - Press `Ctrl + C`
   - Wait for "Shutting down..." message
   - Positions remain open (will be managed on restart)

### **Emergency Stop All:**
```powershell
# Kill all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Kill all Node processes (dashboard)
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```

⚠️ **Warning:** This doesn't close your trading positions! Close positions manually on Aster DEX if needed.

---

## 🎯 What Happens When Running

### **Every 10 Minutes (ASTER Bot):**
1. ✅ Fetches ASTERUSDT market data (price, volume, 5-min candles)
2. ✅ Sends data to GPT-4 for technical analysis
3. ✅ Receives AI decision (long/short/hold/close)
4. ✅ Executes trade if confidence > 60%
5. ✅ Sets stop loss (-3%) and take profit (+5%)
6. ✅ Logs decision to `logs/decisions.json`

### **Every 10 Minutes (MOON Bot):**
1. ✅ Calculates current moon phase (mathematical)
2. ✅ Fetches BTCUSDT market data
3. ✅ Applies rule-based strategy:
   - Moon waning → LONG
   - Moon waxing → SHORT
   - Transition → HOLD
4. ✅ Executes trade if rules met
5. ✅ Sets stop loss (-2%) and take profit (+4%)
6. ✅ Logs decision to `logs/moon_decisions_BTCUSDT.json`

### **Dashboard Updates:**
- Fetches data from backend API every 5 seconds
- Updates positions, balance, PNL in real-time
- Shows AI reasoning and moon phase analysis

---

## 🚀 Quick Reference Commands

### **Start Everything:**
```powershell
# Terminal 1
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp
python main_dual.py

# Terminal 2
cd C:\Users\papa\Documents\coding_projects\crypto\aster\aster_vibe_comp\dashboard
npm run dev

# Browser
# Open: http://localhost:3000
```

### **Check Status:**
```powershell
# Backend API
Invoke-RestMethod http://localhost:8000/api/status

# Dashboard
Invoke-WebRequest http://localhost:3000 -UseBasicParsing

# Processes
Get-Process python, node
```

### **View Logs:**
```powershell
# Live log tail
Get-Content logs\vibe_trader.log -Wait -Tail 20

# Last 10 AI decisions
Get-Content logs\decisions.json | ConvertFrom-Json | Select-Object -Last 10 | Format-Table

# Moon phase decisions
Get-Content logs\moon_decisions_BTCUSDT.json | ConvertFrom-Json | Select-Object -Last 10
```

### **Clean Restart:**
```powershell
# Stop everything
Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force

# Clear cache
Remove-Item -Recurse -Force agent\__pycache__, api\__pycache__, utils\__pycache__ -ErrorAction SilentlyContinue

# Restart
python main_dual.py
```

---

## 📚 Additional Resources

- **Aster DEX Docs**: https://docs.asterdex.com
- **OpenAI API**: https://platform.openai.com
- **Your Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs (Swagger UI)

---

## 💡 Pro Tips

1. **Monitor costs**: Check OpenAI usage at https://platform.openai.com/usage
2. **Start small**: Test with small position sizes first ($1-5)
3. **Watch the logs**: Logs show AI reasoning - learn from them!
4. **Check moon phases**: Use `python scripts/check_moon.py`
5. **Test trades manually**: Use `python scripts/test_trade.py`
6. **Save decisions**: All AI decisions are saved - analyze them later!

---

## 🏆 You're All Set!

Your cost-optimized dual-strategy trading bot is now running:
- ✅ **ASTER Bot**: AI-powered technical analysis
- ✅ **MOON Bot**: Lunar cycle trading
- ✅ **Dashboard**: Beautiful real-time interface
- ✅ **Cost**: Under $5/day!

**Happy trading! May the moon and AI be with you! 🌙🤖**

---

*Last updated: October 22, 2025*  
*System optimized for Aster Trading Arena competition*






