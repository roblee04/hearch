# Hearch -- A surprising! search engine

Welcome to Robin and Harsh's serendipity / surprise based search engine!

*Hearch* is an attempt to bring surprising / serendipitous results to you, the user, after you query some mumbo jumbo. It does this (to varying levels of effectiveness) via a couple of factors such as an augmented ranking algorithm (not just BM25!) and simple query expansions with an LLM.

Though this will not be your daily driver of a search engine, I hope that the results you query will be interesting.

# Running the Project

## Getting started

The first step is to download this repo

```bash
git clone https://github.com/roblee04/hearch.git
```

Then, I recommend you install everything in a virtual environment. I usually use `virtualenv` but any other environment manager should work.

```bash
virtualenv -p python3.10 venv
```

activate the environment

```bash
source venv/bin/activate
```

and install the package and the dependencies

```bash
pip install .
```

## Expand and Crawl data

Expansion step:
```bash
python crawler.py --input-file seeds.txt --output-file out_urls.txt --type both --depth 5 --pages 10
```

Download content to parquet:
```bash
python download_content.py --feed-path out_urls.txt
```

## Launch app

Finally, once the content is crawled and stored you can run the app as

```bash
python -m app.app --data-path output_with_metadata.parquet
```

and if you navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) you'll be able to query the engine.

# About

The project was adapted from Alex Molas's *microsearch* repository, which served as the basis for basic crawling, indexing, ranking, and serving functionalities.

It is pertinent to note that the focus of the project was on the *surprise* element of retrieved documents and not on the actual components of the engine itself, which is why this search engine was not built from scratch (though it would be fun to do so).

However, that's not to say that no work was done on the code. In order to accomodate for this *surprise* factor, heavy modifications were made to the original files.


# Serendipity Factors
- Manually selected Seed Urls to later crawl/expand on
- MarginaliaSearch inspired ranking algorithm
- Query expansion with an LLM

As for how effective each point is and to what degree, I don't know quantitatively. However this can be further explored if we wanted to through some ablation study.

# Limitations
- Seed urls aren't super well established, hand picked
- Is slow (indexing)
- Relevance (onegram reverse index table), doesnt do well on multiword queries

# Changes made to microsearch

## crawler.py

Crawls upon urls that are given to it. This means exploring + indexing more hyperlinks, nested links, and pages that are available on the initial url. This did not exist in the code originally.

### Usage
\$ python crawler.py --input-file input.txt --output-file output.txt --type both --depth 5 --pages 10


### Options
**Depth** -- *(# of depth)* 
- How many layers of links to crawl through. You must set at least a depth of 1 if you want to crawl any hyperlinks. Setting a negative value = no limit. Be careful about that.

**Pages** -- *(# of pages)*
- How many pages to crawl on each link layer (depth). They will be randomly selected. You must set at least 1 if you want to crawl any hyperlinks. Setting a negative value = no limit. Be careful about that.

**Type** -- *(local / external / both)*
- Indicates if you want to only crawl links local to the website, or links external to the website, or both. 


## download_content.py
Scrapes urls that are given to it and outputs its title, content, and metadata in a pandas Dataframe.

### HTML parsing
The original code only scraped RSS feeds (XML type), so normal HTML sites wouldn't be properly scraped. This had to be rewritten to accomodate for HTML sites.

### Metadata scraping
The original code only scraped for title and content. Because we are additionally using metadata as a factor in the ranking, we have to scrape for that too.

### Specific attributes we scrape for:

| Metadata Field | Description | How it's Used | Heuristic for Scraping |
| :--- | :--- | :--- | :--- |
| `content` | The main cleaned text of the document. | **Bonus** | The primary input for the BM25 score, exact phrase matching, proximity, and first position bonuses. |
| `word_location_flags` | A JSON dictionary mapping words to the important HTML tags they appeared in (e.g., `TITLE`, `HEADING`). | **Strong Bonus** | Adds significant weight if a query term is found in a key location. |
| `html_features` | A JSON list of negative user-experience features found on the page (e.g., `ADVERTISEMENT`, `CONSENT`). | **Penalty** | Each feature in this list adds a fixed penalty value to the score, making the page rank lower. |
| `avg_sentence_length`| An integer representing the average number of words per sentence. | **Penalty** | A penalty is applied if this value is below a certain threshold (e.g., < 10). |
| `doc_size_words` | An integer for the total number of words in the cleaned `content`. | **Penalty** | A penalty is applied if the document is too short (e.g., < 250 words). |
| `quality` | An abstract score where a higher number means worse quality. | **Penalty** | Adds a penalty that is multiplied for longer documents, heavily penalizing long, low-quality content. |
| `year` | The estimated year of publication for the article. | *[Not currently used in score]* | Could be used in the future to boost recent content or for time-based searches. |
| `doc_flags` | A JSON list identifying the type of software that generated the page (e.g., `GeneratorWiki`). | *[Not currently used in score]* | Can be used to apply special rules, e.g., disabling certain penalties for forums. |
| `rank` & `topology` | Abstract scores for a site's authority and its position in the web's link graph. | **Bonus** | Provides a small, general bonus to documents from more authoritative sites. |

***

**Note on Non-Scraped Factors:**

*   **Term Proximity** and **First Position** are not stored as separate metadata. They are calculated at search time by analyzing the word order within the scraped `content` field.
*   **Domain Override** is not scraped data. It is a manual configuration set directly within the `SearchEngine` code to boost or penalize entire domains.


## engine.py
Provides an *engine* class that takes a list of urls, indexes them, and ranks them.

The vanilla implementation just uses BM25 for ranking most relevant pages.

Our implementation combines BM25 with MarginaliaSearch's document rating.


### Score Calculation

The final score is calculated with a normalization formula that inverts a relevance score and applies penalties:

$$
\text{Final Score} = \sqrt{\frac{1 + 500 + (10 \cdot P_{\text{total}})}{1 + S_{\text{relevance}}}}
$$

-   $S_{\text{relevance}}$: The **Relevance Score**. A high value here is good, indicating the document's content is a strong match for the query.
-   $P_{\text{total}}$: The **Total Intrinsic Penalty**. This is a query-independent penalty based on negative document features (like ads or trackers). A high value here is bad.

#### 1. The Relevance Score ($S_{\text{relevance}}$)

The relevance score is a weighted sum of several query-dependent factors, adjusted by a manual domain override.

$$
S_{\text{relevance}} = A_{\text{domain}} \cdot (S_{\text{BM25}} + S_{\text{flags}} + S_{\text{verbatim}} + S_{\text{proximity}} + S_{\text{position}})
$$

The components are:
*   $A_{\text{domain}}$: A **Domain Override** factor to manually boost (`<1.0`) or penalize (`>1.0`) an entire website.
*   $S_{\text{BM25}}$: The score from the **Okapi BM25** ranking function, a standard for measuring term frequency and rarity.
*   $S_{\text{flags}}$: A **Term Location Bonus** that rewards documents where query keywords appear in important HTML tags like `<title>` or `<h1>`.
*   $S_{\text{verbatim}}$: A strong **Exact Phrase Bonus** for documents that contain the complete, verbatim query string.
*   $S_{\text{proximity}}$: A **Term Proximity Bonus** that rewards documents where query keywords appear close to each other.
*   $S_{\text{position}}$: An **Early Appearance Bonus** for documents where query keywords appear early in the text.

#### 2. The Intrinsic Penalty ($P_{\text{total}}$)

The penalty is derived from a document's intrinsic, query-independent properties. First, a comprehensive bonus/penalty score ($B_{\text{doc}}$) is calculated by adding bonuses and subtracting penalties.

$$
B_{\text{doc}} = (\text{Bonuses}) - (\text{Penalties})
$$

-   **Bonuses**:
    -   $B_{\text{rank}}$: A bonus based on pre-calculated site-wide authority.
    -   $B_{\text{topology}}$: A bonus based on the document's position in the site's link graph.
-   **Penalties**:
    -   $P_{\text{flags}}$: The "anti-bullshit" penalty for user-hostile features like `ADVERTISEMENT`, `POPOVER`, `AFFILIATE_LINK`, and `CONSENT` banners.
    -   $P_{\text{quality}}$: A penalty for algorithmically determined low quality.
    -   $P_{\text{length}}$: A penalty for documents being too short.
    -   $P_{\text{sentence}}$: A penalty for documents with very short average sentence lengths.

The final penalty value $P_{\text{total}}$ used in the main formula is just the negative part of this score, ensuring bonuses do not erase penalties from other factors.

$$
P_{\text{total}} = -\min(0, B_{\text{doc}})
$$



## app.py

Apis that are available to be called. 
These apis are served by default, however are used in a cleaner and more elegant frontend.


# Useful Links

## Dataset:
https://github.com/MarginaliaSearch/PublicData/tree/master/sets

## References:
https://github.com/alexmolas/microsearch.git 
https://github.com/MarginaliaSearch/MarginaliaSearch/tree/master
https://wiby.me/about/guide.html 