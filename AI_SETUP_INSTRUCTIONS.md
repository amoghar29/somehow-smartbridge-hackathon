# AI Setup Instructions - Enable Real AI Responses

## Issue: Seeing Warning Messages Instead of AI Responses?

If you're seeing messages like "⚠️ AI Model not available" when clicking AI buttons, it means the Claude API key is not configured.

## Quick Fix - Enable Real AI Responses

### Step 1: Get Your Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create Key"**
5. Copy your API key (starts with `sk-ant-...`)

### Step 2: Set the Environment Variable

#### **Windows (Command Prompt)**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
python backend/main.py
```

#### **Windows (PowerShell)**
```powershell
$env:ANTHROPIC_API_KEY="your-api-key-here"
python backend/main.py
```

#### **Linux/Mac**
```bash
export ANTHROPIC_API_KEY=your-api-key-here
python backend/main.py
```

#### **Permanent Setup (Recommended)**

Create a `.env` file in the backend directory:
```bash
# backend/.env
ANTHROPIC_API_KEY=your-api-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

### Step 3: Restart the Backend

After setting the API key, restart your backend server:
```bash
cd backend
python main.py
```

### Step 4: Verify It's Working

1. Go to http://localhost:8000/health in your browser
2. You should see `"model_loaded": true` in the response
3. Try the AI features in the frontend - they should now show real AI responses!

---

## What Changed?

### Before (Hardcoded Responses)
- Backend was falling back to hardcoded responses based on keywords
- Responses looked generic and didn't adapt to your specific situation

### Now (Real AI)
- Uses Claude API for intelligent, contextual responses
- Personalized advice based on your income, expenses, and risk profile
- Supports three personas: conservative, professional, aggressive
- Longer, more detailed responses (up to 500 tokens)

---

## Testing the AI Features

Once configured, test these features:

1. **Budget Analysis** (`/pages/2_💰_Budget.py`)
   - Enter your income and expenses
   - Click "🤖 Get AI Budget Analysis"
   - You'll see personalized budget optimization advice

2. **Tax Planning** (`/pages/4_💳_Tax_Planner.py`)
   - Enter your annual income and deductions
   - Click "🤖 Get AI Tax-Saving Recommendations"
   - Get specific tax-saving strategies for Indian tax laws

3. **AI Chat** (`/pages/3_🤖_AI_Chat.py`)
   - Ask any financial question in the chat
   - Select your financial profile for personalized advice
   - Get instant responses powered by Claude AI

4. **AI Assistant** (`/pages/4_🤖_AI_Assistant.py`)
   - Chat interface with topic context
   - Learning center resources
   - FAQ section

---

## Troubleshooting

### "AI Model not available" Warning
- Make sure you set the ANTHROPIC_API_KEY environment variable
- Restart the backend after setting the variable
- Check the backend console for error messages

### "Request timed out" Error
- The API might be slow on first request
- Wait a moment and try again
- Check your internet connection

### API Key Not Working
- Verify the key is correct (should start with `sk-ant-`)
- Make sure you have credits in your Anthropic account
- Check if the key has the right permissions

---

## API Usage & Costs

- **Model Used**: `claude-haiku-4-5-20251001` (fast and cost-effective)
- **Max Tokens**: 500 per response
- **Approximate Cost**: ~$0.01 per 20-30 AI interactions
- **Response Cache**: Enabled to reduce redundant API calls

The app uses a response cache to avoid making duplicate API calls for the same questions, saving both time and cost!

---

## Need Help?

If you're still having issues:
1. Check the backend console for detailed error logs
2. Verify your API key is valid at https://console.anthropic.com/
3. Make sure the backend is running on http://localhost:8000

**Backend Console Output Should Show:**
```
INFO: Claude API client initialized successfully
INFO: AI model will be loaded on first request
```

Happy Financial Planning! 💰🤖
