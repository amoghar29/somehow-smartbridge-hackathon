# ⚡ Quick Start with Claude API

## 🎯 Your app now uses Claude API for instant AI responses!

---

## 📦 Step 1: Install Anthropic

```bash
pip install anthropic
```

---

## 🔑 Step 2: Get API Key

1. Visit: **https://console.anthropic.com/**
2. Sign up (free $5 credits!)
3. Go to **API Keys**
4. **Create Key**
5. Copy the key (starts with `sk-ant-...`)

---

## ⚙️ Step 3: Set Environment Variable

**PowerShell (Windows):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Or create `.env` file:**

Create `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## 🚀 Step 4: Start Backend

```bash
cd backend
python main.py
```

Look for: `"Claude API client initialized successfully"`

---

## ✨ That's It!

Your AI responses now take **1-2 seconds** instead of 20+ minutes!

### What You Get:
- ✅ Instant responses (1-2 seconds)
- ✅ High-quality financial advice
- ✅ Stable backend (no disconnections)
- ✅ Works on any hardware

### If No API Key:
- ✅ App still works!
- ✅ Uses smart fallback responses
- ✅ No errors

---

## 📊 Test It:

1. Open frontend
2. Ask a question in chat
3. Get instant response!

---

**See `CLAUDE_API_SETUP.md` for detailed instructions!**
