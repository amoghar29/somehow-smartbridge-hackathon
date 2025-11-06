# 🤖 Claude API Setup Guide

## Why Use Claude API?

Your app now uses **Claude API** instead of the local IBM Granite model because:
- ✅ **Instant responses** (1-2 seconds vs 20-30 minutes!)
- ✅ **Higher quality** financial advice
- ✅ **No memory issues** or disconnections
- ✅ **Works on any hardware** (no GPU needed)
- ✅ **Always up-to-date** model

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Anthropic Library

```bash
cd backend
pip install anthropic
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Get Your API Key

1. Go to: **https://console.anthropic.com/**
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **"Create Key"**
5. Copy your API key (starts with `sk-ant-...`)

**Free Tier:**
- $5 free credits when you sign up
- Enough for ~thousands of requests
- No credit card required to start

### Step 3: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Or create a `.env` file:**

Create `backend/.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### Step 4: Restart Backend

```bash
cd backend
python main.py
```

---

## ✅ Verify It's Working

1. Start the backend
2. Check logs for: `"Claude API client initialized successfully"`
3. Try a query in your app
4. You should see: `"Generating AI response using Claude API..."`
5. Response appears **in 1-2 seconds**!

---

## 📊 What Changed

### Before (Local Model):
- ⏳ 20-30 minutes per response
- 🔴 Backend disconnections
- 💾 5GB model in memory
- 🐌 CPU-only, very slow

### After (Claude API):
- ✅ 1-2 seconds per response
- ✅ Stable backend
- ✅ No local model needed
- 🚀 Fast on any hardware

---

## 💰 Cost & Limits

**Claude Sonnet 3.5 Pricing:**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Approximate costs for your app:**
- Chat query: ~$0.001 (0.1 cents)
- Goal planning: ~$0.002 (0.2 cents)
- Budget analysis: ~$0.002 (0.2 cents)

**Example:** 1000 queries = ~$1.50

**Free credits ($5) = ~3,000+ requests!**

---

## 🔧 Configuration Options

### Use a Different Model

Edit `backend/core/granite_service.py`, line 76:

```python
# Current (fastest, best)
model="claude-3-5-sonnet-20241022"

# Cheaper option
model="claude-3-haiku-20240307"  # Faster & cheaper

# Most capable
model="claude-3-opus-20240229"  # Slower but best quality
```

### Adjust Response Length

In your agent files, change `max_tokens`:

```python
# Shorter responses (cheaper, faster)
advice = generate(prompt, max_tokens=150, temperature=0.7)

# Longer responses
advice = generate(prompt, max_tokens=500, temperature=0.7)
```

### Disable API (Use Fallbacks Only)

Don't set `ANTHROPIC_API_KEY` - the app will automatically use smart fallback responses.

---

## 🛡️ Fallback System

Your app has **3 layers** of fallback:

1. **Claude API** (primary) - Instant, high-quality
2. **Smart contextual responses** - Instant, keyword-based
3. **Generic fallbacks** - Always available

If Claude API fails or is unavailable:
- ✅ App continues working
- ✅ Uses smart contextual responses
- ✅ No errors shown to user

---

## 📝 Environment Variables

Create `backend/.env` file with:

```bash
# Required for AI responses
ANTHROPIC_API_KEY=your-api-key-here

# Optional configuration
BACKEND_URL=http://localhost:8000
API_HOST=127.0.0.1
API_PORT=8000
```

---

## 🧪 Testing

Test the integration:

```bash
# Start backend
cd backend
python main.py

# In another terminal, test API
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"question": "How can I save money?", "persona": "professional"}'
```

Expected response in **1-2 seconds**!

---

## ⚠️ Troubleshooting

### "Claude API not initialized"

**Problem:** API key not set

**Solution:**
```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set it
export ANTHROPIC_API_KEY="your-key"
```

### "API call failed: Authentication error"

**Problem:** Invalid API key

**Solution:**
1. Verify key from console.anthropic.com
2. Check for extra spaces or quotes
3. Regenerate key if needed

### "Rate limit exceeded"

**Problem:** Too many requests

**Solution:**
- Wait a few minutes
- Implement request throttling
- Upgrade plan if needed

### Still Using Fallbacks

**Check logs for:**
```
Claude API not available, using smart fallback
```

**Means:** API key not set correctly

---

## 🔐 Security Best Practices

**Never commit API keys to Git:**

Add to `.gitignore`:
```
.env
*.env
**/.env
```

**For production:**
- Use environment variables
- Use secrets management (AWS Secrets Manager, etc.)
- Rotate keys regularly
- Monitor usage

---

## 📚 Additional Resources

- **Anthropic Console:** https://console.anthropic.com/
- **API Documentation:** https://docs.anthropic.com/
- **Python SDK:** https://github.com/anthropics/anthropic-sdk-python
- **Pricing:** https://www.anthropic.com/api

---

## 🎉 You're All Set!

Your Personal Finance Assistant now has:
- ⚡ **Instant AI responses** with Claude
- 🧠 **High-quality** financial advice
- 🔄 **Smart fallbacks** if API unavailable
- 💰 **Cost-effective** with free tier

**Start the backend and enjoy blazing-fast AI!** 🚀

---

## Quick Reference

```bash
# Install
pip install anthropic

# Set key (Windows PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-..."

# Set key (Linux/Mac)
export ANTHROPIC_API_KEY="sk-ant-..."

# Start backend
python backend/main.py

# Test
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "persona": "professional"}'
```

**Questions?** Check the logs or Anthropic docs!
