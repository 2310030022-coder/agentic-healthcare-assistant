
import re
import requests
import xml.etree.ElementTree as ET

from urllib.parse import urlparse
from html import unescape


MEDLINE_API = (
    "https://wsearch.nlm.nih.gov/ws/query"
)

ALLOWED_DOMAINS = {
    "medlineplus.gov",
    "www.medlineplus.gov"
}


def clean_html(text):
    """Remove markup from medical search snippets."""
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return " ".join(text.split())


def trusted_medical_url(url):
    """Allow only HTTPS links to approved domains."""
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme == "https"
            and parsed.hostname in ALLOWED_DOMAINS
        )
    except (ValueError, TypeError):
        return False


def search_medlineplus(query, max_results=5):
    """
    Search MedlinePlus health topics through
    the U.S. National Library of Medicine API.
    """
    if not query or not query.strip():
        return []

    max_results = min(max(int(max_results), 1), 10)

    params = {
        "db": "healthTopics",
        "term": query.strip(),
        "retmax": max_results
    }

    try:
        response = requests.get(
            MEDLINE_API,
            params=params,
            timeout=15,
            headers={
                "User-Agent": (
                    "AgenticHealthcareCapstone/1.0"
                )
            }
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)
        results = []

        for document in root.findall(".//document"):
            url = document.attrib.get("url", "")

            if not trusted_medical_url(url):
                continue

            title = ""
            summary = ""

            for content in document.findall("content"):
                name = content.attrib.get("name", "")
                value = clean_html(
                    "".join(content.itertext())
                )

                if name == "title":
                    title = value
                elif name in ("FullSummary", "snippet"):
                    summary = value

            if title:
                results.append({
                    "title": title,
                    "url": url,
                    "content": summary,
                    "source": "MedlinePlus"
                })

        return results[:max_results]

    except (
        requests.RequestException,
        ET.ParseError,
        ValueError
    ):
        return []


def retrieve_medical_information(query, max_results=5):
    """
    Retrieve verified-source medical search results.
    """
    results = search_medlineplus(
        query,
        max_results
    )

    return {
        "query": query,
        "sources": results,
        "success": bool(results),
        "source_count": len(results)
    }


def format_medical_sources(sources):
    """Prepare retrieved medical sources for RAG."""
    if not sources:
        return (
            "No verified medical information was "
            "retrieved. Do not generate unsupported "
            "medical claims."
        )

    sections = []

    for i, source in enumerate(sources, start=1):
        sections.append(
            f"Source {i}\n"
            f"Title: {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Content: {source['content']}"
        )

    return "\n\n".join(sections)
