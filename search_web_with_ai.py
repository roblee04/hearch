#!/usr/bin/env python3
"""
AI Web Search - Search the Entire Internet
Finds websites containing at least 5 keywords from your query.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from microsearch.ai_web_search import search_entire_web_with_ai, extract_keywords


def print_header(query: str, min_keywords: int):
    """Print search header."""
    print("\n" + "=" * 80)
    print("🌐 AI WEB SEARCH - Searching Entire Internet")
    print("=" * 80)
    print(f"Query: \"{query}\"")
    print(f"Requirement: Websites must contain at least {min_keywords} keywords")
    print("=" * 80 + "\n")


def print_results(results: list, query: str):
    """Print results in a nice format."""
    if not results:
        print("❌ No results found.")
        print("\nPossible reasons:")
        print("  - OPENAI_API_KEY environment variable not set")
        print("  - API error or rate limit")
        print("  - Network connectivity issues")
        return
    
    keywords = extract_keywords(query)
    print(f"Query Keywords: {', '.join(keywords[:10])}\n")
    print(f"✅ Found {len(results)} websites from the internet:\n")
    
    for i, result in enumerate(results, 1):
        # Create nice box
        print(f"┌─ Result #{i} {'─' * 65}")
        print(f"│")
        print(f"│ 📌 {result['title']}")
        print(f"│ 🔗 {result['url']}")
        print(f"│ 📁 {result['content_type']} | ⭐ Authority: {result['authority_score']}/10")
        print(f"│")
        
        # Keywords matched
        matched = result.get('matched_keywords', [])
        print(f"│ ✓ Matched Keywords ({len(matched)}): ", end='')
        print(f"{', '.join(matched[:8])}")
        if len(matched) > 8:
            print(f"│   + {len(matched) - 8} more...")
        print(f"│")
        
        # Description
        if result.get('description'):
            desc = result['description']
            words = desc.split()
            line = "│   "
            for word in words:
                if len(line) + len(word) + 1 > 78:
                    print(line)
                    line = "│   " + word
                else:
                    line += " " + word if len(line) > 4 else word
            if line.strip() != "│":
                print(line)
            print(f"│")
        
        # Why relevant
        if result.get('why_relevant'):
            print(f"│ 💡 Why Relevant:")
            reason = result['why_relevant']
            words = reason.split()
            line = "│   "
            for word in words:
                if len(line) + len(word) + 1 > 78:
                    print(line)
                    line = "│   " + word
                else:
                    line += " " + word if len(line) > 4 else word
            if line.strip() != "│":
                print(line)
            print(f"│")
        
        print(f"└{'─' * 77}\n")


def main():
    """Main function."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='sk-your-api-key-here'")
        return 1
    
    # Get query
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        print("🔍 AI Web Search")
        print("-" * 40)
        query = input("Enter your search query: ").strip()
        if not query:
            print("❌ No query provided. Exiting.")
            return 1
    
    # Get min keyword requirement
    min_keywords = 5
    try:
        custom = input(f"Min keywords per site (default: {min_keywords}): ").strip()
        if custom:
            min_keywords = int(custom)
    except:
        pass
    
    # Print header
    print_header(query, min_keywords)
    
    # Search
    print("⏳ Searching the entire internet with AI...\n")
    
    try:
        results = search_entire_web_with_ai(
            query=query,
            min_keyword_matches=min_keywords,
            num_results=10
        )
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Print results
    print("\n" + "=" * 80)
    print_results(results, query)
    
    if not results:
        return 1
    
    # Summary
    print("=" * 80)
    print("📊 Summary")
    print("=" * 80)
    
    total_keywords = sum(r['keyword_count'] for r in results)
    avg_keywords = total_keywords / len(results) if results else 0
    avg_authority = sum(r['authority_score'] for r in results) / len(results) if results else 0
    
    content_types = {}
    for r in results:
        ct = r.get('content_type', 'Other')
        content_types[ct] = content_types.get(ct, 0) + 1
    
    print(f"Total Websites: {len(results)}")
    print(f"Avg Keywords/Site: {avg_keywords:.1f}")
    print(f"Avg Authority: {avg_authority:.1f}/10")
    print(f"Content Types: {', '.join(f'{k} ({v})' for k, v in content_types.items())}")
    print()
    
    # Save option
    save_prompt = input("💾 Save results to JSON file? (y/n): ").strip().lower()
    if save_prompt in ('y', 'yes'):
        import json
        from datetime import datetime
        
        safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query)
        safe_query = safe_query.replace(' ', '_')[:40]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"web_search_{safe_query}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'min_keyword_matches': min_keywords,
                'timestamp': datetime.now().isoformat(),
                'num_results': len(results),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {filename}")
    
    print("\n✨ Done!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

