# Pinecone Setup Guide

## Step 1: Create Pinecone Account

1. **Go to Pinecone:** https://www.pinecone.io/
2. **Sign up** for a free account
3. **Verify your email** and complete setup

## Step 2: Create an Index

1. **Login to Pinecone Console:** https://app.pinecone.io/
2. **Click "Create Index"**
3. **Configure your index:**

   - **Index Name:** `asu-agent` (or match your .env file)
   - **Dimensions:** `768` (for Gemini embeddings)
   - **Metric:** `cosine`
   - **Cloud Provider:** `AWS` (free tier)
   - **Region:** `us-east-1` (free tier)

4. **Click "Create Index"**

## Step 3: Get API Key

1. **Go to API Keys** in Pinecone console
2. **Click "Create API Key"**
3. **Copy the API key**
4. **Update your `.env` file:**
   ```
   PINECONE_API_KEY=your-actual-api-key-here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=asu-agent
   ```

## Step 4: Test Connection

### Option A: Use Test Endpoints (Recommended)

1. **Start your server:** `python main.py`
2. **Test Pinecone status:**
   ```
   GET http://localhost:8000/test/pinecone/info
   ```
3. **Test embeddings:**
   ```
   GET http://localhost:8000/test/embeddings/status
   ```

### Option B: Use Test Script

```bash
cd Hackathon2709/backend
python -c "
from services.embeddings import EmbeddingService
import asyncio

async def test():
    service = EmbeddingService()
    if service.index:
        print('✅ Pinecone connected!')
        stats = service.index.describe_index_stats()
        print(f'Index: {stats}')
    else:
        print('❌ Pinecone not connected - using test mode')

asyncio.run(test())
"
```

## Step 5: Verify Setup

### Expected Results:

**✅ Success:**

```json
{
  "status": "connected",
  "index_name": "asu-agent",
  "total_vectors": 0,
  "dimension": 768
}
```

**❌ Test Mode (needs setup):**

```json
{
  "status": "test_mode",
  "message": "Pinecone not connected - using test storage",
  "setup_required": true
}
```

## Troubleshooting

### Common Issues:

1. **"Invalid API key"**

   - Check your API key in `.env`
   - Make sure no extra spaces or quotes

2. **"Index not found"**

   - Verify index name matches `.env` file
   - Check index was created successfully

3. **"Wrong dimensions"**

   - Index dimension must be `768` for Gemini embeddings
   - Delete and recreate index if wrong dimension

4. **"Region mismatch"**
   - Ensure `PINECONE_ENVIRONMENT` matches your index region
   - Free tier is usually `us-east-1`

### Debug Commands:

```bash
# Check environment variables
python -c "from config import settings; print(f'API Key: {settings.pinecone_api_key[:10]}...'); print(f'Environment: {settings.pinecone_environment}'); print(f'Index: {settings.pinecone_index_name}')"

# Test Pinecone connection
python -c "import pinecone; pinecone.init(api_key='your-key', environment='us-east-1'); print(pinecone.list_indexes())"
```

## Free Tier Limits

- **1 Index** maximum
- **100K vectors** maximum
- **768 dimensions** maximum
- **5MB storage** maximum

Perfect for development and testing!

## Production Considerations

- **Paid plans** for more indexes and storage
- **Different regions** for better performance
- **Backup strategies** for important data
- **Monitoring** for usage and performance
