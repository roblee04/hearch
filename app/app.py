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

script_dir = pathlib.Path(__file__).resolve().parent
templates_path = script_dir / "templates"
static_path = script_dir / "static"

# Configuration
ENABLE_QUERY_EXPANSION = True  # Set to False to disable query expansion
NUM_EXPANDED_QUERIES = 4  # Number of alternative queries to generate
ORIGINAL_QUERY_WEIGHT = 0.40  # Weight for original query (40%)
EXPANDED_QUERY_WEIGHT = 0.15  # Weight for each expanded query (15% each, total 60%)

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
async def search_results(request: Request, query: str = Path(...)):
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
    
    top_results = get_top_results(results, n=10)
    return templates.TemplateResponse(
        "results.html", {
            "request": request, 
            "results": top_results, 
            "query": query,
            "expanded_queries": all_queries_used[1:] if ENABLE_QUERY_EXPANSION else []
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