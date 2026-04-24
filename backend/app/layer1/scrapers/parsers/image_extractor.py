"""
Image Extraction Module
Extracted from ConfigurableScraper._extract_images()

Handles:
- Standard src attribute extraction
- Lazy loading: data-src, data-lazy-src, data-original
- Srcset parsing
- OpenGraph image fallback
- Data URI filtering
"""

import logging
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_images(
    soup: BeautifulSoup,
    selectors: dict,
    base_url: str
) -> List[dict]:
    """
    Extract images from article with lazy-loading support.

    Args:
        soup: Parsed HTML document
        selectors: Selector config dict from SourceConfig
        base_url: Base URL of the source for resolving relative URLs

    Returns:
        List of dicts with 'url' and 'alt' keys (max 5)
    """
    images = []
    img_selector = selectors.get('image', 'article img, .content img')

    # Convert to list if needed
    selector_list = [img_selector] if isinstance(img_selector, str) else img_selector

    try:
        for selector in selector_list:
            for sel in (selector.split(',') if isinstance(selector, str) else [selector]):
                for img in soup.select(sel.strip())[:5]:  # Limit to 5 images
                    # Try multiple src attributes (lazy loading support)
                    src = (img.get('src') or
                           img.get('data-src') or
                           img.get('data-lazy-src') or
                           img.get('data-original') or
                           img.get('data-lazy'))

                    # Try srcset if no src found
                    if not src:
                        srcset = img.get('srcset')
                        if srcset:
                            # Parse srcset and get first URL
                            src = srcset.split(',')[0].strip().split()[0]

                    if src and not src.startswith('data:'):  # Skip data URIs
                        # Make absolute URL
                        if not src.startswith('http'):
                            src = urljoin(base_url, src)

                        images.append({
                            "url": src,
                            "alt": img.get('alt', '')
                        })

                if images:  # Stop if we found images
                    break

            if images:
                break

        # Fallback: Try OpenGraph image
        if not images:
            og_img = soup.select_one("meta[property='og:image']")
            if og_img:
                src = og_img.get('content')
                if src:
                    images.append({"url": src, "alt": "OpenGraph image"})

    except Exception as e:
        logger.debug(f"Image extraction failed: {e}")

    return images[:5]  # Final limit to 5
