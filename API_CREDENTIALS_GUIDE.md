# API Credentials Setup Guide

## 🎯 Summary: What You Actually Need

### ✅ **REQUIRED** (System won't work without this):

- **Google API Key** - For Gemini LLM (the brain of the system)

### 🔧 **OPTIONAL** (System works great without these):

- **Google Drive Credentials** - Currently using mock responses
- **SerpAPI Key** - Currently using free DuckDuckGo

---

## 🔑 Required Setup

### Google API Key (Gemini LLM) - **ESSENTIAL**

**Why needed**: Powers the AI that generates intelligent responses
**Cost**: Free tier available (generous limits)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Edit `backend/.env`:
   ```
   GOOGLE_API_KEY=your_actual_key_here
   ```

---

## 🌐 Optional Enhancements

### 1. Real Google Drive Access (Optional)

**Current Status**: ✅ Working with mock responses
**Why optional**: System simulates Google Drive responses for demo

**To enable real Google Drive access:**

1. **Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**
3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Search "Google Drive API" → Enable
4. **Create Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: "Desktop application"
   - Name: "Agentic RAG Chatbot"
5. **Download JSON**:
   - Download the credentials file
   - Rename to `credentials.json`
   - Place in `backend/` folder

**First run**: Browser will open for Google OAuth consent

### 2. Enhanced Web Search (Optional)

**Current Status**: ✅ Working with DuckDuckGo (free)
**Why optional**: DuckDuckGo provides good results without API limits

**To enable SerpAPI (better results, more reliable):**

1. **Sign up**: https://serpapi.com/users/sign_up
2. **Get API Key**: Dashboard → API Key
3. **Add to `.env`**:
   ```
   SERPAPI_API_KEY=your_serpapi_key_here
   ```
4. **Update code** in `backend/agents/web_search_agent.py`:
   ```python
   # Uncomment these lines:
   from langchain_community.tools import SerpAPIWrapper
   search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERPAPI_API_KEY"))
   ```

---

## 💰 Cost Breakdown

### Free Tier Usage:

- **Google Gemini API**: 60 queries/minute, 1500/day (very generous)
- **DuckDuckGo**: Completely free, unlimited
- **Google Drive API**: 100 requests/100 seconds/user (sufficient for most use)

### Paid Options:

- **SerpAPI**: $50/month for 5000 searches (optional)
- **Google Gemini**: $0.001 per 1000 tokens after free tier

---

## 🚀 Quick Start Recommendation

**For immediate testing**: Just add Google API key (only required step)
**For production**: Add all credentials for full functionality

The system is designed to work excellently with just the Google API key!

---

## 🔍 How to Check What's Working

Run this command to see current status:

```bash
curl http://localhost:8001/health
```

Response shows which services are active:

```json
{
  "status": "healthy",
  "services": {
    "pdf_processing": "✓",
    "vector_store": "✓",
    "web_search": "✓",
    "google_drive_mcp": "✓",
    "speech_to_text": "✓"
  }
}
```

All services show ✓ even with mock Google Drive!
