# Troubleshooting Guide - Model Download Issues

## Issue: Model Download Failed (Connection Interrupted)

You encountered: `ChunkedEncodingError: Connection broken: IncompleteRead`

This happens when downloading the large IBM Granite model (~5GB) and the connection drops.

## Solution 1: Clean Up and Retry (Recommended)

### Step 1: Delete Incomplete Download

The incomplete download is in your cache. Delete it:

**Windows:**
```bash
# Delete the model cache
rmdir /s /q model_cache
# Or manually delete: D:\somehow-smartbridge-hackathon\backend\model_cache\
```

**Important:** The incomplete files must be deleted or the download won't retry.

### Step 2: Start Server

The server will now start WITHOUT trying to load the model:

```bash
python main.py
```

The model will only load when you make your first AI request.

### Step 3: Make First AI Request

- Go to http://127.0.0.1:8000/docs
- Try the `/ai/generate` endpoint
- The model will download now (may take 10-20 minutes)
- If it fails again, try Solution 2

## Solution 2: Use a Smaller Model (Faster)

If your connection keeps dropping, use a smaller model:

### Update config/settings.py:

```python
# Change this line:
MODEL_ID = "ibm-granite/granite-3.0-2b-instruct"

# To one of these smaller alternatives:
MODEL_ID = "distilgpt2"  # ~350MB - Fast but basic
# OR
MODEL_ID = "gpt2"  # ~500MB - Better quality
# OR
MODEL_ID = "microsoft/phi-2"  # ~2.7GB - Good balance
```

Then restart the server.

## Solution 3: Manual Download with Resume Support

Use `huggingface-cli` which supports resume:

```bash
# Install huggingface-cli
pip install huggingface-hub[cli]

# Download with resume support
huggingface-cli download ibm-granite/granite-3.0-2b-instruct --cache-dir ./model_cache --resume-download

# This will resume if interrupted
```

Then restart your server.

## Solution 4: Download Overnight

For slow/unstable connections:

1. Leave the download running overnight
2. Check in the morning
3. If it failed, delete cache and retry

## Verification

After successful download, check:

```bash
# Should see ~5GB of files
dir model_cache /s

# Or check the API
curl http://127.0.0.1:8000/health
```

Should show: `"model_loaded": true`

## Quick Reference

| Model | Size | Download Time | Quality |
|-------|------|---------------|---------|
| distilgpt2 | 350MB | 2-5 min | Basic |
| gpt2 | 500MB | 3-7 min | Good |
| phi-2 | 2.7GB | 10-30 min | Better |
| granite-3.0-2b | 5GB | 20-60 min | Best |

## Still Having Issues?

1. Check your internet connection stability
2. Try using mobile hotspot (sometimes more stable)
3. Use smaller model for development
4. Download at off-peak hours
5. Check if firewall is blocking
