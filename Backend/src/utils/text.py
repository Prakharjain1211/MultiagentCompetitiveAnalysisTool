"""
Text processing utilities for cleaning, truncating, and splitting text.

Used primarily by the scraper to normalize raw HTML and by the
synthesizer to prepare text for chunking and RAG indexing.

Functions:
    clean_html: Strip HTML tags and extract readable text.
    truncate: Safely trim text at word boundaries with an ellipsis.
    split_sentences: Segment text into sentence-level units.
"""

import re

from bs4 import BeautifulSoup


def clean_html(raw_html: str) -> str:
    """Strip HTML/XML tags and return clean, whitespace-normalized text.

    Removes non-content elements (script, style, nav, footer, header, aside)
    via BeautifulSoup's decompose(), then extracts text with a single-space
    separator and collapses all whitespace runs.

    Args:
        raw_html: Raw HTML string to be cleaned.

    Returns:
        Cleaned plain text with tags removed and whitespace normalized.
    """
    soup = BeautifulSoup(raw_html, "lxml")
    # Remove boilerplate / non-content tags that add noise.
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    # Extract text: use space separator, strip leading/trailing whitespace.
    text = soup.get_text(separator=" ", strip=True)
    # Collapse multiple spaces, newlines, tabs into single spaces.
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(text: str, max_chars: int) -> str:
    """Truncate text to a maximum character count at a word boundary.

    Ensures truncation never splits a word in the middle by using rsplit
    on the space delimiter. An ellipsis ("...") is appended when truncated.

    Args:
        text: The input string to truncate.
        max_chars: Maximum allowed character length.

    Returns:
        Truncated string ending with "..." if shortened, or the original
        string if it fits within max_chars.
    """
    if len(text) <= max_chars:
        return text
    # rsplit finds the last space within the limit to avoid word-splitting.
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def split_sentences(text: str) -> list[str]:
    """Split text into individual sentences using regex.

    Uses a lookbehind pattern to split after sentence-ending punctuation
    (. ! ?) followed by whitespace. Strips leading/trailing whitespace
    from each sentence and filters out empty strings.

    Args:
        text: Input text to be sentence-segmented.

    Returns:
        List of cleaned sentence strings.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]