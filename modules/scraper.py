# modules/scraper.py

import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from langchain.docstore.document import Document

load_dotenv()  # Loads SERPAPI_API_KEY from .env

def scrape_web_results(query, max_results=5):
    """
    Perform a real-time Google search using SerpAPI.
    Returns a list of LangChain Document objects with title+snippet and source link.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("❌ SERPAPI_API_KEY is not set in .env file.")

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": max_results
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        print(f"❌ Error fetching SerpAPI results: {e}")
        return []

    documents = []
    for res in results.get("organic_results", []):
        title = res.get("title", "")
        snippet = res.get("snippet", "")
        link = res.get("link", "")
        content = f"{title}\n{snippet}"
        documents.append(Document(page_content=content, metadata={"source": link}))

    return documents
