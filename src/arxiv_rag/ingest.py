"""Fetch papers from the arXiv API."""

import xml.etree.cElementTree as ET
import httpx

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}

def fetch_papers(category: str, max_results: int) -> list[dict]:
    """Fetch latest papers from an arXiv category."""
    params = {
        "search_query": f"cat:{category}",
        "start":0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    
    response = httpx.get(ARXIV_API_URL, params=params, timeout=30.0)
    response.raise_for_status()
    
    return parse_atom_feed(response.text)

def parse_atom_feed(xml_text: str) -> list[dict]:
    """Parse arXiv's Atom XML response into a list of paper dicts."""
    root = ET.fromstring(xml_text)
    papers = []
    
    for entry in root.findall("atom:entry", ATOM_NS):
        arxiv_url = entry.find("atom:id",ATOM_NS).text
        # "http://arxiv.org/abs/2401.12345v1" -> "2401.12345"
        arxiv_id = arxiv_url.split("/abs/")[-1].split("v")[0]
        
        title = entry.find("atom:title", ATOM_NS).text.strip()
        abstract = entry.find("atom:summary", ATOM_NS).text.strip()
        published = entry.find("atom:published", ATOM_NS).text
        
        authors = [
            author.find("atom:name", ATOM_NS).text
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        
        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "published": published,
        })
    return papers
    
def main() -> None:
    """Fetch 10 latest cs.LG papers and print their titles."""
    papers = fetch_papers(category = "cs.LG", max_results=10)
    print(f"Fetched {len(papers)} papers:\n")
    for i, paper in enumerate(papers, start=1):
        print(f"{i}. [{paper['arxiv_id']}] {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")
        print(f"   Published: {paper['published']}\n")
        
if __name__ == "__main__":
    main()