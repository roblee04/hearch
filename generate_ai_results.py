#!/usr/bin/env python3
"""
Standalone script to generate unique search results using ChatGPT.
Can be run independently or imported into other modules.

Usage:
    python generate_ai_results.py "your search query"
    python generate_ai_results.py
"""

import sys
import os
import json
from datetime import datetime

# Add src to path so we can import microsearch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from microsearch.ai_result_generator import generate_interesting_results


def print_header(query: str):
    """Print a nice header for the results."""
    print("\n" + "=" * 80)
    print(f"🤖 AI-Generated Search Results")
    print("=" * 80)
    print(f"Query: \"{query}\"")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


def print_results(results: list):
    """Print results in a nice format."""
    if not results:
        print("❌ No results generated.")
        print("\nPossible reasons:")
        print("  - OPENAI_API_KEY environment variable not set")
        print("  - API error or rate limit")
        print("  - Network connectivity issues")
        return
    
    print(f"✅ Generated {len(results)} unique results:\n")
    
    for i, result in enumerate(results, 1):
        # Create a nice box for each result
        print(f"┌─ Result #{i} {'─' * 65}")
        print(f"│")
        print(f"│ 📌 {result['title']}")
        print(f"│ 🔗 {result['url']}")
        print(f"│ 📁 Category: {result['category']}")
        print(f"│")
        print(f"│ 📝 Description:")
        # Word wrap description
        desc_lines = result['description'].split('\n')
        for line in desc_lines:
            words = line.split()
            current_line = "│    "
            for word in words:
                if len(current_line) + len(word) + 1 > 78:
                    print(current_line)
                    current_line = "│    " + word
                else:
                    current_line += " " + word if len(current_line) > 5 else word
            if current_line.strip() != "│":
                print(current_line)
        
        if 'reasoning' in result and result['reasoning']:
            print(f"│")
            print(f"│ 💡 Why This is Interesting:")
            reason_lines = result['reasoning'].split('\n')
            for line in reason_lines:
                words = line.split()
                current_line = "│    "
                for word in words:
                    if len(current_line) + len(word) + 1 > 78:
                        print(current_line)
                        current_line = "│    " + word
                    else:
                        current_line += " " + word if len(current_line) > 5 else word
                if current_line.strip() != "│":
                    print(current_line)
        
        print(f"│")
        print(f"└{'─' * 77}\n")


def save_to_json(results: list, query: str):
    """Save results to a JSON file."""
    # Create a safe filename
    safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query)
    safe_query = safe_query.replace(' ', '_')[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"ai_results_{safe_query}_{timestamp}.json"
    
    data = {
        'query': query,
        'timestamp': datetime.now().isoformat(),
        'num_results': len(results),
        'results': results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename


def main():
    """Main function to run the script."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='sk-your-api-key-here'")
        print("\nOr add it to your ~/.bashrc or ~/.zshrc:")
        print("  echo 'export OPENAI_API_KEY=\"sk-your-key\"' >> ~/.zshrc")
        return 1
    
    # Get query from command line arguments or prompt user
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        print("🔍 AI Search Result Generator")
        print("-" * 40)
        query = input("Enter your search query: ").strip()
        if not query:
            print("❌ No query provided. Exiting.")
            return 1
    
    # Print header
    print_header(query)
    
    # Generate results
    print("⏳ Generating unique results using ChatGPT...\n")
    
    try:
        results = generate_interesting_results(
            query=query,
            num_results=10,
            include_reasoning=True
        )
    except Exception as e:
        print(f"❌ Error generating results: {e}")
        return 1
    
    # Print results
    print_results(results)
    
    if not results:
        return 1
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Summary")
    print("=" * 80)
    
    categories = {}
    for result in results:
        cat = result.get('category', 'Other')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"Total Results: {len(results)}")
    print(f"Categories: {', '.join(f'{cat} ({count})' for cat, count in categories.items())}")
    print()
    
    # Ask to save
    save_prompt = input("💾 Save results to JSON file? (y/n): ").strip().lower()
    if save_prompt in ('y', 'yes'):
        try:
            filename = save_to_json(results, query)
            print(f"✅ Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    print("\n✨ Done!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

