# Query Expansion Setup Guide

Query expansion uses an LLM to generate alternative search queries, making results more serendipitous and comprehensive.

## Quick Start

The query expansion system tries multiple LLM backends in order:
1. **Ollama** (local, free) - tried first
2. **OpenAI** (or compatible API) - tried if Ollama unavailable
3. **Fallback** (simple templates) - used if no LLM available

## Option 1: Ollama (Recommended - Free & Local)

### Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### Start Ollama and Pull a Model

```bash
# Start Ollama service (runs in background)
ollama serve

# In another terminal, pull a model
ollama pull llama3.2

# Or use a smaller/faster model
ollama pull llama3.2:1b
```

### Test It
```bash
cd /Users/harsh/development/CC/hearch
python -m src.microsearch.query_expansion
```

**That's it!** Ollama will be auto-detected and used.

### Optional: Configure Different Model
```bash
export OLLAMA_MODEL=llama3.2:1b  # Use smaller model
export OLLAMA_URL=http://localhost:11434/api/generate  # Custom URL
```

## Option 2: OpenAI API (or OpenRouter)

### Using OpenAI
```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-3.5-turbo"  # or gpt-4, gpt-4o-mini, etc.
```

### Using OpenRouter (Access to Many Models)
```bash
export OPENAI_API_KEY="your-openrouter-key"
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
export OPENAI_MODEL="meta-llama/llama-3.2-3b-instruct:free"  # Free model
```

Get an OpenRouter key at: https://openrouter.ai/

## Configuration

Edit `app/app.py` to configure query expansion:

```python
# Configuration
ENABLE_QUERY_EXPANSION = True  # Set to False to disable
NUM_EXPANDED_QUERIES = 4  # Number of alternative queries (default: 4)
ORIGINAL_QUERY_WEIGHT = 0.40  # Weight for original query (40%)
EXPANDED_QUERY_WEIGHT = 0.15  # Weight per expanded query (15% each)
```

## How It Works

1. **User searches:** "potatoes"
2. **LLM generates alternatives:**
   - "how to make potato salad"
   - "best potato recipes"
   - "potato nutrition facts"
   - "growing potatoes at home"
3. **System searches all 5 queries** (original + 4 expansions)
4. **Results are combined with weights:**
   - Original query: 40%
   - Each expanded query: 15%
5. **Top 10 combined results are displayed**

## Testing Query Expansion

Test the query expansion module directly:

```bash
cd /Users/harsh/development/CC/hearch
python -m src.microsearch.query_expansion
```

Or test with a custom query:

```python
from microsearch.query_expansion import expand_query

expansions = expand_query("artificial intelligence", num_expansions=5)
print(expansions)
```

## Troubleshooting

### "Query expansion failed"
- Check if Ollama is running: `ollama list`
- Check if API keys are set: `echo $OPENAI_API_KEY`
- System will fallback to simple template-based expansion

### Slow Response
- Use a smaller Ollama model: `llama3.2:1b`
- Reduce `NUM_EXPANDED_QUERIES` in config
- Set `ENABLE_QUERY_EXPANSION = False` to disable

### No Ollama Models
```bash
ollama pull llama3.2:1b  # Fast, small model (1.3GB)
ollama pull llama3.2     # Better quality (2GB)
```

## Performance Tips

- **Fast:** Use `llama3.2:1b` with Ollama (responses in ~1-2 seconds)
- **Quality:** Use `llama3.2` or `gpt-3.5-turbo` (responses in ~3-5 seconds)
- **Free:** Ollama is completely free and runs locally
- **Disable if needed:** Set `ENABLE_QUERY_EXPANSION = False` in app.py






