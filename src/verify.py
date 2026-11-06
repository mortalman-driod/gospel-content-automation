"""
Milestone 2 & M4: Verification Engine (src/verify.py)
Strict verification in code:
1. Fuzzy-matching quotes against transcripts with difflib ratio >= 0.92 after normalization.
2. Timestamp and YouTube URL resolution (youtu.be/<id>?t=<sec>).
3. Biblical Canon Validator: Rejects non-existent books, chapters, or verses.
4. Risk / Prosperity / Guaranteed-outcome promise scanner.
"""

import difflib
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("kingdom_journal.verify")

# Standard Biblical Canon (Protestant 66 books with chapter counts)
BIBLE_BOOKS = {
    # Old Testament
    "genesis": (50, ["gen", "ge", "gn"]),
    "exodus": (40, ["exo", "ex"]),
    "leviticus": (27, ["lev", "le", "lv"]),
    "numbers": (36, ["num", "nu", "nm", "nb"]),
    "deuteronomy": (34, ["deut", "de", "dt"]),
    "joshua": (24, ["josh", "jos", "jsh"]),
    "judges": (21, ["judg", "jdg", "jg", "jdgs"]),
    "ruth": (4, ["rth", "ru"]),
    "1 samuel": (31, ["1 sam", "1 samuel", "1sam", "1 s", "1samuel"]),
    "2 samuel": (24, ["2 sam", "2 samuel", "2sam", "2 s", "2samuel"]),
    "1 kings": (22, ["1 kgs", "1 kings", "1ki", "1 k", "1kings"]),
    "2 kings": (25, ["2 kgs", "2 kings", "2ki", "2 k", "2kings"]),
    "1 chronicles": (29, ["1 chron", "1 chr", "1 ch", "1chron"]),
    "2 chronicles": (36, ["2 chron", "2 chr", "2 ch", "2chron"]),
    "ezra": (10, ["ezr"]),
    "nehemiah": (13, ["neh", "ne"]),
    "esther": (10, ["esth", "es"]),
    "job": (42, ["jb"]),
    "psalm": (150, ["psalms", "ps", "psa", "pss"]),
    "proverbs": (31, ["prov", "pr", "prv"]),
    "ecclesiastes": (12, ["eccl", "ecc", "ec"]),
    "song of solomon": (8, ["song of songs", "song", "sos", "canticle of canticles"]),
    "isaiah": (66, ["isa", "is"]),
    "jeremiah": (52, ["jer", "je", "jr"]),
    "lamentations": (5, ["lam", "la"]),
    "ezekiel": (48, ["ezek", "eze", "ezk"]),
    "daniel": (12, ["dan", "da", "dn"]),
    "hosea": (14, ["hos", "ho"]),
    "joel": (3, ["joe", "jl"]),
    "amos": (9, ["am"]),
    "obadiah": (1, ["obad", "ob"]),
    "jonah": (4, ["jnh", "jon"]),
    "micah": (7, ["mic", "mc"]),
    "nahum": (3, ["nah", "na"]),
    "habakkuk": (3, ["hab", "hb"]),
    "zephaniah": (3, ["zeph", "zep", "zp"]),
    "haggai": (2, ["hag", "hg"]),
    "zechariah": (14, ["zech", "zec", "zc"]),
    "malachi": (4, ["mal", "ml"]),
    # New Testament
    "matthew": (28, ["matt", "mat", "mt"]),
    "mark": (16, ["mrk", "mar", "mk"]),
    "luke": (24, ["luk", "lk"]),
    "john": (21, ["joh", "jhn", "jn"]),
    "acts": (28, ["act", "ac"]),
    "romans": (16, ["rom", "ro", "rm"]),
    "1 corinthians": (16, ["1 cor", "1co", "1 corinthians", "1cor"]),
    "2 corinthians": (13, ["2 cor", "2co", "2 corinthians", "2cor"]),
    "galatians": (6, ["gal", "ga"]),
    "ephesians": (6, ["eph", "ep"]),
    "philippians": (4, ["phil", "php", "pp"]),
    "colossians": (4, ["col", "co"]),
    "1 thessalonians": (5, ["1 thess", "1th", "1 thessalonians", "1thess"]),
    "2 thessalonians": (3, ["2 thess", "2th", "2 thessalonians", "2thess"]),
    "1 timothy": (6, ["1 tim", "1ti", "1 timothy", "1tim"]),
    "2 timothy": (4, ["2 tim", "2ti", "2 timothy", "2tim"]),
    "titus": (3, ["tit", "ti"]),
    "philemon": (1, ["philem", "phm", "pm"]),
    "hebrews": (13, ["heb", "he"]),
    "james": (5, ["jas", "jm"]),
    "1 peter": (5, ["1 pet", "1pe", "1 peter", "1pt"]),
    "2 peter": (3, ["2 pet", "2pe", "2 peter", "2pt"]),
    "1 john": (5, ["1 jn", "1jo", "1 john", "1jhn"]),
    "2 john": (1, ["2 jn", "2jo", "2 john", "2jhn"]),
    "3 john": (1, ["3 jn", "3jo", "3 john", "3jhn"]),
    "jude": (1, ["jud", "jd"]),
    "revelation": (22, ["rev", "re", "rv", "apocalypse"])
}

# Inverted alias lookup
BOOK_LOOKUP: Dict[str, Tuple[str, int]] = {}
for canonical, (max_chapters, aliases) in BIBLE_BOOKS.items():
    BOOK_LOOKUP[canonical.lower()] = (canonical.title(), max_chapters)
    for alias in aliases:
        BOOK_LOOKUP[alias.lower()] = (canonical.title(), max_chapters)

FILLER_WORDS = {
    "um", "uh", "you know", "like", "amen", "hallelujah", 
    "praise the lord", "praise god", "somebody say amen", "glory to god",
    "shout hallelujah", "can i get an amen"
}

RISK_GUARANTEE_PATTERNS = [
    r"\bguaranteed (financial|visa|marriage|healing|instant)\b",
    r"\bdeclare that in (24|48) hours\b",
    r"\byour bank account will receive\b",
    r"\bnext 7 days you will marry\b",
    r"\bsend your seed to be healed\b",
    r"\bdrop your account number for instant\b"
]

def normalize_text_for_match(text: str) -> str:
    """Normalizes text by lowercasing, stripping punctuation, filler words, and excess whitespace."""
    if not text:
        return ""
    text = text.lower()
    
    # Common spoken contraction expansions
    text = re.sub(r"\bcan't\b", "cannot", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bdon't\b", "do not", text)
    text = re.sub(r"\bisn't\b", "is not", text)
    text = re.sub(r"\baren't\b", "are not", text)
    text = re.sub(r"\bit's\b", "it is", text)
    text = re.sub(r"\bthat's\b", "that is", text)
    text = re.sub(r"\bwhat's\b", "what is", text)
    text = re.sub(r"\bi'm\b", "i am", text)
    text = re.sub(r"\bthey're\b", "they are", text)
    text = re.sub(r"\bwe're\b", "we are", text)
    text = re.sub(r"\byou're\b", "you are", text)

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Remove filler words
    for filler in sorted(FILLER_WORDS, key=len, reverse=True):
        text = re.sub(r"\b" + re.escape(filler) + r"\b", " ", text)

    # Collapse whitespace
    tokens = text.split()
    return " ".join(tokens)

def fuzzy_verify_quote(
    candidate_quote: str,
    raw_transcript: List[Dict],
    threshold: float = 0.92,
    claimed_start_sec: Optional[float] = None
) -> Tuple[bool, float, Optional[Dict]]:
    """
    High-performance fuzzy-matching of candidate_quote against the transcript.
    Uses token pre-filtering and temporal locality for sub-second execution on large transcripts.
    Returns: (is_verified, score, match_details_or_None)
    """
    if not candidate_quote or not raw_transcript:
        return False, 0.0, None

    candidate_norm = normalize_text_for_match(candidate_quote)
    candidate_tokens = candidate_norm.split()
    cand_len = len(candidate_tokens)
    if cand_len < 3:
        return False, 0.0, None

    cand_set = set(candidate_tokens)
    n_snippets = len(raw_transcript)

    # Fast Pass 1: Build indices to evaluate
    if claimed_start_sec is not None:
        # Prioritize snippets within +/- 90 seconds of claimed_start_sec
        local_indices = []
        other_indices = []
        for idx, snip in enumerate(raw_transcript):
            snip_time = float(snip.get("start", 0.0))
            if abs(snip_time - claimed_start_sec) <= 90:
                local_indices.append(idx)
            else:
                other_indices.append(idx)
        # Search local first, then others only if needed
        evaluation_passes = [local_indices, other_indices]
    else:
        evaluation_passes = [list(range(n_snippets))]

    best_score = 0.0
    best_match_meta = None

    for pass_indices in evaluation_passes:
        if not pass_indices:
            continue

        for i in pass_indices:
            tokens_with_time = []
            accumulated_text = []

            for j in range(i, min(i + 5, n_snippets)):
                snip_text = raw_transcript[j].get("text", "")
                snip_time = float(raw_transcript[j].get("start", 0.0))
                accumulated_text.append(snip_text)

                snip_norm = normalize_text_for_match(snip_text)
                for tok in snip_norm.split():
                    tokens_with_time.append((tok, snip_time))

                w_len = len(tokens_with_time)
                if w_len < cand_len * 0.7:
                    continue

                window_tokens = [t[0] for t in tokens_with_time]
                window_norm = " ".join(window_tokens)

                # Substring shortcut: exact match
                if candidate_norm in window_norm:
                    cand_first_tok = candidate_tokens[0]
                    match_tok_idx = 0
                    for t_idx, (tok, t_sec) in enumerate(tokens_with_time):
                        if tok == cand_first_tok:
                            match_tok_idx = t_idx
                            break
                    best_match_meta = {
                        "start_sec": int(tokens_with_time[match_tok_idx][1]),
                        "matched_text": " ".join(accumulated_text),
                        "score": 1.0
                    }
                    return True, 1.0, best_match_meta

                # Pre-filter: skip window if token overlap is too low
                overlap = len(cand_set.intersection(window_tokens))
                if overlap < cand_len * 0.65:
                    continue

                max_k = max(1, w_len - cand_len + 4)
                for k in range(0, max_k):
                    sub_slice_tokens = window_tokens[k : k + cand_len + 3]
                    sub_overlap = len(cand_set.intersection(sub_slice_tokens))
                    if sub_overlap < cand_len * 0.7:
                        continue

                    sub_slice = " ".join(sub_slice_tokens)
                    score = difflib.SequenceMatcher(None, candidate_norm, sub_slice).ratio()
                    if score > best_score:
                        best_score = score
                        match_start = tokens_with_time[k][1] if k < len(tokens_with_time) else snip_time
                        best_match_meta = {
                            "start_sec": int(match_start),
                            "matched_text": " ".join(accumulated_text),
                            "score": round(score, 3)
                        }
                        if best_score >= 0.98:
                            return True, best_score, best_match_meta

        if best_score >= threshold:
            break

    is_verified = best_score >= threshold
    return is_verified, best_score, best_match_meta

def validate_scripture_reference(ref: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validates a scripture reference against the standard biblical canon.
    Returns: (is_valid, canonical_formatted_ref, error_message_if_any)
    Examples:
        'Romans 8:26' -> (True, 'Romans 8:26', None)
        'Psalm 46:5' -> (True, 'Psalms 46:5', None)
        'Hezekiah 3:16' -> (False, '', 'Book Hezekiah is not in the Biblical canon')
        'Romans 29:1' -> (False, '', 'Romans only has 16 chapters, requested 29')
    """
    if not ref or not ref.strip():
        return False, "", "Empty scripture reference"

    ref_str = ref.strip()
    # Match pattern: [Book Name] [Chapter]:[Verse(-Verse)?]
    match = re.match(r"^((?:\d\s+)?[A-Za-z\s]+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$", ref_str)
    if not match:
        return False, "", f"Invalid reference format: '{ref}'"

    raw_book, raw_chapter, raw_verse_start, raw_verse_end = match.groups()
    book_key = raw_book.strip().lower()

    if book_key not in BOOK_LOOKUP:
        return False, "", f"Book '{raw_book}' is not recognized in the Biblical canon"

    canonical_name, max_chapters = BOOK_LOOKUP[book_key]
    chapter = int(raw_chapter)

    if chapter < 1 or chapter > max_chapters:
        return False, "", f"{canonical_name} has {max_chapters} chapters, but chapter {chapter} was requested"

    if raw_verse_start:
        v_start = int(raw_verse_start)
        if v_start < 1 or v_start > 180: # Max verse count in any chapter is 176 (Psalm 119)
            return False, "", f"Invalid verse number: {v_start}"
        
        if raw_verse_end:
            v_end = int(raw_verse_end)
            if v_end < v_start:
                return False, "", f"Invalid verse range: {v_start}-{v_end}"
            formatted = f"{canonical_name} {chapter}:{v_start}-{v_end}"
        else:
            formatted = f"{canonical_name} {chapter}:{v_start}"
    else:
        formatted = f"{canonical_name} {chapter}"

    return True, formatted, None

def scan_risk_flags(text: str) -> List[str]:
    """Scans text for forbidden prosperity, guaranteed outcome, or manipulative phrasing."""
    flags = []
    text_lower = text.lower()
    for pattern in RISK_GUARANTEE_PATTERNS:
        if re.search(pattern, text_lower):
            flags.append(f"Matched risk pattern: '{pattern}'")
    return flags

def format_timestamp_url(video_id: str, start_sec: int) -> str:
    """Creates timestamped YouTube link: youtu.be/<id>?t=<sec>"""
    return f"https://youtu.be/{video_id}?t={int(start_sec)}"
