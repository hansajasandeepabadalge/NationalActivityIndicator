"""
Link Extraction Module
Extracted from ConfigurableScraper._extract_article_links()

Handles:
- CSS selector-based link extraction
- Regex pattern matching on all links
- Heuristic fallback (links with 5+ word text)
- Relative → absolute URL conversion
"""

import re
import logging
from typing import List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_article_links(
    soup: BeautifulSoup,
    base_url: str,
    selectors: dict,
    source_base_url: str
) -> List[str]:
    """
    Extract article links from list page.

    Uses article_link_selector if provided, otherwise falls back to
    pattern matching on all links.

    Args:
        soup: Parsed HTML of list page
        base_url: URL of the list page
        selectors: Selector config dict from SourceConfig
        source_base_url: Base URL of the source (for filtering)

    Returns:
        List of absolute article URLs
    """
    links = set()

    # Method 1: Use CSS selector if provided
    link_selector = selectors.get('article_link_selector')
    if link_selector:
        for a in soup.select(link_selector):
            href = a.get('href')
            if href:
                full_url = make_absolute_url(href, base_url)
                if full_url:
                    links.add(full_url)

    # Method 2: Use pattern matching on all links
    pattern = selectors.get('article_link_pattern')
    if pattern and not links:
        regex = re.compile(pattern)
        for a in soup.find_all('a', href=True):
            href = a['href']
            if regex.search(href):
                full_url = make_absolute_url(href, base_url)
                if full_url:
                    links.add(full_url)

    # Method 3: Fallback - look for links with meaningful text
    if not links:
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            # Heuristic: links with 5+ word text are likely articles
            if len(text.split()) >= 5 and not any(
                x in href.lower() for x in ['login', 'signup', 'contact', 'about']
            ):
                full_url = make_absolute_url(href, base_url)
                if full_url and source_base_url in full_url:
                    links.add(full_url)

    return list(links)


def make_absolute_url(href: str, base_url: str) -> Optional[str]:
    """Convert relative URL to absolute."""
    if not href:
        return None

    # Already absolute
    if href.startswith('http'):
        return href

    # Protocol-relative
    if href.startswith('//'):
        return 'https:' + href

    # Root-relative
    if href.startswith('/'):
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{href}"

    # Relative
    return base_url.rstrip('/') + '/' + href.lstrip('/')
