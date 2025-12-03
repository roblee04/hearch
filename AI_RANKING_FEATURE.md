# 🤖 AI-Powered Result Ranking

## Overview

Your search engine now uses ChatGPT to intelligently rank search results by "interestingness" and relevance! This feature analyzes the content, titles, and metadata of search results to surface the most engaging and valuable content for users.

## Features

### 1. **Intelligent Content Curation**
- ChatGPT analyzes each search result's title, content snippet, and metadata
- Ranks results based on multiple criteria:
  - **Relevance**: How well it matches the query intent
  - **Uniqueness**: Whether it offers unique insights or perspectives
  - **Quality**: Indication of high-quality, substantive content
  - **Depth**: In-depth information vs superficial content
  - **Recency**: Up-to-date information when applicable
  - **Engagement**: Genuinely interesting content for curious readers

### 2. **AI Explanations**
- Each result includes an AI-generated explanation of why it's interesting
- Helps users understand why content was ranked highly
- Displayed as a highlighted insight below each result URL

### 3. **Visual Indicators**
- 🤖 **AI-Curated** badge appears when AI ranking is active
- Animated badge to draw attention to the AI-powered feature
- Clean, modern UI integration

## How It Works

### Ranking Process

1. **Initial Search**: Standard BM25 + metadata scoring retrieves candidate results
2. **AI Analysis**: Top 20 candidates are sent to ChatGPT for analysis
3. **Intelligent Ranking**: GPT-3.5/4 ranks the top 10 most interesting results
4. **Explanation Generation**: AI provides reasoning for each selection
5. **Display**: Results shown with AI insights

### Configuration

Edit `app/app.py` to customize the feature:

```python
# Configuration
ENABLE_AI_RANKING = True  # Set to False to disable AI ranking
ENABLE_QUERY_EXPANSION = True  # Works with query expansion
```

### API Integration

The feature uses OpenAI API. Set your API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_MODEL="gpt-3.5-turbo"  # or "gpt-4" for better results
```

You can also use OpenRouter or other compatible endpoints:

```bash
export OPENAI_API_BASE="https://openrouter.ai/api/v1"
export OPENAI_MODEL="openai/gpt-4"
```

## Implementation Details

### New Module: `ai_ranker.py`

Located at `src/microsearch/ai_ranker.py`, this module provides:

- `rank_results_with_ai()`: Main ranking function
- `get_content_snippet()`: Extract relevant content snippets
- `_fallback_ranking()`: Graceful degradation if AI unavailable
- Automatic fallback to standard ranking if API key not set

### Updated Files

1. **`app/app.py`**
   - Added AI ranking configuration
   - Integrated `rank_results_with_ai()` in search results endpoint
   - Passes AI insights to template

2. **`app/templates/results.html`**
   - Added AI-Curated badge in header
   - Display AI reasoning for each result
   - Visual indicators for AI-ranked content

3. **`app/static/css/styles.css`**
   - Styled AI badge with pulse animation
   - AI insight boxes with gradient background
   - Responsive design for mobile

4. **`requirements.txt`**
   - Added `openai>=1.0.0`
   - Added `requests` (for API calls)

## Benefits

### For Users
- 🎯 **Better Results**: Most interesting content surfaces first
- 💡 **Context**: Understand why results were selected
- 🚀 **Discovery**: Find unexpected, engaging content
- ⚡ **Efficiency**: Less time sifting through irrelevant results

### For Developers
- 🔧 **Configurable**: Easy to enable/disable
- 🛡️ **Robust**: Graceful fallback to standard ranking
- 🔄 **Extensible**: Easy to customize ranking criteria
- 📊 **Transparent**: AI reasoning shown to users

## Performance Considerations

- **Latency**: AI ranking adds ~1-3 seconds per query
- **Cost**: ~$0.001-0.005 per search (using GPT-3.5-turbo)
- **Caching**: Consider adding result caching for popular queries
- **Optimization**: Only top 20 candidates analyzed (not all results)

## Usage Examples

### Query: "machine learning"

**Without AI Ranking**:
1. ml-tutorial.com (score: 10.5)
2. learn-ml-now.com (score: 9.8)
3. machine-learning-research.edu (score: 9.2)

**With AI Ranking**:
1. machine-learning-research.edu
   - 🤖 *"Cutting-edge research with unique insights into transformer architectures"*
2. ml-tutorial.com
   - 🤖 *"Comprehensive guide with practical examples and clear explanations"*
3. learn-ml-now.com
   - 🤖 *"Beginner-friendly approach with interactive demonstrations"*

## Future Enhancements

Potential improvements:
- [ ] Caching of AI rankings for popular queries
- [ ] User feedback on AI rankings
- [ ] A/B testing AI vs standard ranking
- [ ] Personalized ranking based on user history
- [ ] Multi-language support for AI analysis
- [ ] Real-time learning from user interactions

## Troubleshooting

### AI Ranking Not Working?

1. **Check API Key**: Ensure `OPENAI_API_KEY` is set
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Check Configuration**: Verify `ENABLE_AI_RANKING = True` in `app.py`

3. **Check Terminal Output**: Look for "🤖 Using AI to rank..." message

4. **Fallback Mode**: If API fails, app automatically uses standard ranking

### No AI Insights Shown?

- Check that `ai_insights` is being passed to template
- Verify OpenAI API is responding (check terminal logs)
- Ensure you have API credits available

## Credits

Built with:
- **OpenAI GPT-3.5/4**: Intelligent content analysis
- **FastAPI**: Web framework
- **Custom BM25**: Initial result ranking
- **Bootstrap 5**: UI components

---

**Version**: 1.0.0  
**Date**: December 2025  
**Status**: Production Ready ✅

