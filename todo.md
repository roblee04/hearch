
# FOCUS
- NICE COOL FRONTEND :D
- QUERY EXPANSION @ app.py
- Expanding + crawling dataset from seeds.txt. (will take a good amount of time!)
- Im thinking that the number of indexed domains can be ~10,000 for a proof of concept


# crawler.py
- find better seed domains? or just shotgun it with cpu time

# engine.py
- double check marginalia weighting implementation

# app.py

- add query expansion with LLMs (with weights, maybe just 2-3 xtra queries) \
--> should be using an openai compatible wrapper (ollama / openrouter) \
--> augment query maybe 2 - 3 times, should be a simple aggregations of query(new_generated_query) \
--> probably should weight initial query higher perhaps * 40% (out of 100% total), other 3 queries can be 20% \

- Note, prompting can be finicky, so its probably good to use pydantic / data validation library
- example prompting:
- You are going to query a search engine. Find relevant, but serendipitous queries. Return as a list of strings.
- You are a professional query maker. Your audience is a interdisciplinary class of graduate students taking Computational Creativity. Given a query, return queries that would bring the most serendipitous / surprising results.
- You are a genius, but starving artist. Given a query, augment it so that the new query would bring the most interesting result in a search engine.


- add more information (metadata?) that can be exposed via api?
