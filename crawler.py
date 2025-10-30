import argparse
import aiohttp
import asyncio
import logging
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

# Usage:
# python url_expander.py --input-file seeds.txt --output-file deep_crawl_output.txt --depth 3 --pages -1 --type both

# --- Set up Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    """Parses command-line arguments for the web crawler."""
    parser = argparse.ArgumentParser(
        description="""
        Crawl websites starting from a list of seed URLs to discover and expand the list of links.
        Outputs all discovered URLs to a specified text file.
        """
    )
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to the input text file containing seed URLs, one per line."
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the output text file where the expanded list of URLs will be saved."
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="""
        How many layers of links to crawl.
        Depth=0 means only process the seed URLs (no crawling).
        Depth=1 crawls the seed URLs and finds links on them.
        A negative value means unlimited depth (use with caution!).
        Default is 1.
        """
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=20,
        help="""
        Max number of pages to crawl on each link layer (depth).
        Pages are randomly selected from the newly found links at each level.
        A negative value means no limit.
        Default is 20.
        """
    )
    parser.add_argument(
        "--type",
        type=str,
        default='local',
        choices=['local', 'external', 'both'],
        help="""
        Specifies which type of links to follow.
        'local': Only links on the same domain.
        'external': Only links to a different domain.
        'both': Both local and external links.
        Default is 'local'.
        """
    )
    return parser.parse_args()


async def fetch_and_find_links(session: aiohttp.ClientSession, url: str, crawl_type: str) -> Set[str]:
    """
    Fetches a single URL, parses its HTML for hyperlinks, and returns a set of
    new URLs based on the specified crawl type.
    """
    found_links = set()
    try:
        async with session.get(url, timeout=15) as response:
            # We only care about successful responses with HTML content
            if response.status != 200 or 'text/html' not in response.headers.get('content-type', ''):
                logger.debug(f"Skipping non-HTML page or bad status ({response.status}) at: {url}")
                return found_links

            html_content = await response.text()
            soup = BeautifulSoup(html_content, "html.parser")
            base_netloc = urlparse(url).netloc

            for link in soup.find_all("a", href=True):
                href = link.get("href")
                if not href:
                    continue
                
                # Ignore mailto, javascript, and other non-http links
                if href.startswith(('mailto:', 'javascript:', '#', 'tel:')):
                    continue

                # Resolve relative URLs to absolute ones
                abs_url = urljoin(url, href)

                # Clean the URL by removing the fragment identifier
                parsed_abs_url = urlparse(abs_url)
                if parsed_abs_url.scheme not in ('http', 'https'):
                    continue
                
                cleaned_url = parsed_abs_url._replace(fragment="").geturl()
                link_netloc = parsed_abs_url.netloc

                # Filter links based on the crawl type
                is_local = link_netloc == base_netloc
                
                if crawl_type == 'local' and is_local:
                    found_links.add(cleaned_url)
                elif crawl_type == 'external' and not is_local and link_netloc:
                    found_links.add(cleaned_url)
                elif crawl_type == 'both' and link_netloc:
                    found_links.add(cleaned_url)

    except aiohttp.ClientError as e:
        logger.error(f"HTTP Client Error fetching {url}: {e}")
    except asyncio.TimeoutError:
        logger.error(f"Timeout error fetching {url}")
    except Exception as e:
        # This catches parsing errors or other unexpected issues
        logger.error(f"An unexpected error occurred for {url}: {e}")
    
    return found_links


async def main(args):
    """Main function to coordinate the crawling process."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        with open(args.input_file, "r") as f:
            seed_urls = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        logger.error(f"Error: The input file '{args.input_file}' was not found.")
        return

    if not seed_urls:
        logger.warning("The input file is empty. No URLs to process.")
        return

    # --- Crawler State Management ---
    # Holds all URLs ever discovered (seed + new)
    all_discovered_urls = set(seed_urls)
    # URLs that have been sent for crawling to avoid re-crawling
    visited_urls = set()
    # URLs to be crawled in the current depth level
    urls_to_crawl_this_level = set(seed_urls)
    current_depth = 0
    
    logger.info(f"Starting crawl with {len(seed_urls)} seed URLs. Config: Depth={args.depth}, Pages/Level={args.pages}, Type={args.type}")

    async with aiohttp.ClientSession(headers=headers) as session:
        # The main crawl loop, continues as long as there are links to crawl and we are within the depth limit
        while urls_to_crawl_this_level and (args.depth < 0 or current_depth < args.depth):
            logger.info(f"--- Starting Depth {current_depth + 1} | Crawling {len(urls_to_crawl_this_level):,} URLs ---")
            
            # Add the URLs for the current level to the visited set
            visited_urls.update(urls_to_crawl_this_level)
            
            # Create a list of async tasks for the current level
            tasks = [fetch_and_find_links(session, url, args.type) for url in urls_to_crawl_this_level]
            results = await asyncio.gather(*tasks, return_exceptions=False)
            
            # Process the results from this level's crawl
            newly_found_links = set()
            for link_set in results:
                newly_found_links.update(link_set)
            
            # Filter out any links we've already designated for crawling
            unique_new_links = newly_found_links - visited_urls
            
            # Add these unique discoveries to our master list
            all_discovered_urls.update(unique_new_links)

            logger.info(f"Depth {current_depth + 1} finished. Found {len(unique_new_links):,} new unique URLs.")
            
            # --- Prepare for the next level ---
            # Apply the --pages limit
            if args.pages >= 0 and len(unique_new_links) > args.pages:
                urls_to_crawl_this_level = set(random.sample(list(unique_new_links), args.pages))
                logger.info(f"Randomly selected {len(urls_to_crawl_this_level)} URLs for the next level due to '--pages' limit.")
            else:
                urls_to_crawl_this_level = unique_new_links
            
            current_depth += 1

    # --- Save the results ---
    logger.info(f"Crawl finished. Discovered a total of {len(all_discovered_urls):,} URLs.")
    
    try:
        # Sort for consistent output
        sorted_urls = sorted(list(all_discovered_urls))
        with open(args.output_file, "w") as f:
            for url in sorted_urls:
                f.write(url + "\n")
        logger.info(f"Successfully saved {len(sorted_urls)} URLs to {args.output_file}")
    except IOError as e:
        logger.error(f"Failed to write to output file '{args.output_file}': {e}")


if __name__ == "__main__":
    args = parse_args()
    # Be careful with high depths or unlimited pages!
    if args.depth < 0:
        logger.warning("WARNING: You have set an unlimited crawl depth. This can lead to very long run times and high resource usage.")
    if args.pages < 0:
        logger.warning("WARNING: You have set an unlimited number of pages per level. This can lead to very long run times and high resource usage.")

    asyncio.run(main(args))