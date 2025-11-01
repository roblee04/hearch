import argparse
import aiohttp
import asyncio
import logging
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, Dict
from urllib.robotparser import RobotFileParser

# --- Constants ---
# Define our User-Agent here to be used by both the session and the robot parser.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MyEducationCrawler/1.1"

# --- Set up Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    """Parses command-line arguments for the web crawler."""
    parser = argparse.ArgumentParser(
        description="A polite, asynchronous web crawler that respects robots.txt."
    )
    # ... (rest of the argument parser is unchanged)
    parser.add_argument(
        "--input-file", required=True,
        help="Path to the input text file containing seed URLs, one per line."
    )
    parser.add_argument(
        "--output-file", required=True,
        help="Path to the output text file where the expanded list of URLs will be saved."
    )
    parser.add_argument(
        "--depth", type=int, default=1,
        help="How many layers of links to crawl. Depth=0 means only seed URLs. Negative value is unlimited. Default is 1."
    )
    parser.add_argument(
        "--pages", type=int, default=20,
        help="Max number of pages to crawl per depth level. A negative value means no limit. Default is 20."
    )
    parser.add_argument(
        "--type", type=str, default='local', choices=['local', 'external', 'both'],
        help="Specifies which type of links to follow: 'local', 'external', or 'both'. Default is 'local'."
    )
    parser.add_argument(
        "--concurrency", type=int, default=10,
        help="Maximum number of concurrent requests. Default is 10."
    )
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="Base delay in seconds between requests. A random jitter is added. Default is 1.0."
    )
    return parser.parse_args()


# NEW: Function to get and cache robot parsers
async def get_robot_parser(session: aiohttp.ClientSession, netloc: str, cache: Dict[str, RobotFileParser]) -> RobotFileParser:
    """
    Fetches, parses, and caches the robots.txt file for a given domain (netloc).
    Returns a RobotFileParser object.
    """
    if netloc in cache:
        return cache[netloc]

    parser = RobotFileParser()
    # Default to allowing everything if robots.txt is missing or fails
    parser.set_url(f"https://{netloc}/robots.txt")

    try:
        async with session.get(parser.url, timeout=10) as response:
            if response.status == 200:
                text = await response.text()
                parser.parse(text.splitlines())
                logger.info(f"Successfully fetched and parsed robots.txt for {netloc}")
            else:
                logger.debug(f"Could not find a robots.txt for {netloc} (status: {response.status}), assuming allow all.")
                # An empty parser with no rules allows everything
                parser.parse([])
    except Exception as e:
        logger.error(f"Error fetching robots.txt for {netloc}: {e}. Assuming allow all.")
        parser.parse([])

    cache[netloc] = parser
    return parser


async def fetch_and_find_links(session: aiohttp.ClientSession, url: str, crawl_type: str) -> Set[str]:
    # ... (This function is unchanged from the previous version)
    found_links = set()
    try:
        # Set a reasonable timeout for each request
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
            if response.status != 200:
                logger.debug(f"Failed status {response.status} for {url}")
                return found_links

            if 'text/html' not in response.headers.get('content-type', '').lower():
                logger.debug(f"Skipping non-HTML page at: {url}")
                return found_links

            html_content = await response.text()
            soup = BeautifulSoup(html_content, "html.parser")
            base_netloc = urlparse(url).netloc

            for link in soup.find_all("a", href=True):
                href = link.get("href")
                if not href:
                    continue

                if href.startswith(('mailto:', 'javascript:', '#', 'tel:')):
                    continue

                abs_url = urljoin(url, href)
                parsed_abs_url = urlparse(abs_url)

                if parsed_abs_url.scheme not in ('http', 'https'):
                    continue

                cleaned_url = parsed_abs_url._replace(fragment="").geturl()
                link_netloc = parsed_abs_url.netloc

                is_local = link_netloc == base_netloc

                if crawl_type == 'local' and is_local:
                    found_links.add(cleaned_url)
                elif crawl_type == 'external' and not is_local and link_netloc:
                    found_links.add(cleaned_url)
                elif crawl_type == 'both' and link_netloc:
                    found_links.add(cleaned_url)

    except asyncio.TimeoutError:
        logger.error(f"Timeout error fetching {url}")
    except aiohttp.ClientError as e:
        logger.error(f"Client error fetching {url}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred for {url}: {e}")
    
    return found_links


async def process_url(session: aiohttp.ClientSession, url: str, crawl_type: str, semaphore: asyncio.Semaphore, delay: float) -> Set[str]:
    # ... (This function is unchanged from the previous version)
    async with semaphore:
        logger.debug(f"Requesting: {url}")
        found_links = await fetch_and_find_links(session, url, crawl_type)
        # Add a randomized delay to be polite to the server
        await asyncio.sleep(delay + random.uniform(0, delay * 0.5))
        return found_links


async def main(args):
    """Main function to coordinate the crawling process."""
    headers = {"User-Agent": USER_AGENT}

    try:
        with open(args.input_file, "r") as f:
            seed_urls = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        logger.error(f"Error: The input file '{args.input_file}' was not found.")
        return

    all_discovered_urls = set(seed_urls)
    visited_urls = set()
    urls_to_crawl_this_level = set(seed_urls)
    current_depth = 0
    
    # NEW: Cache for robot file parsers
    robot_parsers: Dict[str, RobotFileParser] = {}

    semaphore = asyncio.Semaphore(args.concurrency)
    
    logger.info(f"Starting crawl with {len(seed_urls)} seed URLs. Config: Depth={args.depth}, Concurrency={args.concurrency}, User-Agent='{USER_AGENT}'")

    async with aiohttp.ClientSession(headers=headers) as session:
        while urls_to_crawl_this_level and (args.depth < 0 or current_depth <= args.depth):
            logger.info(f"--- Starting Depth {current_depth + 1} | Crawling up to {len(urls_to_crawl_this_level):,} URLs ---")
            
            visited_urls.update(urls_to_crawl_this_level)
            
            tasks = [process_url(session, url, args.type, semaphore, args.delay) for url in urls_to_crawl_this_level]
            results = await asyncio.gather(*tasks, return_exceptions=False)
            
            newly_found_links = set()
            for link_set in results:
                newly_found_links.update(link_set)
            
            unique_new_links = newly_found_links - all_discovered_urls
            
            # --- NEW: Filter newly found links based on robots.txt ---
            allowed_new_links = set()
            if unique_new_links:
                logger.info(f"Checking robots.txt for {len(unique_new_links):,} new links...")
                for url in unique_new_links:
                    netloc = urlparse(url).netloc
                    if not netloc:
                        continue
                    
                    parser = await get_robot_parser(session, netloc, robot_parsers)
                    if parser.can_fetch(USER_AGENT, url):
                        allowed_new_links.add(url)
                    else:
                        logger.debug(f"Disallowed by robots.txt: {url}")
                logger.info(f"Found {len(allowed_new_links):,} URLs allowed by robots.txt.")
            # --- End of robots.txt filter ---

            all_discovered_urls.update(allowed_new_links)

            logger.info(f"Depth {current_depth + 1} finished. Found {len(allowed_new_links):,} new unique & allowed URLs. Total discovered: {len(all_discovered_urls):,}")
            
            current_depth += 1
            if args.depth > 0 and current_depth > args.depth:
                break

            if args.pages >= 0 and len(allowed_new_links) > args.pages:
                urls_to_crawl_this_level = set(random.sample(list(allowed_new_links), args.pages))
                logger.info(f"Randomly selected {len(urls_to_crawl_this_level)} URLs for the next level due to '--pages' limit.")
            else:
                urls_to_crawl_this_level = allowed_new_links

    logger.info(f"Crawl finished. Discovered a total of {len(all_discovered_urls):,} URLs.")
    
    try:
        sorted_urls = sorted(list(all_discovered_urls))
        with open(args.output_file, "w") as f:
            for url in sorted_urls:
                f.write(url + "\n")
        logger.info(f"Successfully saved {len(sorted_urls)} URLs to {args.output_file}")
    except IOError as e:
        logger.error(f"Failed to write to output file '{args.output_file}': {e}")


if __name__ == "__main__":
    args = parse_args()
    if args.depth < 0:
        logger.warning("WARNING: Unlimited crawl depth can lead to very long run times.")
    if args.pages < 0:
        logger.warning("WARNING: Unlimited pages per level can lead to very long run times.")

    asyncio.run(main(args))