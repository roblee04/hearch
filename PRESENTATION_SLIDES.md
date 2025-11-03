# Hearch: Serendipitous Search Through Computational Creativity
## Slide Deck Outline

---

## SLIDE 1: Title
**Hearch: A Serendipitous Search Engine**

*Finding what you weren't looking for, computationally.*

By: Robin Lee & Harsh  
Course: Computational Creativity  
November 2025

---

## SLIDE 2: The Problem

### Traditional Search Engines
- Optimized for **relevance** and **popularity**
- Return predictable, mainstream results
- Commercial and SEO-dominated
- No room for discovery or surprise

### The Question
**"What if search was designed for serendipity, not just accuracy?"**

---

## SLIDE 3: What is Hearch?

A search engine that prioritizes:
- 🎲 **Serendipity** - Unexpected but valuable discoveries
- 🌈 **Diversity** - Multiple perspectives and angles
- ✨ **Quality** - Well-written, thoughtful content
- 🎨 **Creativity** - Alternative viewpoints

**Core Philosophy**: The best results aren't always the most obvious ones.

---

## SLIDE 4: Computational Creativity in Action

### Three Creative Mechanisms:

**1. Creative Query Expansion**
```
"potatoes" →
  • "potato cultivation throughout history"
  • "cultural significance of potatoes worldwide"
  • "unexpected uses for potatoes in science"
  • "potatoes in literature and metaphor"
```

**2. Anti-Mainstream Ranking**
- Penalizes ads, popups, commercial content
- Rewards unique, personal perspectives

**3. Curated Discovery**
- Human-selected interesting seeds
- Machine-scale exploration

---

## SLIDE 5: How Query Expansion Works

```
┌─────────────┐
│ User Query  │  "potatoes"
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  LLM (Ollama/OpenAI)   │  High temperature (0.8)
│  Creative Reframing     │  Divergent thinking
└──────┬──────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  4-5 Alternative Queries         │
│  • Historical angle               │
│  • Scientific angle               │
│  • Cultural angle                 │
│  • Metaphorical angle            │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Search All Queries in Parallel  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Merge & Rank with Diversity     │
│  Serendipitous Results ✨        │
└──────────────────────────────────┘
```

**Creativity Type**: Exploratory + Combinational

---

## SLIDE 6: Marginalia-Inspired Ranking

### Traditional vs Hearch

| Traditional Search | Hearch |
|-------------------|---------|
| ✓ High traffic | ✓ Unique content |
| ✓ SEO optimized | ✓ Personal blogs |
| ✓ Commercial sites | ✗ Anti-ads penalty |
| ✓ Wikipedia first | ✓ Diverse sources |

### The Formula
```
Final Score = √[(500 + Penalties) / (1 + Relevance)]
```

**Key Insight**: Lower "relevance" can mean higher score!  
→ Creates surprise bias

---

## SLIDE 7: System Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Query Expansion    │  ← Ollama/OpenAI LLM
│  (Creative Layer)   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Search Engine Core │
│  • BM25 Baseline    │
│  • Serendipity Rank │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Result Fusion      │
│  (Diversity Merge)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  🎨 Serendipitous   │
│     Results         │
└─────────────────────┘
```

---

## SLIDE 8: Data Pipeline

**Step 1: Curated Seeds**
- Personal blogs, niche sites, creative portfolios
- Hand-picked for "interestingness"

**Step 2: Intelligent Crawling**
- Depth-based exploration
- Local + external links
- BFS/DFS hybrid

**Step 3: Rich Metadata Extraction**
- Content + Title + Headings
- Quality metrics (sentence length, doc size)
- "Anti-bullshit" features (ads, popups, trackers)

**Step 4: Parquet Storage**
- Efficient, queryable dataset

---

## SLIDE 9: Computational Creativity Framework

### 1. Exploratory Creativity
**Query Expansion**: Navigate conceptual space around a topic
- LLM explores different angles
- High temperature = more creative

### 2. Transformational Creativity
**Value Inversion**: Change the rules of search
- Popularity → Uniqueness
- Authority → Interestingness

### 3. Combinational Creativity
**Result Fusion**: Novel combinations of existing elements
- Merge multiple query perspectives
- Diversity-aware ranking

### 4. Collaborative Creativity
**Human-AI Partnership**: Human taste + Machine scale
- Manual curation + Computational expansion

---

## SLIDE 10: Example - "Machine Learning"

### Traditional Search Results:
1. Wikipedia - Machine Learning
2. Coursera - ML Course
3. TensorFlow - Official Docs
4. Medium - "Intro to ML"
5. AWS - ML Services

### Hearch Results (with expansion):
1. "Why Machine Learning Projects Fail" - Personal blog
2. "ML in Medieval Literature Analysis" - Niche academic
3. "Teaching ML to Elementary Students" - Education blog
4. "The Philosophy of Neural Networks" - Essay
5. "Analog Machine Learning with Marbles" - DIY project

**Difference**: Unexpected angles, diverse perspectives, creative connections

---

## SLIDE 11: Technical Stack

| Component | Technology |
|-----------|-----------|
| **Core Engine** | Python 3.10+ |
| **Web Framework** | Flask |
| **Search Algorithm** | BM25 (scikit-learn) |
| **Query Expansion** | Ollama (local) or OpenAI |
| **Data Storage** | Parquet (pandas) |
| **Crawling** | Requests + BeautifulSoup |
| **Frontend** | Modern HTML/CSS/JS |

### Key Features:
- ✅ Local LLM support (Ollama) - Free!
- ✅ Automatic fallback if no LLM
- ✅ Transparent ranking algorithm
- ✅ Extensible and modular

---

## SLIDE 12: Live Demo Points

### Demo 1: Query Expansion in Action
```bash
python src/microsearch/query_expansion.py
```
Watch the LLM generate creative alternatives in real-time!

### Demo 2: Search Comparison
Search "potatoes" and see:
- Original query results
- Expanded query results  
- Merged, diverse final ranking

### Demo 3: Ranking Transparency
Show how penalties affect scores for:
- Ad-heavy site: LOW score
- Personal blog: HIGH score
- SEO spam: VERY LOW score

---

## SLIDE 13: Why This Matters for Computational Creativity

### 1. **Creativity as a Primary Goal**
Not a side effect - serendipity is the optimization target

### 2. **LLMs for Creative Reframing**
Using AI not for answers, but for better questions

### 3. **Algorithmic Counter-Culture**
Deliberately resisting mainstream bias in AI systems

### 4. **Human-AI Collaboration Model**
Neither fully automated nor fully manual
- Human: Taste and curation
- Machine: Scale and exploration
- Together: Discovery

---

## SLIDE 14: Evaluation

### Qualitative Success Metrics:
✓ **Surprise** - "I didn't expect this result!"  
✓ **Diversity** - Multiple perspectives represented  
✓ **Quality** - Well-written, thoughtful content  
✓ **Discovery** - "I learned something new"  

### Potential Quantitative Metrics:
- Result diversity score (cosine distance)
- Anti-popularity ratio (% from low-traffic sites)
- Query expansion creativity (semantic distance)
- User engagement time (proxy for interest)

### Known Limitations:
- Small index (not web-scale)
- Single-word bias in indexing
- "Interesting" is subjective

---

## SLIDE 15: Novel Contributions

### To Computational Creativity:
1. **Serendipity as an optimization target** in information systems
2. **LLMs for conceptual exploration** beyond Q&A
3. **Deliberate anti-mainstream bias** in ranking
4. **Human-AI creative partnership** model

### To Search Engines:
1. Quality over quantity ranking
2. Transparent, explainable scoring
3. Local LLM integration (privacy + cost)
4. Curated discovery at scale

---

## SLIDE 16: Related Work & Inspiration

**MarginaliaSearch**
- Anti-commercial search engine
- Quality-focused ranking
- Inspiration for our penalty system

**Wiby.me**
- "Surprise me" button for old web
- Random discovery model

**StumbleUpon (RIP)**
- The original serendipity engine
- User-curated discovery

**Boden's Creativity Theory**
- Exploratory, Combinational, Transformational
- Framework for our creativity types

---

## SLIDE 17: Future Directions

### Short-term:
- 🎯 Adaptive serendipity (learn user preferences)
- 📊 User study on discovery effectiveness
- 🔄 Real-time crawling improvements

### Long-term:
- 🖼️ Multi-modal creativity (images, video, audio)
- 🤝 Collaborative filtering ("similar surprises")
- 🌐 Meta-search layer (creative proxy for Google/Bing)
- 🎮 Gamification (serendipity scores, discovery badges)

### Research Questions:
- Can we quantify serendipity?
- What's the optimal balance of surprise vs relevance?
- How do users discover they like something unexpected?

---

## SLIDE 18: Key Takeaways

### 1. **The Problem**
Traditional search is predictable and commercial

### 2. **The Solution**  
Computational creativity through serendipity-optimized search

### 3. **The Innovation**
LLM query expansion + anti-mainstream ranking

### 4. **The Impact**
Users discover valuable content they wouldn't find otherwise

### 5. **The Future**
A model for creative information systems

---

## SLIDE 19: Conclusion

**Core Insight:**
> "The most creative search results often come from deliberately NOT giving users exactly what they asked for."

**What We Built:**
- A working search engine with computational creativity
- LLM-powered query expansion (local & free)
- Quality-over-popularity ranking
- Human-AI collaborative discovery

**What We Learned:**
- Creativity can be systematized (but not mechanized)
- Serendipity needs both randomness and curation
- AI amplifies human taste at scale

**Tagline:** *Finding what you weren't looking for, computationally.*

---

## SLIDE 20: Thank You + Demo

### Try Hearch:
```bash
# Install
git clone https://github.com/roblee04/hearch.git
pip install .

# Run Ollama (optional but recommended)
ollama pull llama3.2
ollama serve

# Launch
python -m app.app --data-path output_with_metadata.parquet
```

Visit: http://127.0.0.1:8000/

### Questions?

**GitHub**: https://github.com/roblee04/hearch  
**Authors**: Robin Lee & Harsh  
**Course**: Computational Creativity  

---

## BONUS SLIDE: Technical Deep Dive (if asked)

### Ranking Formula Explained:

```
Final Score = √[(1 + 500 + 10×P) / (1 + R)]

Where:
R = Relevance Score (BM25 + bonuses)
P = Penalties (ads, trackers, low quality)
```

**Why this works:**
- √ spreads scores nicely
- Inversion (1/R) rewards lower relevance
- Constant 500 ensures numeric stability
- Penalty multiplier (10×P) strongly discourages spam

**Example Scores:**
- High relevance (R=100), no penalties (P=0): Score = 2.45
- Low relevance (R=10), no penalties (P=0): Score = 6.71 ← HIGHER!
- High relevance (R=100), high penalties (P=50): Score = 6.56
- Perfect commercial spam (R=1000, P=100): Score = 3.53

→ Underdog bonus + spam penalty = Serendipity!

---

## APPENDIX: Demo Queries to Try

1. **"potatoes"** - Shows creative expansion
2. **"machine learning"** - Diverse perspectives
3. **"philosophy"** - Non-mainstream sources
4. **"creativity"** - Meta!
5. **"weird hobbies"** - Pure serendipity

Each should surface unexpected but valuable results!

