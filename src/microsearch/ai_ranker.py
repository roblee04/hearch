"""
AI-Powered Result Ranking Module
Uses ChatGPT to analyze and rank search results by interestingness and relevance.
"""

import os
import json
from typing import List, Dict, Tuple


def get_content_snippet(content: str, max_length: int = 200) -> str:
    """Extract a snippet from content for analysis."""
    if not content:
        return ""
    return content[:max_length].strip() + ("..." if len(content) > max_length else "")


def rank_results_with_ai(
    query: str,
    results: Dict[str, float],
    metadata_dict: Dict[str, dict],
    top_n: int = 10
) -> List[Tuple[str, float, str]]:
    """
    Uses ChatGPT to analyze and rank search results by interestingness.
    
    Args:
        query: The original search query
        results: Dictionary of {url: score} from search engine
        metadata_dict: Dictionary of {url: metadata} with content and other info
        top_n: Number of top results to return
        
    Returns:
        List of tuples (url, original_score, ai_reasoning) sorted by AI ranking
    """
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Falling back to standard ranking.")
            return _fallback_ranking(results, metadata_dict, top_n)
        
        # Take initial top candidates (e.g., top 20) to analyze
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        candidates = sorted_results[:min(20, len(sorted_results))]
        
        # Prepare data for AI analysis
        candidates_info = []
        for idx, (url, score) in enumerate(candidates):
            meta = metadata_dict.get(url, {})
            title = meta.get('title', 'No title')
            content_snippet = get_content_snippet(meta.get('content', ''))
            pub_date = meta.get('pub_date', 'Unknown')
            
            candidates_info.append({
                'index': idx,
                'url': url,
                'title': title,
                'snippet': content_snippet,
                'pub_date': str(pub_date) if pub_date else 'Unknown',
                'original_score': round(score, 3)
            })
        
        # Create prompt for AI analysis
        prompt = f"""You are an expert at identifying the most interesting and valuable web content for users.

Query: "{query}"

Below are {len(candidates_info)} search results. Analyze them and rank the TOP {top_n} most interesting results.

Consider:
1. **Relevance**: How well does it match the query intent?
2. **Uniqueness**: Does it offer unique insights or perspectives?
3. **Quality**: Does the title/snippet suggest high-quality, substantive content?
4. **Depth**: Does it appear to provide in-depth information vs superficial content?
5. **Recency**: Is it recent and up-to-date? (when applicable)
6. **Engagement**: Would this be genuinely interesting and engaging for a curious reader?

Results to analyze:
{json.dumps(candidates_info, indent=2)}

Return ONLY a JSON array of the top {top_n} most interesting results. Each item should be:
{{
  "index": <original index number>,
  "reasoning": "<brief 1-sentence explanation of why this is interesting>"
}}

Order them from most interesting (rank 1) to least interesting (rank {top_n}).
Return ONLY the JSON array, no other text."""

        client = openai.OpenAI(api_key=api_key, base_url=api_base)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content curator who identifies the most interesting, valuable, and engaging search results for users. You prioritize depth, uniqueness, and genuine value over generic content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent rankings
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse AI rankings
        try:
            start = ai_response.find("[")
            end = ai_response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = ai_response[start:end]
                rankings = json.loads(json_str)
                
                # Build final ranked results
                ranked_results = []
                for rank_item in rankings[:top_n]:
                    idx = rank_item.get('index')
                    reasoning = rank_item.get('reasoning', 'AI selected as interesting')
                    
                    if idx is not None and idx < len(candidates):
                        url, score = candidates[idx]
                        ranked_results.append((url, score, reasoning))
                
                if ranked_results:
                    print(f"✅ AI successfully ranked {len(ranked_results)} results")
                    return ranked_results
                    
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response: {e}")
            
    except Exception as e:
        print(f"AI ranking failed: {e}")
    
    # Fallback to standard ranking
    return _fallback_ranking(results, metadata_dict, top_n)


def _fallback_ranking(
    results: Dict[str, float],
    metadata_dict: Dict[str, dict],
    top_n: int
) -> List[Tuple[str, float, str]]:
    """Fallback ranking when AI is not available."""
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return [(url, score, "Standard ranking") for url, score in sorted_results[:top_n]]


def explain_ranking(ranked_results: List[Tuple[str, float, str]]) -> str:
    """Generate a human-readable explanation of the AI ranking."""
    if not ranked_results:
        return "No results to display."
    
    explanation = "🤖 AI-Curated Results:\n\n"
    for i, (url, score, reasoning) in enumerate(ranked_results, 1):
        explanation += f"{i}. {reasoning}\n"
    
    return explanation


if __name__ == "__main__":
    # Test the AI ranker
    test_query = "machine learning"
    test_results = {
        "example.com/ml-guide": 10.5,
        "blog.com/intro-to-ml": 9.2,
        "research.edu/deep-learning": 8.7,
    }
    test_metadata = {
        "example.com/ml-guide": {
            "title": "Complete Machine Learning Guide",
            "content": "This comprehensive guide covers everything you need to know about machine learning...",
            "pub_date": "2024-01-15"
        },
        "blog.com/intro-to-ml": {
            "title": "Introduction to ML for Beginners",
            "content": "Learn the basics of machine learning in this beginner-friendly tutorial...",
            "pub_date": "2023-06-20"
        },
        "research.edu/deep-learning": {
            "title": "Advanced Deep Learning Research",
            "content": "Cutting-edge research in deep neural networks and transformer architectures...",
            "pub_date": "2024-02-01"
        }
    }
    
    print(f"Testing AI ranking for query: {test_query}")
    ranked = rank_results_with_ai(test_query, test_results, test_metadata, top_n=3)
    
    print("\nRanked Results:")
    for i, (url, score, reasoning) in enumerate(ranked, 1):
        print(f"{i}. {url}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasoning: {reasoning}\n")

