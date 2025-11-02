# 🚀 Bot 2 (DeepSeek) Quick Setup

## When You Return with Credentials:

### 1. Add These Lines to Your `.env` File:

```bash
# ═══════════════════════════════════════════════════════════════
# BOT 2: DeepSeek Configuration
# ═══════════════════════════════════════════════════════════════
BOT2_ENABLED=true

# Your NEW wallet credentials for Bot 2:
BOT2_USER_ADDRESS=<paste_here>
BOT2_SIGNER_ADDRESS=<paste_here>
BOT2_PRIVATE_KEY=<paste_here>

# DeepSeek API key:
DEEPSEEK_API_KEY=<paste_here>

# Bot 2 Trading Settings:
BOT2_SYMBOL=ASTERUSDT
BOT2_STRATEGY=contrarian
```

### 2. Run Multi-Bot System:

```bash
python main_multi_bot.py
```

### 3. What You'll See:

```
════════════════════════════════════════════════════════════
MULTI-BOT TRADING SYSTEM - 2 Bots Active
════════════════════════════════════════════════════════════
  • GPT4o: ASTERUSDT via openai (aggressive)
  • DEEPSEEK: ASTERUSDT via deepseek (contrarian)
════════════════════════════════════════════════════════════

[GPT4o] 🚀 Aggressive Vibe Trader initialized
[DEEPSEEK] 🚀 Aggressive Vibe Trader initialized

[GPT4o] Set leverage to 5x for ASTERUSDT
[DEEPSEEK] Set leverage to 5x for ASTERUSDT

[GPT4o] Analyzing market... (looking for trends)
[DEEPSEEK] Analyzing market... (looking for reversals)
```

---

## 🎯 Strategy Differences:

### Bot 1 (GPT-4o-mini - Aggressive):
- Trades WITH trends
- Multi-timeframe alignment
- Larger positions on conviction
- Holds for bigger moves

### Bot 2 (DeepSeek - Contrarian):
- Trades AGAINST extremes
- RSI <30 = LONG, RSI >70 = SHORT
- Quick scalps
- Fades overbought/oversold

**Result:** Natural hedge! When market trends, Bot 1 wins. When market reverses, Bot 2 wins.

---

## 💰 Separate Wallets = Separate Risk

Each bot trades independently:
- Bot 1: $104 wallet → Max $80 position
- Bot 2: Your new wallet → Max $80 position

**Total capital at risk:** Both wallets combined

---

## 📊 Comparing Performance

After 24 hours, you can compare:

```python
# Bot 1 (GPT-4o-mini):
Win Rate: 55%
Avg R/R: 2.3:1
Total Trades: 18
P&L: +$42

# Bot 2 (DeepSeek):
Win Rate: 48%
Avg R/R: 2.8:1
Total Trades: 24
P&L: +$56
```

See which strategy performs better! 📈

---

## 🛠️ I'm Ready When You Are!

Just paste:
1. ✅ Bot 2 User Address
2. ✅ Bot 2 Signer Address
3. ✅ Bot 2 Private Key
4. ✅ DeepSeek API Key

And I'll help you configure and launch! 🚀

