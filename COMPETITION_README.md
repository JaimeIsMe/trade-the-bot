# Trade The Bot - AI-Powered Multi-Asset Trading System

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-blue)](https://tradethebot.com)
[![API](https://img.shields.io/badge/API-api.tradethebot.com-green)](https://api.tradethebot.com)

An autonomous AI trading system powered by **Qwen3 Flash** that trades cryptocurrency perpetuals across 5 major assets: BTC, ETH, SOL, BNB, and ASTER.

## 🌟 Features

- **Multi-Asset Trading**: Simultaneously manages 5 independent trading bots
- **AI-Powered Decisions**: Uses Qwen3 Flash for real-time market analysis and trade execution
- **Live Dashboard**: Real-time monitoring with neon-glowing UI
- **Risk Management**: Dynamic stop-loss, take-profit, and position sizing
- **Technical Analysis**: Multi-timeframe analysis with RSI, MACD, Bollinger Bands, ATR
- **WebSocket Integration**: Real-time updates for prices, trades, and AI decisions

## 🚀 Live Demo

- **Dashboard**: [https://tradethebot.com](https://tradethebot.com)
- **API**: [https://api.tradethebot.com](https://api.tradethebot.com)

## 🏗️ Architecture

```
┌─────────────────────┐
│   Frontend (React)  │  ← Hosted on DreamHost
│   tradethebot.com   │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│ Cloudflare Tunnel   │  ← Secure connection
│ api.tradethebot.com │
└──────────┬──────────┘
           │ Local
           ▼
┌─────────────────────┐
│  Backend (FastAPI)  │  ← Runs locally (API keys secure)
│    localhost:8000   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Trading Bots     │  ← AI decision-making
│   (Qwen3 Flash)     │
└─────────────────────┘
```

## 🤖 AI Trading Model

The system uses **Qwen3 Flash** by Alibaba Cloud for:
- **Ultra-fast inference**: Real-time market analysis
- **Multi-timeframe analysis**: 1m, 5m, 15m, 1h, 4h charts
- **Technical indicators**: RSI, MACD, Bollinger Bands, ATR, Volume
- **Risk assessment**: Dynamic position sizing and stop-loss calculation
- **Confidence scoring**: Self-reported confidence drives position sizes

### Trading Parameters
- **Leverage**: 5x default
- **Position Sizing**: 1-5% of account balance per trade
- **Risk/Reward**: Typically 1.5:1 to 3:1
- **Frequency**: Mid-to-low frequency (decisions every 2-3 minutes)

## 📊 Dashboard Features

- **Live Price Ticker**: Real-time crypto prices with neon glow effects
- **Performance Charts**: Cumulative P&L, individual trades, win rates
- **AI Decisions Log**: View bot reasoning and confidence scores
- **Multi-Bot Tabs**: Switch between 5 independent trading bots
- **Portfolio Summary**: Total balance, open P&L, positions
- **Info Pages**: Model details, asset information, trading methodology

## 🛠️ Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- Recharts
- Axios
- Lucide Icons

### Backend
- Python 3.11+
- FastAPI
- WebSockets
- aiohttp
- Uvicorn

### Infrastructure
- DreamHost (Frontend hosting)
- Cloudflare Tunnel (Secure API access)
- Aster DEX (Trading platform)

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Aster API credentials

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trade-the-bot.git
cd trade-the-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file
ASTER_API_KEY=your_api_key
ASTER_API_SECRET=your_api_secret
ASTER_API_URL=https://api.aster.finance
OPENAI_API_KEY=your_openai_key  # For Qwen3 Flash via OpenRouter
```

5. Run the backend:
```bash
python main_multi_bot.py
```

### Frontend Setup

1. Navigate to dashboard:
```bash
cd dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## 🚀 Deployment

### Backend with Cloudflare Tunnel

1. Install Cloudflare Tunnel:
```bash
cloudflared tunnel create tradethebot
```

2. Configure tunnel:
```yaml
# config.yml
tunnel: your-tunnel-id
credentials-file: /path/to/credentials.json

ingress:
  - hostname: api.tradethebot.com
    service: http://localhost:8000
  - service: http_status:404
```

3. Run tunnel:
```bash
cloudflared tunnel run tradethebot
```

### Frontend to DreamHost

1. Build the dashboard:
```bash
cd dashboard
npm run build
```

2. Upload `dist/` folder contents to DreamHost `public_html/`

3. Ensure `.htaccess` is uploaded for proper SPA routing

## 📈 Performance

- **Real-time updates**: WebSocket for sub-second latency
- **Cached responses**: 2-3 minute cache on backend
- **Rate limiting**: 6 requests/minute to prevent API bans
- **Optimized build**: ~687KB minified JS bundle

## 🔐 Security

- **API keys never leave local machine**
- **Cloudflare Tunnel** for secure backend access
- **No API keys in frontend code**
- **Environment variables** for sensitive data
- **CORS protection** on backend
- **Rate limiting** to prevent abuse

## 📝 Competition Entry

This project is submitted for the Aster Trading Competition. Key highlights:

- ✅ **Live deployment**: Publicly accessible at tradethebot.com
- ✅ **Multi-asset trading**: 5 independent bots
- ✅ **AI-powered**: Qwen3 Flash for decision-making
- ✅ **Real-time dashboard**: Live monitoring and visualization
- ✅ **Risk management**: Dynamic stop-loss and position sizing
- ✅ **Technical analysis**: Multi-timeframe with multiple indicators

## 🙏 Acknowledgments

- **Aster DEX** for the trading platform
- **Alibaba Cloud** for Qwen3 Flash
- **Cloudflare** for secure tunneling
- **DreamHost** for hosting

## 📄 License

MIT License - see LICENSE file for details

## 📧 Contact

- **Website**: [https://tradethebot.com](https://tradethebot.com)
- **API**: [https://api.tradethebot.com](https://api.tradethebot.com)

---

**⚠️ Disclaimer**: This is an experimental trading bot. Use at your own risk. Past performance does not guarantee future results. Never trade with money you cannot afford to lose.

