# Ollama Setup Guide for Local Embeddings

## Why Ollama?

- ✅ **Free & Unlimited** - No API quotas or costs
- ✅ **Private** - All processing happens locally
- ✅ **Fast** - No network latency
- ✅ **Reliable** - No external dependencies

## Step 1: Install Ollama

### macOS:

```bash
# Download and install from website
curl -fsSL https://ollama.com/install.sh | sh

# Or using Homebrew
brew install ollama
```

### Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows:

Download from: https://ollama.com/download/windows

## Step 2: Start Ollama Service

```bash
# Start Ollama (runs on localhost:11434)
ollama serve
```

Keep this terminal open - Ollama needs to run in the background.

## Step 3: Pull the Embedding Model

```bash
# Pull the nomic-embed-text model (best for embeddings)
ollama pull nomic-embed-text

# Alternative models you can try:
# ollama pull all-minilm        # Smaller, faster
# ollama pull mxbai-embed-large # Larger, more accurate
```

## Step 4: Test Ollama

```bash
# Test if Ollama is working
curl http://localhost:11434/api/tags

# Test embedding generation
curl http://localhost:11434/api/embeddings \
  -d '{
    "model": "nomic-embed-text",
    "prompt": "Hello world"
  }'
```

## Step 5: Configure Your Backend

Your `.env` file should have:

```
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text
```

## Step 6: Test Integration

```bash
cd Hackathon2709/backend
python test_ollama.py
```

## Model Comparison

| Model             | Size  | Dimension | Speed   | Quality |
| ----------------- | ----- | --------- | ------- | ------- |
| nomic-embed-text  | 274MB | 768       | Fast    | High    |
| all-minilm        | 133MB | 384       | Fastest | Good    |
| mxbai-embed-large | 669MB | 1024      | Slower  | Highest |

**Recommended: nomic-embed-text** (best balance of speed and quality)

## Troubleshooting

### "Connection refused"

- Make sure `ollama serve` is running
- Check if port 11434 is available
- Try: `lsof -i :11434`

### "Model not found"

- Run: `ollama list` to see installed models
- Pull the model: `ollama pull nomic-embed-text`

### "Slow performance"

- Ollama uses CPU by default
- For GPU acceleration, ensure you have compatible hardware
- Check: `ollama ps` to see running models

### Memory Issues

- Ollama loads models into RAM
- nomic-embed-text needs ~1GB RAM
- Close other applications if needed

## Performance Tips

### 1. Keep Model Loaded

```bash
# Pre-load model to avoid startup delay
curl http://localhost:11434/api/embeddings \
  -d '{"model": "nomic-embed-text", "prompt": "warmup"}'
```

### 2. Batch Processing

The embedding service automatically batches requests for efficiency.

### 3. Monitor Resources

```bash
# Check Ollama status
ollama ps

# Check system resources
htop
```

## Production Deployment

### Docker Setup

```dockerfile
FROM ollama/ollama

# Pull model during build
RUN ollama serve & sleep 5 && ollama pull nomic-embed-text

EXPOSE 11434
CMD ["ollama", "serve"]
```

### Systemd Service (Linux)

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target
```

## Switching Between Providers

You can easily switch between Ollama and Gemini:

### Use Ollama (Local, Free):

```bash
# In .env
EMBEDDING_PROVIDER=ollama
```

### Use Gemini (Cloud, Paid):

```bash
# In .env
EMBEDDING_PROVIDER=gemini
```

The system automatically detects and uses the configured provider!

## Next Steps

1. **Test Ollama setup:** `python test_ollama.py`
2. **Start your backend:** `python main.py`
3. **Test embeddings:** Use Postman collection
4. **Upload PDFs and generate quizzes** - now with unlimited embeddings!

Your PDF Quiz System now has unlimited, free, local embeddings! 🎉
