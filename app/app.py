import argparse
from fastapi import FastAPI, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from uvicorn import run
import pathlib

from microsearch.engine import SearchEngine  

script_dir = pathlib.Path(__file__).resolve().parent
templates_path = script_dir / "templates"
static_path = script_dir / "static"

# Querying thru 3000 items is super slow, reminder to add @cache decorator to help with this

app = FastAPI()
engine = SearchEngine()
templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


def get_top_results(results_dict: dict, n: int) -> dict:
    """Sorts and returns the top N results based on score."""
    # The engine already returns scores, so we just sort and slice

    # lower score is better, reverse = False
    sorted_results = sorted(results_dict.items(), key=lambda x: x[1], reverse=False)
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
    results = engine.search(query)
    top_results = get_top_results(results, n=10) # Increased to 10
    return templates.TemplateResponse(
        "results.html", {"request": request, "results": top_results, "query": query}
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