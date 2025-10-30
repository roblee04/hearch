from collections import defaultdict
from math import log
import string
import pandas as pd
from datetime import datetime, timedelta

def normalize_string(input_string: str) -> str:
    """Removes punctuation, converts to lowercase, and removes extra spaces."""
    if not isinstance(input_string, str):
        return ""
    translation_table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    string_without_punc = input_string.translate(translation_table)
    string_without_double_spaces = " ".join(string_without_punc.split())
    return string_without_double_spaces.lower()


class SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        # --- Core indexing structures ---
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._documents: dict[str, str] = {}
        # New: Store metadata for each document
        self._metadata: dict[str, dict] = {}

        # --- BM25 parameters ---
        self.k1 = k1
        self.b = b

        # --- Metadata Ranking Weights (inspired by Marginalia) ---
        # These weights are added or subtracted to create a final document score.
        # This score is then used to modulate the BM25 score.
        self.BONUS_WEIGHTS = {
            'recent_publish': 0.15,  # Bonus for articles published in the last 2 years
            'topology': 0.05,        # Small bonus based on the number of links (log scaled)
        }
        self.PENALTY_WEIGHTS = {
            'short_document': 0.20,  # Penalty for documents with less than 150 words
            'short_sentence': 0.10,  # Penalty for avg sentence length < 8 words
            'long_url': 0.15,
            'kebab_case_url': 0.05,
            'has_ads': 0.25,
            'has_tracking': 0.10,
            'has_consent_banner': 0.05,
            'has_affiliate_links': 0.15,
        }

    @property
    def posts(self) -> list[str]:
        return list(self._documents.keys())

    @property
    def number_of_documents(self) -> int:
        return len(self._documents)

    @property
    def avdl(self) -> float:
        """Calculates Average Document Length. Cached for performance."""
        if not hasattr(self, "_avdl"):
            total_length = sum(len(d.split()) for d in self._documents.values())
            self._avdl = total_length / self.number_of_documents if self.number_of_documents > 0 else 0
        return self._avdl

    def idf(self, kw: str) -> float:
        """Calculates Inverse Document Frequency for a keyword."""
        N = self.number_of_documents
        n_kw = len(self._index.get(kw, {}))
        # Standard IDF formula with smoothing
        return log((N - n_kw + 0.5) / (n_kw + 0.5) + 1)

    def bm25(self, kw: str) -> dict[str, float]:
        """Calculates BM25 scores for a single keyword across all relevant documents."""
        result = {}
        idf_score = self.idf(kw)
        avdl = self.avdl
        
        # [huggingface.co](https://huggingface.co/blog/xhluca/bm25s) provides a good overview of BM25.
        # This implementation follows the standard Okapi BM25 formula.
        for url, freq in self._index.get(kw, {}).items():
            doc_len = len(self._documents[url].split())
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / avdl)
            result[url] = idf_score * numerator / denominator
        return result

    def calculate_metadata_score(self, url: str) -> float:
        """
        Calculates a bonus/penalty score based on a document's metadata.
        A positive score is a bonus, a negative score is a penalty.
        """
        doc_meta = self._metadata.get(url)
        if not doc_meta:
            return 0.0

        score = 0.0

        # --- Apply Bonuses ---
        pub_date = doc_meta.get('pub_date')
        if pub_date and not pd.isna(pub_date):
            if datetime.now(pub_date.tzinfo) - pub_date < timedelta(days=365 * 2):
                score += self.BONUS_WEIGHTS['recent_publish']
        
        link_count = doc_meta.get('internal_link_count', 0) + doc_meta.get('external_link_count', 0)
        score += log(1 + link_count) * self.BONUS_WEIGHTS['topology']

        # --- Apply Penalties ---
        if doc_meta.get('word_count', 151) < 150:
            score -= self.PENALTY_WEIGHTS['short_document']
        if doc_meta.get('avg_sentence_length', 9) < 8:
            score -= self.PENALTY_WEIGHTS['short_sentence']
        if doc_meta.get('is_long_url', False):
            score -= self.PENALTY_WEIGHTS['long_url']
        if doc_meta.get('has_kebab_case_url', False):
            score -= self.PENALTY_WEIGHTS['kebab_case_url']
        if doc_meta.get('has_ads_keywords', False):
            score -= self.PENALTY_WEIGHTS['has_ads']
        if doc_meta.get('has_tracking_scripts', False):
            score -= self.PENALTY_WEIGHTS['has_tracking']
        if doc_meta.get('has_consent_banner', False):
            score -= self.PENALTY_WEIGHTS['has_consent_banner']
        if doc_meta.get('affiliate_link_count', 0) > 0:
            score -= self.PENALTY_WEIGHTS['has_affiliate_links']

        return score

    def search(self, query: str) -> dict[str, float]:
        """
        Performs a hybrid search:
        1. Calculates a base score using BM25 for keyword relevance.
        2. Calculates a metadata score for document quality.
        3. Combines them into a final score.
        """
        keywords = normalize_string(query).split(" ")
        
        # 1. Calculate base BM25 scores by summing keyword scores
        bm25_scores: dict[str, float] = defaultdict(float)
        for kw in keywords:
            for url, score in self.bm25(kw).items():
                bm25_scores[url] += score

        # 2. Apply metadata scores to create the final hybrid score
        final_scores: dict[str, float] = {}
        for url, bm25_score in bm25_scores.items():
            metadata_score = self.calculate_metadata_score(url)
            
            # The final score is the BM25 score modulated by the metadata score.
            # A metadata score of 0 leaves the BM25 score unchanged.
            # A positive metadata score boosts the final score.
            # A negative metadata score penalizes the final score.
            final_score = bm25_score * (1.0 + metadata_score)
            
            # Ensure score doesn't become negative
            final_scores[url] = max(0, final_score)
            
        return final_scores

    def index(self, url: str, content: str, metadata: dict) -> None:
        """Indexes a single document, its content, and its metadata."""
        if not content or not isinstance(content, str):
            return  # Skip indexing empty or invalid content

        self._documents[url] = content
        self._metadata[url] = metadata
        
        words = normalize_string(content).split(" ")
        for word in words:
            if word:
                self._index[word][url] += 1
        
        # Invalidate cached average document length
        if hasattr(self, "_avdl"):
            del self._avdl

    def bulk_index(self, documents: pd.DataFrame):
        """Indexes a DataFrame of documents."""
        
        for _, row in documents.iterrows():
            metadata_dict = row.to_dict()
            self.index(
                url=metadata_dict.get('URL'),
                content=metadata_dict.get('content'),
                metadata=metadata_dict
            )
    