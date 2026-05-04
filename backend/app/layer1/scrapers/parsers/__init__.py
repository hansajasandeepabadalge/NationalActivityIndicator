"""
Parsers Package
Extracted from ConfigurableScraper for single-responsibility design.

Each module handles one parsing concern:
- link_extractor: Article link discovery (CSS, regex, heuristic)
- content_parser: Text and body extraction with fallback chains
- date_parser: Date string parsing (15+ formats, relative dates)
- image_extractor: Image extraction with lazy-load support
"""

from app.layer1.scrapers.parsers.link_extractor import extract_article_links, make_absolute_url
from app.layer1.scrapers.parsers.content_parser import extract_text, extract_body
from app.layer1.scrapers.parsers.date_parser import parse_date
from app.layer1.scrapers.parsers.image_extractor import extract_images

__all__ = [
    'extract_article_links',
    'make_absolute_url',
    'extract_text',
    'extract_body',
    'parse_date',
    'extract_images',
]
