# 🚀 Qwen-Flash (Qwen-Turbo) Setup

## ✅ What is Qwen-Flash?

**Qwen-Flash** (also called Qwen-Turbo) is:
- ✅ **Faster** than Qwen-Max
- ✅ **Cheaper** than Qwen-Max (~60% cost savings)
- ✅ **Better** than old Qwen-Turbo (replaced it)
- ✅ Still very capable for trading decisions

---

## 💰 Cost Comparison:

| Model | Input | Output | Est. Monthly Cost |
|-------|-------|--------|-------------------|
| **Qwen-Flash** | $0.04 | $0.12 | **~$7/month** 🎯 |
| Qwen-Max | $0.40 | $1.20 | ~$68/month |
| DeepSeek | $0.14 | $0.28 | ~$19/month |
| GPT-4o-mini | $0.15 | $0.60 | ~$27/month |

**Qwen-Flash is THE CHEAPEST option!** 💰

---

## 🔧 How to Switch to Qwen-Flash:

### Update Your `.env` File:

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
QWEN_API_KEY=sk-your-existing-qwen-key
```

**Note:** The model identifier is `qwen-turbo` (this is Qwen-Flash)

### Then Restart:

```bash
python main.py
```

---

## 📊 What to Expect:

### Qwen-Flash vs Qwen-Max:
- **Speed:** Faster responses ✅
- **Cost:** ~90% cheaper ✅
- **Quality:** Slightly lower but still very good
- **Trading:** Should still trade aggressively like Qwen-Max

### Free Tier with Qwen-Flash:
```
1M free tokens / ~2,500 tokens per decision = 400 decisions
400 decisions / 60 per hour = ~6.5 hours free

After that: Only $7/month! 🎉
```

---

## 🎯 Ready to Switch!

Your Qwen API key works for both Qwen-Max and Qwen-Flash - just change the model name!

**Want me to switch you to Qwen-Flash now?**

