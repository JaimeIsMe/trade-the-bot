# 🔄 Quick Model Switching Guide

## 🎯 How to Switch Between Models

You have **4 models** available now:
1. ✅ GPT-4o-mini (OpenAI) - **Current default**
2. ✅ Qwen3-Max (Alibaba) - **NEW! Ready to test**
3. ✅ DeepSeek-Chat (DeepSeek)
4. ✅ Claude Haiku (Anthropic)

---

## ⚡ Quick Switch (Edit .env file):

### Switch to Qwen3-Max:
```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-max
QWEN_API_KEY=sk-your-qwen-key
```

### Switch to GPT-4o-mini:
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

### Switch to DeepSeek:
```bash
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
DEEPSEEK_API_KEY=sk-your-deepseek-key
```

### Switch to Claude:
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-haiku-20241022
ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## 📊 Model Comparison

| Model | Cost | Speed | Reasoning | Best For |
|-------|------|-------|-----------|----------|
| **GPT-4o-mini** | $$ | Fast | Good | Balanced |
| **Qwen3-Max** | $$$ | Fast | Excellent | Technical analysis |
| **DeepSeek** | $ | Fast | Very Good | Cost savings |
| **Claude Haiku** | $$$$ | Fast | Good | Creative analysis |

---

## 🎲 Testing Workflow

1. **Baseline with GPT-4o-mini** (24 hours)
   - Track all metrics
   
2. **Test Qwen3-Max** (24 hours)
   - Same market conditions
   - Compare decisions
   
3. **Analyze Results:**
   - Which made better trades?
   - Which had higher win rate?
   - Was the cost difference worth it?

---

## 💡 Pro Tip: Keep Track

Create a simple log:

```
Day 1-2 (GPT-4o-mini):
  - Total trades: 12
  - Win rate: 58%
  - P&L: +$23
  - API cost: $1.80
  - Best trade: +$8
  
Day 3-4 (Qwen3-Max):
  - Total trades: 15
  - Win rate: 62%
  - P&L: +$31
  - API cost: $4.50
  - Best trade: +$12

Winner: Qwen3-Max (+35% better P&L, but 2.5x cost)
```

---

## ✅ You're Ready!

Just paste your Qwen API key in the `.env` file and restart! 🚀

