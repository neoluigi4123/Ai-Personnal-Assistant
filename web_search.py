"""
Main Llm Function Script
"""
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
from readability import Document

def browse(query: str, num_results: int = 5):
    query = query.strip()

    if query.lower().startswith(("http://", "https://")):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(query, headers=headers, timeout=10)
            response.raise_for_status()

            # Use Readability to extract the main article
            doc = Document(response.text)
            html = doc.summary()

            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            return text[:1000]

        except Exception as e:
            return f"Error: {e}"

    else:
        results = DDGS().text(query, max_results=num_results)
        return {"query": query, "results": results}