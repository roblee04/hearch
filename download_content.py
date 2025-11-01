import argparse
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlparse
from dateutil.parser import parse as parse_date
from tqdm.asyncio import tqdm

# --- Configuration for Metadata Extraction ---
# (Configuration is unchanged)
TRACKING_DOMAINS = {
    'google-analytics.com', 'googletagmanager.com', 'stats.g.doubleclick.net',
    'facebook.net', 'connect.facebook.net', 'criteo.com', 'hotjar.com',
    'semrush.com', 'ahrefs.com', 'hubspot.com'
}
CONSENT_KEYWORDS = {'cookie', 'privacy', 'consent', 'gdpr', 'accept'}
AD_KEYWORDS = {'advertisement', 'sponsored', 'ad-slot'}


# --- Set up Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper Functions (Refactored) ---

def _find_pub_date(soup: BeautifulSoup):
    """Tries to find the publication date from various meta tags."""
    meta_selectors = [
        "meta[property='article:published_time']",
        "meta[property='og:published_time']",
        "meta[name='publication_date']",
        "meta[name='parsely-pub-date']",
        "meta[name='sailthru.date']",
        "meta[name='dc.date.issued']",
        "time[datetime]",
    ]
    for selector in meta_selectors:
        element = soup.select_one(selector)
        if element:
            date_str = element.get('content') or element.get('datetime')
            if date_str:
                try:
                    return parse_date(date_str)
                except (ValueError, TypeError):
                    continue
    return None

def clean_content_from_soup(soup: BeautifulSoup) -> str:
    """Removes script/style tags and cleans up whitespace from a BeautifulSoup object."""
    # This function now expects a soup object to avoid re-parsing
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose() # .decompose() is slightly more efficient than .extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = " ".join(chunk for chunk in chunks if chunk)
    return cleaned_text

def extract_metadata(url: str, soup: BeautifulSoup, cleaned_text: str) -> dict:
    """
    Extracts metadata from the page.
    The URL comment about BM25 is interesting! Okapi BM25 is a ranking function used by search engines to score document relevance [en.wikipedia.org](https://en.wikipedia.org/wiki/Okapi_BM25). 
    Your approach of collecting metadata to use as priors or penalties on top of a text-based score is a solid strategy.
    """
    title = soup.title.string.strip() if soup.title else ''
    description = soup.find('meta', attrs={'name': 'description'})
    description_text = description['content'].strip() if description else ''
    
    words = cleaned_text.split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', cleaned_text)
    num_sentences = len([s for s in sentences if len(s.strip()) > 5])
    avg_sentence_length = (word_count / num_sentences) if num_sentences > 0 else 0

    internal_links, external_links, affiliate_links = 0, 0, 0
    parsed_base_url = urlparse(url)
    all_links = soup.find_all('a', href=True)

    for link in all_links:
        href = link['href']
        abs_url = urljoin(url, href)
        parsed_abs_url = urlparse(abs_url)

        if parsed_abs_url.netloc == parsed_base_url.netloc:
            internal_links += 1
        else:
            external_links += 1

        if 'aff_' in href or 'tag=' in href or 'amzn.to' in href:
            affiliate_links += 1

    text_lower = cleaned_text.lower()
    url_path = parsed_base_url.path

    metadata = {
        'title': title, 'meta_description': description_text, 'pub_date': _find_pub_date(soup),
        'word_count': word_count, 'avg_sentence_length': round(avg_sentence_length, 2),
        'heading_text': ' '.join(h.get_text(" ", strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])),
        'internal_link_count': internal_links, 'external_link_count': external_links,
        'affiliate_link_count': affiliate_links,
        'has_consent_banner': any(kw in text_lower for kw in CONSENT_KEYWORDS),
        'has_ads_keywords': any(kw in text_lower for kw in AD_KEYWORDS),
        'has_tracking_scripts': any(any(td in s['src'] for td in TRACKING_DOMAINS) for s in soup.find_all('script', src=True)),
        'is_long_url': len(url) > 100, 'has_kebab_case_url': '-' in url_path,
    }
    return metadata

async def fetch_process_and_extract(
    session: aiohttp.ClientSession, 
    url: str, 
    semaphore: asyncio.Semaphore
) -> dict | None:
    """
    Fetches a URL under a semaphore, cleans content, extracts metadata, and returns a dict.
    """
    # IMPROVEMENT: Wrap the entire network operation in the semaphore
    async with semaphore:
        # logger.info(f"Starting to fetch {url}")
        try:
            # IMPROVEMENT: Use a more specific timeout object
            timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=20)
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                html_content = await response.text()

                # IMPROVEMENT: Parse the HTML only ONCE
                soup = BeautifulSoup(html_content, "html.parser")
                
                # Pass the soup object to the cleaning function
                cleaned_text = clean_content_from_soup(soup)
                
                # Re-use the soup object for metadata extraction
                metadata = extract_metadata(url, soup, cleaned_text)

                record = {'URL': url, 'content': cleaned_text, **metadata}
                # logger.info(f"Successfully processed {url}")
                return record
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP Client Error fetching {url}: {e}")
            pass
        except asyncio.TimeoutError:
            logger.error(f"Timeout error fetching {url} after 30 seconds")
            pass
        except Exception as e:
            logger.error(f"An unexpected error occurred for {url}: {e}")
            pass
    
    return None

def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Crawl content and metadata from a list of URLs.")
    parser.add_argument(
        "--feed-path", required=True,
        help="Path to a file containing a list of URLs to crawl, one per line."
    )
    # IMPROVEMENT: Make concurrency configurable
    parser.add_argument(
        "--concurrency", type=int, default=15,
        help="Number of concurrent requests to allow."
    )
    return parser.parse_args()

async def main(url_file: str, concurrency_limit: int):
    """Main function to coordinate the crawling process."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # IMPROVEMENT: Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrency_limit)
    logger.info(f"Starting crawl with a concurrency limit of {concurrency_limit}")

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            with open(url_file, "r") as file:
                urls = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            logger.error(f"Error: The file '{url_file}' was not found.")
            return

        if not urls:
            logger.warning("The input file is empty. No URLs to process.")
            return

        # IMPROVEMENT: Pass the semaphore to each task
        tasks = [fetch_process_and_extract(session, url, semaphore) for url in urls]
        results = await tqdm.gather(*tasks, desc="Crawling URLs")

    successful_results = [res for res in results if res]

    if not successful_results:
        logger.warning("Could not retrieve content from any of the provided URLs.")
        return

    df = pd.DataFrame.from_records(successful_results)
    
    output_file = "output_with_metadata.parquet"
    df.to_parquet(output_file, index=False)
    logger.info(f"Successfully saved {len(df)} results to {output_file}")
    print("\nSample of saved data:")
    print(df["URL"].head().tolist())


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.feed_path, args.concurrency))