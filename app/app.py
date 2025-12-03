import argparse
from fastapi import FastAPI, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from uvicorn import run
import pathlib
from collections import defaultdict

from microsearch.engine import SearchEngine  
from microsearch.query_expansion import expand_query
from microsearch.ai_ranker import rank_results_with_ai
from microsearch.ai_result_generator import generate_interesting_results, merge_results
from microsearch.ai_web_search import search_entire_web_with_ai

script_dir = pathlib.Path(__file__).resolve().parent
templates_path = script_dir / "templates"
static_path = script_dir / "static"

# Configuration
ENABLE_QUERY_EXPANSION = True  # Set to False to disable query expansion
ENABLE_AI_RANKING = True  # Set to False to disable AI-powered result ranking
ENABLE_AI_RESULT_GENERATION = True  # Set to False to disable AI-generated results
ENABLE_AI_WEB_SEARCH = True  # Set to False to disable comprehensive web search
MIN_KEYWORD_MATCHES = 5  # Minimum keywords that websites must contain
NUM_EXPANDED_QUERIES = 4  # Number of alternative queries to generate
NUM_AI_GENERATED_RESULTS = 10  # Number of AI-generated results to include
ORIGINAL_QUERY_WEIGHT = 0.40  # Weight for original query (40%)
EXPANDED_QUERY_WEIGHT = 0.15  # Weight for each expanded query (15% each, total 60%)
AI_RESULT_WEIGHT = 0.3  # Weight for AI-generated results (relative to indexed results)

app = FastAPI()
engine = SearchEngine()
templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


def combine_weighted_results(results_list: list[tuple[dict, float]]) -> dict[str, float]:
    """
    Combines multiple search result dictionaries with weights.
    
    Args:
        results_list: List of tuples (results_dict, weight)
        
    Returns:
        Combined results with weighted scores
    """
    combined = defaultdict(float)
    
    for results, weight in results_list:
        for url, score in results.items():
            combined[url] += score * weight
    
    return dict(combined)


def get_top_results(results_dict: dict, n: int) -> dict:
    """Sorts and returns the top N results based on score."""
    # The engine already returns scores, so we just sort and slice

    # Higher BM25 scores are better, so reverse=True for descending order
    sorted_results = sorted(results_dict.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_results[:n])


@app.get("/", response_class=HTMLResponse)
async def search(request: Request):
    # This just needs a list of URLs for a potential dropdown or example list
    posts = engine.posts
    return templates.TemplateResponse(
        "search.html", {"request": request, "posts": posts}
    )


@app.get("/results/{query}", response_class=HTMLResponse)
async def search_results(request: Request, query: str = Path(...), ai_only: bool = False):
    if ENABLE_QUERY_EXPANSION:
        # Perform query expansion
        print(f"Original query: {query}")
        expanded_queries = expand_query(query, num_expansions=NUM_EXPANDED_QUERIES)
        print(f"Expanded queries: {expanded_queries}")
        
        # Search with original query
        original_results = engine.search(query)
        
        # Search with expanded queries
        weighted_results = [(original_results, ORIGINAL_QUERY_WEIGHT)]
        
        for exp_query in expanded_queries:
            exp_results = engine.search(exp_query)
            weighted_results.append((exp_results, EXPANDED_QUERY_WEIGHT))
        
        # Combine all results with weights
        results = combine_weighted_results(weighted_results)
        
        # Add metadata for display
        all_queries_used = [query] + expanded_queries
    else:
        # Standard search without expansion
        results = engine.search(query)
        all_queries_used = [query]
    
    # Generate AI-suggested results and merge with indexed results
    ai_generated_results = []
    if ENABLE_AI_RESULT_GENERATION:
        # Use enhanced web search for comprehensive results
        if ENABLE_AI_WEB_SEARCH:
            print(f"🌐 Searching entire web for sites with {MIN_KEYWORD_MATCHES}+ keyword matches...")
            ai_generated_results = search_entire_web_with_ai(
                query=query,
                min_keyword_matches=MIN_KEYWORD_MATCHES,
                num_results=NUM_AI_GENERATED_RESULTS
            )
        else:
            print(f"🤖 Generating unique AI results for query...")
            ai_generated_results = generate_interesting_results(
                query=query,
                num_results=NUM_AI_GENERATED_RESULTS,
                include_reasoning=True
            )
        
        if ai_generated_results:
            print(f"✅ Generated {len(ai_generated_results)} AI results, merging with indexed results...")
            # Merge AI results with indexed results
            merged = merge_results(results, ai_generated_results, ai_weight=AI_RESULT_WEIGHT)
            # Convert back to dict format for ranking
            results = {url: score for url, score, meta in merged}
            # Store metadata for AI-generated results
            for url, score, meta in merged:
                if meta.get('ai_generated') and url not in engine._metadata:
                    # Get description from either 'description' or 'content'
                    description = meta.get('description', meta.get('content', ''))
                    
                    # Build metadata dict
                    metadata = {
                        'title': meta.get('title', ''),
                        'content': description,
                        'ai_generated': True,
                        'category': meta.get('category', meta.get('content_type', '')),
                        'reasoning': meta.get('reasoning', meta.get('why_relevant', ''))
                    }
                    
                    # Add web search specific fields if available
                    if 'matched_keywords' in meta:
                        metadata['matched_keywords'] = meta['matched_keywords']
                        metadata['keyword_count'] = meta.get('keyword_count', len(meta['matched_keywords']))
                    if 'authority_score' in meta:
                        metadata['authority_score'] = meta['authority_score']
                    if 'content_type' in meta:
                        metadata['content_type'] = meta['content_type']
                    
                    engine._metadata[url] = metadata
    
    # Use AI to rank results by interestingness
    if ENABLE_AI_RANKING:
        print(f"🤖 Using AI to rank top 10 most interesting results...")
        ranked_results = rank_results_with_ai(
            query=query,
            results=results,
            metadata_dict=engine._metadata,
            top_n=10
        )
        # Convert to the format expected by template: {url: score}
        top_results = {url: score for url, score, reasoning in ranked_results}
        # Add AI reasoning to metadata for display
        ai_insights = {url: reasoning for url, score, reasoning in ranked_results}
    else:
        top_results = get_top_results(results, n=10)
        ai_insights = {}
    
    # Mark which results are AI-generated
    ai_generated_urls = {r['url'] for r in ai_generated_results}
    
    # Filter to show only AI results if requested
    if ai_only and ai_generated_urls:
        top_results = {url: score for url, score in top_results.items() if url in ai_generated_urls}
        print(f"📌 Showing only AI-generated results: {len(top_results)} results")
    
    return templates.TemplateResponse(
        "results.html", {
            "request": request, 
            "results": top_results, 
            "query": query,
            "expanded_queries": all_queries_used[1:] if ENABLE_QUERY_EXPANSION else [],
            "ai_insights": ai_insights,
            "ai_generated_urls": ai_generated_urls,
            "metadata": engine._metadata,
            "ai_only": ai_only
        }
    )


@app.get("/about")
def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


def parse_args():
    # Updated help text for clarity
    parser = argparse.ArgumentParser(description="Run a search engine server.")
    parser.add_argument(
        "--data-path",
        required=True,
        help="Path to the .parquet file containing crawled data with metadata."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Load the full parquet file with metadata
    data = pd.read_parquet(args.data_path)

    # Fill NaN in content with empty strings to prevent errors
    data['content'] = data['content'].fillna('')

    print(f"Indexing {len(data)} documents from {args.data_path}...")
    
    # Pass the entire DataFrame to the engine
    engine.bulk_index(data)
    
    print("Indexing complete. Starting server...")
    run(app, host="127.0.0.1", port=8000)