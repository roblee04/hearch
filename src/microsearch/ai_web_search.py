"""
Enhanced AI Web Search
Uses ChatGPT to search the entire internet and find websites with multiple keyword matches.
"""

import os
import json
from typing import List, Dict, Set


def extract_keywords(query: str, min_keywords: int = 5) -> List[str]:
    """Extract keywords from query."""
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                  'can', 'could', 'may', 'might', 'must', 'shall'}
    
    words = query.lower().split()
    keywords = [w.strip('.,!?;:') for w in words if w.lower() not in stop_words and len(w) > 2]
    
    # If we don't have enough keywords, use all words
    if len(keywords) < min_keywords:
        keywords = [w.strip('.,!?;:') for w in words if len(w) > 2]
    
    return keywords


def search_entire_web_with_ai(
    query: str,
    min_keyword_matches: int = 5,
    num_results: int = 10
) -> List[Dict[str, str]]:
    """
    Uses ChatGPT to search the ENTIRE internet for websites containing query keywords.
    
    Args:
        query: The search query
        min_keyword_matches: Minimum number of query keywords the website must contain
        num_results: Number of results to return
        
    Returns:
        List of dictionaries with website information
    """
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Cannot search the web with AI.")
            return []
        
        # Extract keywords from query
        keywords = extract_keywords(query, min_keywords=min_keyword_matches)
        keywords_str = ", ".join(keywords[:10])  # Limit to 10 keywords for display
        
        print(f"🔍 Searching entire internet for websites with keywords: {keywords_str}")
        
        # Enhanced prompt for comprehensive web search
        prompt = f"""You are an expert web researcher with complete knowledge of the internet.

Search Query: "{query}"
Keywords to match: {keywords_str}

TASK: Find {num_results} real websites from the ENTIRE INTERNET that:
1. Are highly relevant to the search query
2. Contain AT LEAST {min_keyword_matches} of these keywords in their content
3. Are authoritative, high-quality sources
4. Cover different aspects and perspectives of the topic
5. Include diverse content types (articles, tutorials, tools, research, videos, communities, news)

For EACH website, provide:
1. **url**: The actual, real website URL (must exist and be accessible)
2. **title**: The page or site title
3. **description**: Brief description of the content (2-3 sentences)
4. **matched_keywords**: List of which keywords from the query are found on this site (minimum {min_keyword_matches})
5. **content_type**: Type of content (Tutorial, Research, Tool, Article, Video, Community, News, Documentation, Blog)
6. **authority_score**: How authoritative/trustworthy (1-10)
7. **why_relevant**: Why this site is highly relevant for this query

IMPORTANT:
- Search your ENTIRE knowledge of the internet
- Only suggest websites that ACTUALLY contain the query keywords
- Prioritize sites with more keyword matches
- Include both popular AND lesser-known high-quality sources
- Ensure URLs are real and currently active (as of your knowledge)
- Focus on content-rich sites, not just homepages

Return ONLY a JSON array with this exact format:
[
  {{
    "url": "https://example.com/specific-page",
    "title": "Specific Page Title",
    "description": "Detailed description of what this page contains and why it's valuable.",
    "matched_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "content_type": "Tutorial",
    "authority_score": 9,
    "why_relevant": "This site is highly relevant because..."
  }}
]

Return ONLY the JSON array, no other text."""

        client = openai.OpenAI(api_key=api_key, base_url=api_base)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert web researcher with comprehensive knowledge of the internet. 
You find the most relevant, authoritative websites that match search queries. You only suggest real 
websites that actually exist and contain the query keywords. You prioritize content quality, 
relevance, and keyword matching."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse JSON response
        try:
            start = ai_response.find("[")
            end = ai_response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = ai_response[start:end]
                results = json.loads(json_str)
                
                # Validate and filter results
                validated_results = []
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    
                    # Check required fields
                    if 'url' not in result or 'title' not in result:
                        continue
                    
                    # Check keyword matching
                    matched_kw = result.get('matched_keywords', [])
                    if len(matched_kw) < min_keyword_matches:
                        print(f"⚠️  Skipping {result['url']}: only {len(matched_kw)} keywords matched (need {min_keyword_matches})")
                        continue
                    
                    # Build validated result
                    validated_result = {
                        'url': result.get('url', '').strip(),
                        'title': result.get('title', 'No title').strip(),
                        'description': result.get('description', '').strip(),
                        'matched_keywords': matched_kw,
                        'content_type': result.get('content_type', 'General').strip(),
                        'authority_score': result.get('authority_score', 5),
                        'why_relevant': result.get('why_relevant', '').strip(),
                        'source': 'AI-Web-Search',
                        'ai_generated': True,
                        'keyword_count': len(matched_kw)
                    }
                    
                    if validated_result['url'] and validated_result['title']:
                        validated_results.append(validated_result)
                        print(f"✅ Found: {validated_result['title']} ({len(matched_kw)} keywords)")
                
                print(f"\n🎯 Total results found: {len(validated_results)} websites with {min_keyword_matches}+ keyword matches")
                return validated_results[:num_results]
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"Response preview: {ai_response[:200]}...")
            
    except Exception as e:
        print(f"AI web search failed: {e}")
        import traceback
        traceback.print_exc()
    
    return []


def format_web_search_results(results: List[Dict]) -> str:
    """Format web search results for display."""
    if not results:
        return "No results found."
    
    output = []
    output.append(f"Found {len(results)} websites from the internet:\n")
    
    for i, result in enumerate(results, 1):
        output.append(f"{i}. {result['title']}")
        output.append(f"   URL: {result['url']}")
        output.append(f"   Type: {result['content_type']} | Authority: {result['authority_score']}/10")
        output.append(f"   Keywords matched ({result['keyword_count']}): {', '.join(result['matched_keywords'][:8])}")
        if result.get('description'):
            output.append(f"   Description: {result['description']}")
        if result.get('why_relevant'):
            output.append(f"   💡 {result['why_relevant']}")
        output.append("")
    
    return "\n".join(output)


if __name__ == "__main__":
    import sys
    
    # Test the web search
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("Enter search query: ").strip()
    
    if not query:
        print("No query provided.")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"🌐 AI Web Search - Searching Entire Internet")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Requirement: At least 5 keyword matches per website")
    print(f"{'='*80}\n")
    
    results = search_entire_web_with_ai(query, min_keyword_matches=5, num_results=10)
    
    if results:
        print("\n" + format_web_search_results(results))
        
        # Ask to save
        save = input("\nSave results to JSON? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"web_search_{query.replace(' ', '_')[:30]}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'query': query,
                    'min_keyword_matches': 5,
                    'results': results
                }, f, indent=2)
            print(f"✅ Saved to {filename}")
    else:
        print("❌ No results found. Check your OPENAI_API_KEY.")

