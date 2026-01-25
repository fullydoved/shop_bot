"""Web search and URL fetch services."""

import requests
from urllib.parse import urlparse


def search_web(query: str, max_results: int = 3) -> list[dict]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-5)

    Returns:
        List of dicts with title, url, snippet

    Raises:
        ValueError: If query is empty
        requests.RequestException: If search fails
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    max_results = min(max(1, max_results), 5)

    from ddgs import DDGS

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        {
            'title': r.get('title', ''),
            'url': r.get('href', ''),
            'snippet': r.get('body', ''),
        }
        for r in results
    ]


def fetch_url(url: str) -> dict:
    """Fetch a URL and extract text content.

    Args:
        url: Full URL to fetch

    Returns:
        Dict with title, content, content_type

    Raises:
        ValueError: If URL is invalid
        requests.RequestException: If fetch fails
    """
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"URL must be http or https: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; BEAVS/1.0; +shop-assistant)',
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    content_type = response.headers.get('Content-Type', '').lower()

    # Handle HTML content
    if 'text/html' in content_type:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Get title
        title = ''
        if soup.title:
            title = soup.title.get_text(strip=True)

        # Get main content (prefer article/main, fallback to body)
        main_content = soup.find('article') or soup.find('main') or soup.find('body')

        if main_content:
            # Get text, collapse whitespace
            text = main_content.get_text(separator=' ', strip=True)
            # Collapse multiple spaces/newlines
            text = ' '.join(text.split())
        else:
            text = ''

        # Truncate for token efficiency
        max_chars = 1500
        if len(text) > max_chars:
            text = text[:max_chars] + '...'

        return {
            'title': title,
            'content': text,
            'content_type': 'html',
        }

    # Handle plain text
    elif 'text/plain' in content_type:
        text = response.text[:1500]
        if len(response.text) > 1500:
            text += '...'

        return {
            'title': '',
            'content': text,
            'content_type': 'text',
        }

    # Other content types - just report what it is
    else:
        return {
            'title': '',
            'content': f'Content type: {content_type} (not text/html)',
            'content_type': content_type.split(';')[0],
        }
