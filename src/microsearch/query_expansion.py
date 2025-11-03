"""
Query Expansion Module using LLM
Generates alternative queries to improve search serendipity and recall.
"""

import os
from typing import List
import json


def expand_query_with_ollama(original_query: str, num_expansions: int = 4) -> List[str]:
    """
    Expands a query into multiple related but serendipitous queries using Ollama.
    
    Args:
        original_query: The user's original search query
        num_expansions: Number of alternative queries to generate (default: 4)
    
    Returns:
        List of expanded queries (excluding the original)
    """
    try:
        import requests
        
        # Ollama API endpoint (default local installation)
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        prompt = f"""You are a creative query expansion assistant for a serendipitous search engine.
Given a search query, generate {num_expansions} alternative queries that are:
- Related but explore different angles
- Slightly creative and unexpected
- Likely to surface interesting, surprising content
- Varied in scope (some broader, some more specific)

Original query: "{original_query}"

Generate exactly {num_expansions} alternative queries. Return ONLY a valid JSON array of strings, nothing else.
Example format: ["query 1", "query 2", "query 3", "query 4"]
"""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.8,  # Higher temperature for more creativity
        }
        
        response = requests.post(ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "")
        
        # Try to parse as JSON array
        try:
            # Find JSON array in the response
            start = generated_text.find("[")
            end = generated_text.rfind("]") + 1
            if start != -1 and end > start:
                json_str = generated_text[start:end]
                queries = json.loads(json_str)
                if isinstance(queries, list) and len(queries) > 0:
                    # Return only the requested number of queries
                    return [q.strip() for q in queries[:num_expansions] if isinstance(q, str) and q.strip()]
        except json.JSONDecodeError:
            pass
        
        # Fallback: split by newlines if JSON parsing fails
        lines = [line.strip().strip('"').strip("'").strip('-').strip() 
                 for line in generated_text.split('\n') 
                 if line.strip() and not line.strip().startswith('{') and not line.strip().startswith('[')]
        return [q for q in lines[:num_expansions] if q and q.lower() != original_query.lower()]
        
    except Exception as e:
        print(f"Query expansion failed: {e}")
        # Return simple fallback expansions
        return generate_fallback_expansions(original_query, num_expansions)


def expand_query_with_openai(original_query: str, num_expansions: int = 4) -> List[str]:
    """
    Expands a query using OpenAI API (or compatible endpoint like OpenRouter).
    
    Args:
        original_query: The user's original search query
        num_expansions: Number of alternative queries to generate
    
    Returns:
        List of expanded queries
    """
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        client = openai.OpenAI(api_key=api_key, base_url=api_base)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative query expansion assistant. Generate alternative search queries that are related but explore different angles. Be serendipitous and interesting."
                },
                {
                    "role": "user",
                    "content": f'Generate {num_expansions} alternative search queries for: "{original_query}". Return as a JSON array of strings only.'
                }
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        generated = response.choices[0].message.content
        
        # Parse JSON array
        try:
            start = generated.find("[")
            end = generated.rfind("]") + 1
            if start != -1 and end > start:
                json_str = generated[start:end]
                queries = json.loads(json_str)
                if isinstance(queries, list):
                    return [q.strip() for q in queries[:num_expansions] if isinstance(q, str) and q.strip()]
        except json.JSONDecodeError:
            pass
            
        return generate_fallback_expansions(original_query, num_expansions)
        
    except Exception as e:
        print(f"OpenAI query expansion failed: {e}")
        return generate_fallback_expansions(original_query, num_expansions)


def generate_fallback_expansions(query: str, num_expansions: int = 4) -> List[str]:
    """
    Simple fallback query expansions without LLM.
    
    Args:
        query: Original query
        num_expansions: Number of expansions to generate
    
    Returns:
        List of simple query variations
    """
    expansions = []
    
    # Add simple variations
    templates = [
        f"what is {query}",
        f"how to {query}",
        f"{query} explained",
        f"{query} guide",
        f"learn about {query}",
        f"{query} tutorial",
        f"understanding {query}",
        f"{query} introduction",
    ]
    
    return templates[:num_expansions]


def expand_query(original_query: str, num_expansions: int = 4, method: str = "auto") -> List[str]:
    """
    Main function to expand a query using available LLM services.
    
    Args:
        original_query: The user's search query
        num_expansions: Number of alternative queries to generate
        method: "ollama", "openai", or "auto" (tries ollama first, then openai, then fallback)
    
    Returns:
        List of expanded queries (excluding the original)
    """
    if method == "ollama":
        return expand_query_with_ollama(original_query, num_expansions)
    elif method == "openai":
        return expand_query_with_openai(original_query, num_expansions)
    else:  # auto
        # Try Ollama first (local, free)
        try:
            import requests
            # Quick check if Ollama is available
            requests.get("http://localhost:11434/api/tags", timeout=2)
            return expand_query_with_ollama(original_query, num_expansions)
        except:
            pass
        
        # Try OpenAI if available
        if os.getenv("OPENAI_API_KEY"):
            return expand_query_with_openai(original_query, num_expansions)
        
        # Fallback
        return generate_fallback_expansions(original_query, num_expansions)


if __name__ == "__main__":
    # Test the query expansion
    test_query = "potatoes"
    print(f"Original query: {test_query}")
    print(f"\nExpanded queries:")
    
    expansions = expand_query(test_query, num_expansions=5)
    for i, exp_query in enumerate(expansions, 1):
        print(f"{i}. {exp_query}")

