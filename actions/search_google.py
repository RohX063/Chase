from duckduckgo_search import DDGS

def search_google(query):
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            title = r.get("title", "")
            body = r.get("body", "")
            results.append(f"{title}: {body}")

    return results
