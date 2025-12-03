# Setting Up OpenAI API Key for Query Expansion

## Quick Setup

1. **Get your OpenAI API key:**
   - Visit: https://platform.openai.com/api-keys
   - Sign in or create an account
   - Click "Create new secret key"
   - Copy the key (it starts with `sk-...`)

2. **Create a `.env` file** in the project root with your key:
   ```bash
   echo 'OPENAI_API_KEY=sk-your-actual-key-here' > .env
   ```

3. **Restart the server** to apply changes:
   ```bash
   # Kill the existing server
   lsof -ti :8000 | xargs kill -9
   
   # Start with your data
   python -m app.app --data-path output_feeds_backup.parquet
   ```

## Optional Configuration

You can add these to your `.env` file:

```bash
# Use a different model
OPENAI_MODEL=gpt-4

# Use a different API endpoint (for OpenRouter, etc.)
OPENAI_API_BASE=https://api.openai.com/v1

# Adjust query expansion settings (optional, defaults shown)
NUM_EXPANDED_QUERIES=3
ORIGINAL_QUERY_WEIGHT=0.4
EXPANDED_QUERY_WEIGHT=0.15
```

## Current Status

Your server is running at: http://127.0.0.1:8000/

- Query expansion is ENABLED
- Currently using template-based fallback (generic expansions)
- Once you add your API key, it will use ChatGPT for smarter query expansion

## Testing

After setting up your API key, search for something like "python" and click on the "Query Expansion Active" section to see the AI-generated alternative queries.






