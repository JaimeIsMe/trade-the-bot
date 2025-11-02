# 🚀 Qwen3-Max Testing Guide

## ✅ Qwen3-Max Support Added!

You can now test **Qwen3-Max** against **GPT-4o-mini** to compare performance!

---

## 🔧 How to Switch to Qwen3-Max

### Step 1: Update Your `.env` File

Add these lines (or modify existing ones):

```bash
# === QWEN3-MAX CONFIGURATION ===
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
QWEN_API_KEY=sk-your-qwen-api-key-here
```

### Step 2: Restart the Trader

```bash
python main.py
```

That's it! Your bot will now use Qwen3-Max for trading decisions! 🎉

---

## 🔄 How to Switch Back to GPT-4o-mini

Simply update your `.env`:

```bash
# === BACK TO GPT-4O-MINI ===
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
# QWEN_API_KEY stays in .env (just not used)
```

Then restart:

```bash
python main.py
```

---

## 📊 Comparison Testing Strategy

### Method 1: Sequential Testing (Recommended)

**Day 1-2: GPT-4o-mini**
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```
Run for 24-48 hours, track:
- Total trades
- Win rate
- Avg P&L per trade
- Best/worst trades
- Total API cost

**Day 3-4: Qwen3-Max**
```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
```
Run for 24-48 hours, track same metrics

**Day 5: Compare Results**

---

## 💰 Expected Cost Comparison

### Qwen3-Max Pricing (Alibaba Cloud DashScope):
- Input: ~$0.40 per 1M tokens
- Output: ~$1.20 per 1M tokens

### GPT-4o-mini Pricing:
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Cost Difference:**
- Qwen3-Max: ~2.5x MORE expensive than GPT-4o-mini
- BUT: May have better reasoning/performance

### Monthly Cost Estimate (60-second intervals):

**GPT-4o-mini:**
- ~$27/month

**Qwen3-Max:**
- ~$68/month (2.5x more)

**Trade-off:** Higher cost, potentially better decisions

---

## 🎯 What to Compare:

| Metric | GPT-4o-mini | Qwen3-Max | Winner |
|--------|-------------|-----------|---------|
| **Win Rate** | __%  | __%  | ? |
| **Avg Win** | +__% | +__% | ? |
| **Total Trades** | __ | __ | ? |
| **P&L** | $__ | $__ | ? |
| **API Cost** | $27 | $68 | GPT-4o |
| **Response Speed** | __ ms | __ ms | ? |

---

## 🧠 Why Test Qwen3-Max?

**Qwen3-Max Strengths:**
- ✅ Strong reasoning capabilities
- ✅ Good at mathematical analysis
- ✅ Multilingual (if needed)
- ✅ Large context (128K+)
- ✅ Recent model (cutting edge)

**Potential Edge:**
- Better technical analysis interpretation
- More nuanced risk assessment
- Improved pattern recognition
- Superior multi-timeframe synthesis

---

## 📝 Quick Switch Commands

### Switch to Qwen:
```bash
# In .env file:
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
```

### Switch to GPT-4o-mini:
```bash
# In .env file:
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Switch to DeepSeek (if you want):
```bash
# In .env file:
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
```

---

## 🚀 Ready to Test!

Once you provide your Qwen API key, you can:
1. ✅ Add it to `.env`
2. ✅ Set `LLM_PROVIDER=qwen`
3. ✅ Set `LLM_MODEL=qwen-max`
4. ✅ Restart: `python main.py`
5. ✅ Monitor for 24-48 hours
6. ✅ Compare vs GPT-4o-mini baseline

**Want me to help you configure it now?** Just paste your Qwen API key! 🎯

