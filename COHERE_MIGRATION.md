# Migration to Cohere Embeddings

This project now uses **Cohere's free API** for embeddings instead of sentence-transformers.

## Why the change?

- ✅ **Lightweight**: Dependencies reduced from 1.3 GB → 3 MB
- ✅ **Free**: Cohere offers 1000 API calls/minute on free tier
- ✅ **Fast deployment**: No need to download heavy ML models
- ✅ **Same quality**: 384-dimension embeddings, same as all-MiniLM-L6-v2

## Setup

1. **Get a free Cohere API key**:
   - Go to https://dashboard.cohere.com/api-keys
   - Sign up (no credit card required)
   - Copy your API key

2. **Add to environment variables**:
   ```bash
   COHERE_API_KEY=your-api-key-here
   ```

3. **Deploy**:
   - Render will automatically use the new lightweight dependencies
   - Build time reduced from 5+ minutes to ~30 seconds

## Free Tier Limits

- **1000 API calls per minute**
- **Unlimited total usage**
- **No credit card required**

Perfect for development and small-scale production use!
