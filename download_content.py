import argparse
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlparse
from dateutil.parser import parse as parse_date

# --- Configuration for Metadata Extraction ---

# Known tracking domains to check for in script tags
TRACKING_DOMAINS = {
    'google-analytics.com', 'googletagmanager.com', 'stats.g.doubleclick.net',
    'facebook.net', 'connect.facebook.net', 'criteo.com', 'hotjar.com',
    'semrush.com', 'ahrefs.com', 'hubspot.com'
}

# Keywords to detect consent banners, ads, etc.
CONSENT_KEYWORDS = {'cookie', 'privacy', 'consent', 'gdpr', 'accept'}
AD_KEYWORDS = {'advertisement', 'sponsored', 'ad-slot'}


# --- Set up Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _find_pub_date(soup: BeautifulSoup):
    """Tries to find the publication date from various meta tags."""
    # Common meta tags for publication date
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

def extract_metadata(url: str, soup: BeautifulSoup, cleaned_text: str) -> dict:
    """
    Extracts metadata from the page, inspired by Marginalia Search's ranking factors.
    """
    # 1. Basic Metadata (from <head>)
    title = soup.title.string.strip() if soup.title else ''
    description = soup.find('meta', attrs={'name': 'description'})
    description_text = description['content'].strip() if description else ''

    # 2. Content-based features
    words = cleaned_text.split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', cleaned_text)
    num_sentences = len([s for s in sentences if len(s.strip()) > 5]) # Avoid empty/short splits
    avg_sentence_length = (word_count / num_sentences) if num_sentences > 0 else 0

    # 3. Link Analysis & Topology
    internal_links, external_links, affiliate_links = 0, 0, 0
    parsed_base_url = urlparse(url)
    all_links = soup.find_all('a', href=True)

    for link in all_links:
        href = link['href']
        # Resolve relative URLs
        abs_url = urljoin(url, href)
        parsed_abs_url = urlparse(abs_url)

        if parsed_abs_url.netloc == parsed_base_url.netloc:
            internal_links += 1
        else:
            external_links += 1

        # Heuristic for affiliate links (inspired by HtmlFeature.AFFILIATE_LINK)
        if 'aff_' in href or 'tag=' in href or 'amzn.to' in href:
            affiliate_links += 1

    # 4. HTML "Anti-Features" & Flags (inspired by flagsPenalty)
    text_lower = cleaned_text.lower()
    url_path = parsed_base_url.path
    
    # [researchgate.net](https://www.researchgate.net/publication/220613776_The_Probabilistic_Relevance_Framework_BM25_and_Beyond)
    # The Marginalia code uses BM25 as part of its ranking. The metadata we're collecting
    # here serves as document-level priors or bonuses/penalties that are applied on top of
    # the core BM25 relevance score.
    metadata = {
        # --- Basic Info ---
        'title': title,
        'meta_description': description_text,
        'pub_date': _find_pub_date(soup),
        # --- Content Features ---
        'word_count': word_count,
        'avg_sentence_length': round(avg_sentence_length, 2),
        'heading_text': ' '.join(h.get_text(" ", strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])),
        # --- Topology Features ---
        'internal_link_count': internal_links,
        'external_link_count': external_links,
        # --- Penalty/Flag Features ---
        'affiliate_link_count': affiliate_links,
        'has_consent_banner': any(kw in text_lower for kw in CONSENT_KEYWORDS),
        'has_ads_keywords': any(kw in text_lower for kw in AD_KEYWORDS),
        'has_tracking_scripts': any(
            any(td in s['src'] for td in TRACKING_DOMAINS)
            for s in soup.find_all('script', src=True)
        ),
        'is_long_url': len(url) > 100,
        'has_kebab_case_url': '-' in url_path,
    }
    return metadata

def clean_content(html_content: str) -> str:
    """Removes script/style tags and cleans up whitespace from HTML."""
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = " ".join(chunk for chunk in chunks if chunk)
    return cleaned_text


async def fetch_process_and_extract(session: aiohttp.ClientSession, url: str) -> dict | None:
    """
    Fetches a URL, cleans content, extracts metadata, and returns a combined dictionary.
    """
    try:
        async with session.get(url, timeout=30) as response:
            response.raise_for_status()
            html_content = await response.text()

            # Create the soup object once
            soup = BeautifulSoup(html_content, "html.parser")

            # First, clean the text (which also uses the soup object)
            # The clean_content function is simpler if it creates its own temporary soup
            cleaned_text = clean_content(html_content)
            
            # Then, extract metadata from the original soup and cleaned text
            metadata = extract_metadata(url, soup, cleaned_text)

            # Combine everything into a single record
            record = {
                'URL': url,
                'content': cleaned_text,
                **metadata # Unpack the metadata dictionary into the main record
            }

            logger.info(f"Successfully processed {url}")
            return record
            
    except aiohttp.ClientError as e:
        logger.error(f"HTTP Client Error fetching {url}: {e}")
    except asyncio.TimeoutError:
        logger.error(f"Timeout error fetching {url}")
    except Exception as e:
        logger.error(f"An unexpected error occurred for {url}: {e}")
    
    return None

def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Crawl content and metadata from a list of URLs.")
    parser.add_argument(
        "--feed-path",
        required=True,
        help="Path to a file containing a list of URLs to crawl, one per line."
    )
    return parser.parse_args()


async def main(url_file: str):
    """Main function to coordinate the crawling process."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

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

        tasks = [fetch_process_and_extract(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    # Filter out None results from failed requests
    successful_results = [res for res in results if res]

    if not successful_results:
        logger.warning("Could not retrieve content from any of the provided URLs.")
        return

    # Using from_records is ideal for a list of dictionaries
    df = pd.DataFrame.from_records(successful_results)
    
    output_file = "output_with_metadata.parquet"
    df.to_parquet(output_file, index=False)
    logger.info(f"Successfully saved {len(df)} results to {output_file}")
    print("\nSample of saved data:")
    print(df["URL"].tolist())
    # print("\nColumns saved:")
    # print(df.columns.tolist())


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.feed_path))