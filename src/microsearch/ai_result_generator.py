"""
AI Result Generator
Uses ChatGPT to generate unique, interesting web results for search queries.
These can supplement indexed results or provide suggestions when index is sparse.
"""

import os
import json
from typing import List, Dict, Optional


def generate_interesting_results(
    query: str,
    num_results: int = 10,
    include_reasoning: bool = True
) -> List[Dict[str, str]]:
    """
    Uses ChatGPT to generate unique, interesting web results for a search query.
    
    Args:
        query: The search query
        num_results: Number of results to generate (default: 10)
        include_reasoning: Whether to include reasoning for each result
        
    Returns:
        List of dictionaries with keys:
        - 'url': The suggested URL
        - 'title': Page title
        - 'description': Brief description
        - 'reasoning': Why this is interesting (if include_reasoning=True)
        - 'category': Content category
    """
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Cannot generate AI results.")
            return []
        
        # Create detailed prompt for ChatGPT
        prompt = f"""You are a knowledgeable research assistant helping users discover the most interesting, unique, and valuable web resources.

Query: "{query}"

Generate {num_results} unique, interesting web resources that would be most valuable for someone searching for this topic.

For each result, suggest:
1. A real, high-quality website URL (prioritize authoritative, interesting, and diverse sources)
2. An accurate page title
3. A brief description (2-3 sentences) of what makes this resource valuable
4. Why this is interesting or unique
5. A category (e.g., "Tutorial", "Research", "Community", "Tool", "Documentation", "Blog", "News", "Video")

IMPORTANT:
- Suggest REAL websites that actually exist
- Prioritize quality, depth, and uniqueness over popularity
- Include diverse types of content (articles, tools, communities, research papers, videos, etc.)
- Avoid generic or low-quality sources
- Make sure URLs are realistic and likely to exist

Return ONLY a JSON array with this exact format:
[
  {{
    "url": "https://example.com/page",
    "title": "Page Title",
    "description": "Brief description of the content and why it's valuable.",
    "reasoning": "Why this is interesting or unique for this query.",
    "category": "Category"
  }}
]

Return ONLY the JSON array, no other text."""

        client = openai.OpenAI(api_key=api_key, base_url=api_base)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant that suggests high-quality, diverse web resources. You prioritize depth, uniqueness, and value over popularity. You always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,  # Balance between creativity and consistency
            max_tokens=2000
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse JSON response
        try:
            start = ai_response.find("[")
            end = ai_response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = ai_response[start:end]
                results = json.loads(json_str)
                
                # Validate and clean results
                validated_results = []
                for result in results[:num_results]:
                    if isinstance(result, dict) and 'url' in result and 'title' in result:
                        validated_result = {
                            'url': result.get('url', '').strip(),
                            'title': result.get('title', 'No title').strip(),
                            'description': result.get('description', '').strip(),
                            'category': result.get('category', 'General').strip(),
                            'source': 'AI-Generated',
                            'ai_generated': True
                        }
                        
                        if include_reasoning:
                            validated_result['reasoning'] = result.get('reasoning', '').strip()
                        
                        if validated_result['url'] and validated_result['title']:
                            validated_results.append(validated_result)
                
                print(f"✅ Generated {len(validated_results)} AI-suggested results")
                return validated_results
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"Response was: {ai_response[:200]}...")
            
    except Exception as e:
        print(f"AI result generation failed: {e}")
    
    return []


def merge_results(
    indexed_results: Dict[str, float],
    ai_results: List[Dict[str, str]],
    ai_weight: float = 0.3
) -> List[tuple]:
    """
    Merges indexed search results with AI-generated results.
    
    Args:
        indexed_results: Dict of {url: score} from search engine
        ai_results: List of AI-generated result dicts
        ai_weight: Weight to assign to AI results (0.0-1.0)
        
    Returns:
        List of tuples (url, score, metadata) sorted by combined score
    """
    combined = {}
    
    # Add indexed results
    for url, score in indexed_results.items():
        combined[url] = {
            'score': score,
            'source': 'indexed',
            'ai_generated': False
        }
    
    # Add AI-generated results with weighted scores
    # Give them scores based on their ranking (higher rank = higher score)
    max_indexed_score = max(indexed_results.values()) if indexed_results else 10.0
    
    for i, result in enumerate(ai_results):
        url = result['url']
        # Score decreases with rank: 1st gets highest score, 10th gets lowest
        ai_score = max_indexed_score * ai_weight * (1 - i / len(ai_results))
        
        if url not in combined:
            combined[url] = {
                'score': ai_score,
                'source': 'AI-generated',
                'ai_generated': True,
                'title': result.get('title', ''),
                'description': result.get('description', ''),
                'category': result.get('category', ''),
                'reasoning': result.get('reasoning', '')
            }
        else:
            # URL exists in both - boost its score
            combined[url]['score'] += ai_score * 0.5
            combined[url]['ai_endorsed'] = True
    
    # Sort by score
    sorted_results = sorted(
        combined.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    
    return [(url, meta['score'], meta) for url, meta in sorted_results]


def format_results_for_display(
    merged_results: List[tuple],
    top_n: int = 10
) -> Dict[str, dict]:
    """
    Formats merged results for display in the web interface.
    
    Args:
        merged_results: List of (url, score, metadata) tuples
        top_n: Number of top results to return
        
    Returns:
        Dict of {url: metadata} for top N results
    """
    display_results = {}
    
    for url, score, meta in merged_results[:top_n]:
        display_results[url] = {
            'score': score,
            'source': meta.get('source', 'indexed'),
            'ai_generated': meta.get('ai_generated', False),
            'ai_endorsed': meta.get('ai_endorsed', False),
            'title': meta.get('title', ''),
            'description': meta.get('description', ''),
            'category': meta.get('category', ''),
            'reasoning': meta.get('reasoning', '')
        }
    
    return display_results


# Standalone script functionality
def main():
    """
    Standalone script to generate AI results for a query.
    Usage: python ai_result_generator.py
    """
    import sys
    
    # Get query from command line or prompt
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("Enter search query: ").strip()
        if not query:
            print("No query provided. Exiting.")
            return
    
    print(f"\n🔍 Generating unique results for: '{query}'")
    print("=" * 60)
    
    results = generate_interesting_results(query, num_results=10)
    
    if not results:
        print("❌ No results generated. Check your OPENAI_API_KEY.")
        return
    
    print(f"\n✅ Generated {len(results)} unique results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Category: {result['category']}")
        print(f"   Description: {result['description']}")
        if 'reasoning' in result:
            print(f"   💡 Why interesting: {result['reasoning']}")
        print()
    
    # Option to save results
    save = input("Save results to JSON file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"ai_results_{query.replace(' ', '_')[:30]}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Saved to {filename}")


if __name__ == "__main__":
    main()

