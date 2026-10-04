import re

from includes.schemas.word.hindi_stopwords import HINDI_STOP_WORDS
from includes.schemas.word.english_stopwords import ENGLISH_STOP_WORDS


async def get_tag(item: list = None):
    if not item:
        return []

    # Hindi + English stop words
    stop_words = HINDI_STOP_WORDS | {
        word.lower() for word in ENGLISH_STOP_WORDS
    }

    keywords = []
    seen = set()

    for sentence in item:
        if not sentence:
            continue

        # Sentence ko words mein split karein
        words = re.findall(r"[a-zA-Z\u0900-\u097F]+", str(sentence))
        for word in words:

            if not word:
                continue

            normalized = word.lower().strip()

            # Stop word
            if normalized in stop_words:
                continue

            # Number
            if normalized.isdigit():
                continue

            # Single character
            if len(normalized) <= 1:
                continue

            # Duplicate
            if normalized in seen:
                continue

            seen.add(normalized)

            # Original word preserve karein
            keywords.append(word)

    return keywords
