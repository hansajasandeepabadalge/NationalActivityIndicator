"""
Content Parser Module
Extracted from ConfigurableScraper._extract_text() and _extract_body()

Handles:
- CSS selector-based text extraction with fallback chains
- Multi-selector body extraction with auto-cleaning
- Meta tag fallback (og:title, og:description)
- Script/style/ad removal
- Paragraph-based text assembly
"""

import logging
from typing import Optional, List, Union
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_text(
    soup: BeautifulSoup,
    selector: Optional[Union[str, list]]
) -> Optional[str]:
    """
    Extract text using CSS selector(s).

    Supports:
    - Single selector string: "h1.title"
    - Comma-separated selectors: "h1, .title, #heading"
    - List of selectors (priority order): ["h1.title", "h1", "meta[property='og:title']"]
    - Meta tag extraction: Automatically tries og:title, twitter:title as fallback

    Args:
        soup: Parsed HTML document
        selector: CSS selector string, comma-separated string, or list of selectors

    Returns:
        Extracted text or None
    """
    if not selector:
        return None

    # Convert to list for uniform processing
    selectors = []
    if isinstance(selector, list):
        selectors = selector
    elif isinstance(selector, str):
        # Split comma-separated selectors
        selectors = [s.strip() for s in selector.split(',')]
    else:
        return None

    # Try each selector in order
    for sel in selectors:
        try:
            # Check if it's a meta tag selector
            if sel.startswith('meta['):
                meta = soup.select_one(sel)
                if meta:
                    content = meta.get('content')
                    if content:
                        return content.strip()
            else:
                element = soup.select_one(sel)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
        except Exception as e:
            logger.debug(f"Selector '{sel}' failed: {e}")

    # Fallback: Try common meta tags for title/description
    if 'title' in str(selector).lower():
        for meta_sel in ["meta[property='og:title']", "meta[name='twitter:title']", "title"]:
            try:
                elem = soup.select_one(meta_sel)
                if elem:
                    text = elem.get('content') if elem.name == 'meta' else elem.get_text(strip=True)
                    if text:
                        return text.strip()
            except Exception:
                pass

    return None


def extract_body(soup: BeautifulSoup, selectors: dict) -> str:
    """
    Extract article body content with smart cleaning.

    Supports:
    - Multiple selector fallbacks (string or list)
    - Automatic removal of ads, scripts, styles
    - Paragraph-based text extraction
    - Meta description fallback

    Args:
        soup: Parsed HTML document
        selectors: Selector config dict from SourceConfig

    Returns:
        Extracted body text
    """
    body_selector = selectors.get('body', 'article, .content, .article-body, main')
    exclude_selector = selectors.get('body_exclude')

    body_text = ""

    # Convert to list if needed
    selector_list = [body_selector] if isinstance(body_selector, str) else body_selector

    # Try each selector
    for selector in selector_list:
        for sel in (selector.split(',') if isinstance(selector, str) else [selector]):
            sel = sel.strip()
            try:
                element = soup.select_one(sel)
                if element:
                    # Clone to avoid modifying original
                    element = element.__copy__()

                    # Remove scripts, styles, ads
                    for tag in element.find_all(['script', 'style', 'noscript', 'iframe']):
                        tag.decompose()

                    # Remove excluded elements
                    if exclude_selector:
                        for excluded in element.select(exclude_selector):
                            excluded.decompose()

                    # Get text with paragraph separation
                    paragraphs = element.find_all(['p', 'div'])
                    if paragraphs:
                        body_text = '\n\n'.join([
                            p.get_text(strip=True)
                            for p in paragraphs
                            if len(p.get_text(strip=True)) > 20
                        ])
                    else:
                        body_text = element.get_text(strip=True, separator='\n')

                    if len(body_text) >= 100:
                        return body_text
            except Exception as e:
                logger.debug(f"Body selector '{sel}' failed: {e}")

    # Fallback 1: Concatenate all meaningful paragraphs
    if len(body_text) < 100:
        all_paragraphs = soup.find_all('p')
        meaningful = [
            p.get_text(strip=True)
            for p in all_paragraphs
            if len(p.get_text(strip=True)) > 50
        ]
        body_text = '\n\n'.join(meaningful)

    # Fallback 2: Try meta description
    if len(body_text) < 100:
        meta_desc = soup.select_one("meta[property='og:description'], meta[name='description']")
        if meta_desc:
            body_text = meta_desc.get('content', '')

    return body_text
