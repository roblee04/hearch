# Hearch Presentation - Quick Reference Guide

## 🎤 Elevator Pitch (30 seconds)

**Hearch is a search engine designed for serendipity, not just relevance. It uses LLMs to creatively expand your queries into unexpected angles, then ranks results to favor unique, quality content over commercial spam. Instead of showing you what you already know exists, it helps you discover what you didn't know you were looking for.**

---

## 💡 Core Messages (What to Emphasize)

### 1. **The Problem is Predictability**
- Traditional search engines are too good at giving you exactly what you ask for
- This kills serendipity and discovery
- Commercial interests dominate results
- Users miss out on interesting, unexpected content

### 2. **Creativity Through Three Mechanisms**

**A. Creative Query Expansion (LLM-powered)**
- Take one query → Generate 4-5 creative alternatives
- Each explores a different angle (historical, cultural, scientific, etc.)
- Uses Ollama (local, free) or OpenAI

**B. Anti-Mainstream Ranking**
- Deliberately inverts traditional search priorities
- Penalizes ads, popups, commercial features
- Rewards unique, personal content
- Quality over popularity

**C. Human-AI Collaboration**
- Starts with manually curated "interesting" seed URLs
- Machine explores and expands at scale
- Combines human taste with computational power

### 3. **This is Computational Creativity**
- **Exploratory**: LLM navigates conceptual space around topics
- **Transformational**: Changes the rules of search (inverts values)
- **Combinational**: Merges multiple query perspectives
- **Collaborative**: Human + AI working together

### 4. **It Actually Works**
- Built and deployed working system
- Uses standard technologies (Python, Flask, scikit-learn)
- Local LLM support (no API costs or privacy concerns)
- Produces genuinely surprising, valuable results

---

## 🎯 Key Statistics & Facts to Mention

- **Query Expansion**: 1 query → 4-5 creative alternatives
- **Temperature**: 0.8 (high = more creative)
- **Penalty System**: 10× multiplier for anti-bullshit features
- **Metadata Fields**: 11 different quality signals extracted
- **Technologies**: 7 major components (Python, Flask, BM25, Ollama, etc.)
- **Architecture**: 4-layer system (UI → Expansion → Search → Fusion)

---

## 📊 Perfect Demo Sequence

### Demo 1: Query Expansion (2 minutes)
```bash
python src/microsearch/query_expansion.py
```

**What to say:**
- "Watch how the LLM takes 'potatoes' and generates creative alternatives"
- "Notice how each explores a different angle"
- "This is exploratory creativity in action"

**Expected output:**
- Historical angle: "potato cultivation throughout history"
- Cultural angle: "cultural significance of potatoes"
- Scientific angle: "unexpected uses for potatoes in science"
- Creative angle: "potatoes in literature and metaphor"

### Demo 2: Live Search (3 minutes)
```bash
python -m app.app --data-path output_with_metadata.parquet
```

**Queries to try:**
1. **"potatoes"** - Shows creative expansion clearly
2. **"machine learning"** - Shows diversity of perspectives
3. **"creativity"** - Meta and interesting

**What to point out:**
- Results are NOT the typical Wikipedia/commercial top results
- Notice personal blogs, niche sites, unique perspectives
- Point out the variety of angles covered

### Demo 3: Ranking Transparency (2 minutes)

**Compare these hypothetically:**
- Commercial site with ads → HIGH penalties → LOWER rank
- Personal blog, well-written → NO penalties → HIGHER rank
- SEO spam, thin content → VERY HIGH penalties → VERY LOW rank

**Formula to show:**
```
Final Score = √[(500 + 10×Penalties) / (1 + Relevance)]
```

**Key insight:** Lower relevance can mean higher score = surprise bias!

---

## 🗣️ Answers to Expected Questions

### Q: "How is this different from Google's 'I'm Feeling Lucky'?"
**A:** "Google's button just picks the #1 result - still optimizing for relevance. We're fundamentally changing what we optimize for. Our entire ranking algorithm is designed for surprise, not accuracy."

### Q: "Won't users want relevant results, not surprising ones?"
**A:** "For everyday searches, yes. But there's a huge use case for exploratory search - learning, research, inspiration, creativity. That's what we're targeting. It's a complement to traditional search, not a replacement."

### Q: "How do you measure if results are 'serendipitous'?"
**A:** "Great question! We focus on qualitative metrics - diversity of sources, anti-popularity ratio, user engagement time. Quantifying serendipity is an open research problem, but users know it when they experience it."

### Q: "Why not just use Google with creative queries?"
**A:** "Two reasons: 1) Google still ranks for relevance even with creative queries, so you get predictable results. 2) Our penalty system actively demotes commercial content that Google promotes."

### Q: "What about hallucinations in query expansion?"
**A:** "Since we're using LLMs for query generation, not factual answers, hallucinations are less critical. If the LLM generates a weird query, we just search for it - the search engine handles accuracy."

### Q: "Can this scale to the full web?"
**A:** "Technically yes, but that's not our goal. We're deliberately curated. Marginalia Search does something similar at ~500M pages. The magic is in selection, not scale."

### Q: "How long does query expansion take?"
**A:** "With Ollama locally: 2-5 seconds. With OpenAI: 1-3 seconds. We could cache common expansions or do it asynchronously for better UX."

---

## 🎨 Computational Creativity Buzzwords to Use

Use these naturally throughout your presentation:

- **Exploratory creativity** - Navigating conceptual spaces
- **Transformational creativity** - Changing the rules
- **Combinational creativity** - Novel combinations
- **Conceptual blending** - Merging different domains
- **Divergent thinking** - Multiple directions vs. one answer
- **Serendipity** - Valuable accidents
- **Anti-mainstream bias** - Deliberately resisting dominant patterns
- **Human-AI collaboration** - Augmented intelligence
- **Computational serendipity** - Systematized surprise
- **Creative reframing** - Same topic, new perspective

---

## 🚀 Strong Opening Lines (Choose One)

1. "What if your search engine was trying to surprise you, not just answer your question?"

2. "Google is great at finding what you're looking for. Hearch is great at finding what you didn't know existed."

3. "We built a search engine that deliberately gives you the wrong answer - and that's exactly the right thing to do."

4. "The best discoveries come from asking better questions. We use AI to ask those questions for you."

5. "Traditional search engines kill serendipity. We bring it back, computationally."

---

## 🎬 Strong Closing Lines (Choose One)

1. "In a world of algorithmic echo chambers, we're building tools for algorithmic exploration."

2. "The future of search isn't finding the right answer faster - it's asking better questions."

3. "We've shown that creativity isn't just for art - it's for information systems too."

4. "Hearch proves that the most creative search results come from deliberately NOT giving users what they asked for."

5. "This is just the beginning. Imagine every information system designed for serendipity, not just efficiency."

---

## ⏱️ Timing Suggestions

**For 10-minute presentation:**
- Introduction & Problem (2 min)
- How Hearch Works (3 min)
- Demo (3 min)
- Computational Creativity Aspects (1.5 min)
- Conclusion (0.5 min)

**For 15-minute presentation:**
- Introduction & Problem (2.5 min)
- How Hearch Works (4 min)
- Demo (4 min)
- Computational Creativity Deep Dive (3 min)
- Future Directions (1 min)
- Conclusion (0.5 min)

**For 20-minute presentation:**
- Introduction & Problem (3 min)
- Related Work (2 min)
- How Hearch Works (5 min)
- Demo (5 min)
- Computational Creativity Deep Dive (3 min)
- Future Directions (1.5 min)
- Conclusion (0.5 min)

---

## 📝 Slide Flow Checklist

Make sure your presentation flows like this:

1. ✅ **Hook** - Start with interesting question/problem
2. ✅ **Problem** - Why traditional search is predictable
3. ✅ **Solution** - What Hearch does differently
4. ✅ **How It Works** - Technical overview (3 mechanisms)
5. ✅ **Demo** - Show it working (most important!)
6. ✅ **Creativity** - Connect to computational creativity concepts
7. ✅ **Impact** - Why this matters
8. ✅ **Future** - Where this could go
9. ✅ **Conclusion** - Memorable takeaway

---

## 🎯 What to Practice

1. **Query expansion explanation** (30 seconds)
   - "The LLM takes your query and generates creative alternatives"
   - Show example with "potatoes"

2. **Ranking algorithm explanation** (45 seconds)
   - "We invert traditional search - lower relevance can mean higher score"
   - Show formula visually

3. **Demo transitions** (smooth and quick)
   - Have terminal already open
   - Have commands ready to copy-paste
   - Know what output to expect

4. **Creativity framework connection** (1 minute)
   - "This is exploratory creativity because..."
   - "This is transformational because..."
   - "This combines human and AI..."

---

## 💪 Confidence Boosters

**You built something real that works.**
- Not just a paper concept
- Not just a prototype
- A functional, deployed system

**You combined multiple advanced techniques:**
- LLM integration (Ollama + OpenAI)
- Custom ranking algorithms
- Web crawling and indexing
- Modern web interface

**You have a clear creativity narrative:**
- Exploratory: LLM query expansion
- Transformational: Inverted ranking
- Combinational: Result fusion
- Collaborative: Human-AI partnership

**You're solving a real problem:**
- Search is too predictable
- Commercial interests dominate
- Serendipity is valuable but rare

---

## 🎁 Bonus: One-Liners for Each Slide

Use these as slide subtitles or transition phrases:

1. "Making the web interesting again"
2. "Predictability is the enemy of discovery"
3. "Serendipity as a service"
4. "Asking better questions, computationally"
5. "When low relevance is high value"
6. "The algorithm that inverts the algorithm"
7. "Human taste meets machine scale"
8. "Four types of creativity, one search engine"
9. "Where 'potato' becomes a journey"
10. "The anti-Google for good reason"

---

## 📱 Last-Minute Checklist

**30 minutes before:**
- [ ] Ollama running (`ollama serve`)
- [ ] Model downloaded (`ollama list` to verify)
- [ ] App tested (`python -m app.app --data-path output_with_metadata.parquet`)
- [ ] Browser open to localhost:8000
- [ ] Terminal ready with commands

**5 minutes before:**
- [ ] Deep breath
- [ ] Water nearby
- [ ] Slides ready
- [ ] Confidence high
- [ ] Ready to show something amazing!

---

## 🌟 Remember

**Your project is genuinely creative and novel.**

You're not just applying existing techniques - you're combining them in new ways to solve a real problem. You've built a working system that demonstrates computational creativity in a practical, impactful way.

**The key insight is powerful:**
> "The best search results aren't always the most relevant ones."

This challenges decades of search engine design. That's bold, that's creative, and that's exactly what computational creativity is about.

**You've got this! 🚀**

---

## 🔗 Quick Links for Reference

- **GitHub**: https://github.com/roblee04/hearch
- **Marginalia Search**: https://search.marginalia.nu/
- **Wiby**: https://wiby.me/
- **Ollama**: https://ollama.ai/
- **Boden on Creativity**: Exploratory, Combinational, Transformational

---

Good luck with your presentation! You've built something impressive. 🎉

