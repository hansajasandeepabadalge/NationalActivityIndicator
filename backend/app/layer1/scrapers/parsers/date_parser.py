"""
Date Parser Module
Extracted from ConfigurableScraper._parse_date()

Handles:
- Configured date format from SourceConfig
- ISO8601 / RFC2822 formats
- Relative dates ("2 hours ago", "yesterday")
- 11 common date formats
- Timezone prefix/suffix cleanup
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def parse_date(date_str: Optional[str], selectors: dict) -> Optional[datetime]:
    """
    Parse date string to datetime with enhanced format support.

    Args:
        date_str: Raw date string from article
        selectors: Selector config dict (for date_format)

    Returns:
        Parsed datetime or None
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Clean up common prefixes/suffixes
    date_str = re.sub(
        r'^(Published|Posted|Updated|Date|On):\s*', '', date_str, flags=re.IGNORECASE
    )
    date_str = re.sub(
        r'\s+(GMT|UTC|EST|PST).*$', '', date_str, flags=re.IGNORECASE
    )
    date_str = date_str.strip()

    # Handle relative dates
    relative_patterns = [
        (r'(\d+)\s*minutes?\s*ago', lambda m: datetime.utcnow() - timedelta(minutes=int(m.group(1)))),
        (r'(\d+)\s*hours?\s*ago', lambda m: datetime.utcnow() - timedelta(hours=int(m.group(1)))),
        (r'(\d+)\s*days?\s*ago', lambda m: datetime.utcnow() - timedelta(days=int(m.group(1)))),
        (r'yesterday', lambda m: datetime.utcnow() - timedelta(days=1)),
        (r'today', lambda m: datetime.utcnow()),
    ]

    for pattern, handler in relative_patterns:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            try:
                return handler(match)
            except Exception:
                pass

    # Try configured format first
    date_format = selectors.get('date_format')
    if date_format and date_format.lower() != 'iso8601':
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass

    # Try ISO8601 formats
    iso_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",      # 2025-12-09T10:30:00.000Z
        "%Y-%m-%dT%H:%M:%SZ",         # 2025-12-09T10:30:00Z
        "%Y-%m-%dT%H:%M:%S",          # 2025-12-09T10:30:00
        "%Y-%m-%d %H:%M:%S",          # 2025-12-09 10:30:00
    ]

    for fmt in iso_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # Try common formats
    common_formats = [
        "%B %d, %Y",              # December 9, 2025
        "%d %B %Y",               # 9 December 2025
        "%b %d, %Y",              # Dec 9, 2025
        "%d %b %Y",               # 9 Dec 2025
        "%Y-%m-%d",               # 2025-12-09
        "%d/%m/%Y",               # 09/12/2025
        "%m/%d/%Y",               # 12/09/2025
        "%B %d, %Y %I:%M %p",     # December 9, 2025 10:30 AM
        "%d-%m-%Y",               # 09-12-2025
        "%Y.%m.%d",               # 2025.12.09
        "%d.%m.%Y",               # 09.12.2025
    ]

    for fmt in common_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    logger.debug(f"Could not parse date: {date_str}")
    return None
