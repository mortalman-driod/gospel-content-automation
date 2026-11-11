"""
Institutional Scripture Engine (src/scripture.py)
Provides verbatim, verified Scripture text across public domain translations (WEB, KJV, ASV)
with dynamic theological theme mapping, 66-book Protestant canon validation,
and absolute zero monocultural defaults.
"""

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple

logger = logging.getLogger("kingdom_journal.scripture")

# 66-Book Protestant Canon with standard chapter counts
CANONICAL_BOOKS = {
    # Old Testament (39)
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36, "Ezra": 10,
    "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150, "Proverbs": 31,
    "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66, "Jeremiah": 52,
    "Lamentations": 5, "Ezekiel": 48, "Daniel": 12, "Hosea": 14, "Joel": 3,
    "Amos": 9, "Obadiah": 1, "Jonah": 4, "Micah": 7, "Nahum": 3, "Habakkuk": 3,
    "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 4,
    # New Testament (27)
    "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28,
    "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6,
    "Ephesians": 6, "Philippians": 4, "Colossians": 4, "1 Thessalonians": 5,
    "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4, "Titus": 3,
    "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5, "2 Peter": 3,
    "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
}

CANONICAL_ALIASES = {
    "psalm": "Psalm",
    "psalms": "Psalm",
    "song of songs": "Song of Solomon",
    "song of solomon": "Song of Solomon",
    "canticles": "Song of Solomon",
}

# Verified Offline Scripture Library across Theological Themes
VERIFIED_SCRIPTURES = {
    # Faith & Trust
    "HEBREWS 11:1": {
        "text": "Now faith is assurance of things hoped for, proof of things not seen.",
        "reference": "Hebrews 11:1",
        "translation": "WEB"
    },
    "PROVERBS 3:5-6": {
        "text": "Trust in Yahweh with all your heart, and don't lean on your own understanding. In all your ways acknowledge him, and he will make your paths straight.",
        "reference": "Proverbs 3:5-6",
        "translation": "WEB"
    },
    "MARK 11:23": {
        "text": "For most certainly I tell you, whoever may tell this mountain, 'Be taken up and cast into the sea,' and doesn't doubt in his heart, but believes that what he says is happening; he shall have whatever he says.",
        "reference": "Mark 11:23",
        "translation": "WEB"
    },
    # Prayer & Altar & The Secret Place
    "MATTHEW 6:6": {
        "text": "But you, when you pray, enter into your inner room, and having shut your door, pray to your Father who is in secret; and your Father who sees in secret will reward you openly.",
        "reference": "Matthew 6:6",
        "translation": "WEB"
    },
    "LUKE 18:1": {
        "text": "He also spoke a parable to them that they must always pray, and not give up.",
        "reference": "Luke 18:1",
        "translation": "WEB"
    },
    "JEREMIAH 33:3": {
        "text": "Call to me, and I will answer you, and will show you great and difficult things, which you don't know.",
        "reference": "Jeremiah 33:3",
        "translation": "WEB"
    },
    "1 THESSALONIANS 5:17": {
        "text": "Pray without ceasing.",
        "reference": "1 Thessalonians 5:17",
        "translation": "WEB"
    },
    "JAMES 5:16": {
        "text": "Confess your offenses to one another, and pray for one another, that you may be healed. The effective, earnest prayer of a righteous man is powerfully effective.",
        "reference": "James 5:16",
        "translation": "WEB"
    },
    # Waiting & Patience & Timing
    "ISAIAH 40:31": {
        "text": "But those who wait for Yahweh will renew their strength. They will mount up with wings like eagles. They will run, and not be weary. They will walk, and not faint.",
        "reference": "Isaiah 40:31",
        "translation": "WEB"
    },
    "LAMENTATIONS 3:25-26": {
        "text": "Yahweh is good to those who wait for him, to the soul who seeks him. It is good that a man should hope and quietly wait for the salvation of Yahweh.",
        "reference": "Lamentations 3:25-26",
        "translation": "WEB"
    },
    "PSALM 27:14": {
        "text": "Wait for Yahweh. Be strong, and let your heart take courage. Yes, wait for Yahweh.",
        "reference": "Psalm 27:14",
        "translation": "WEB"
    },
    "GALATIANS 6:9": {
        "text": "Let us not become weary in doing good; for we will reap in due season, if we don't give up.",
        "reference": "Galatians 6:9",
        "translation": "WEB"
    },
    # Spiritual Warfare & Kingdom Victory
    "2 CORINTHIANS 10:4": {
        "text": "For the weapons of our warfare are not of the flesh, but mighty before God to the throwing down of strongholds.",
        "reference": "2 Corinthians 10:4",
        "translation": "WEB"
    },
    "ROMANS 8:37": {
        "text": "No, in all these things, we are more than conquerors through him who loved us.",
        "reference": "Romans 8:37",
        "translation": "WEB"
    },
    "1 JOHN 4:4": {
        "text": "You are of God, little children, and have overcome them; because greater is he who is in you than he who is in the world.",
        "reference": "1 John 4:4",
        "translation": "WEB"
    },
    "EPHESIANS 6:11": {
        "text": "Put on the whole armor of God, that you may be able to stand against the wiles of the devil.",
        "reference": "Ephesians 6:11",
        "translation": "WEB"
    },
    # Grace & Mercy & Redemption
    "HEBREWS 4:16": {
        "text": "Let us therefore draw near with boldness to the throne of grace, that we may receive mercy, and may find grace for help in time of need.",
        "reference": "Hebrews 4:16",
        "translation": "WEB"
    },
    "2 CORINTHIANS 12:9": {
        "text": "He has said to me, 'My grace is sufficient for you, for my power is made perfect in weakness.' Most gladly therefore I will rather glory in my weaknesses, that the power of Christ may rest on me.",
        "reference": "2 Corinthians 12:9",
        "translation": "WEB"
    },
    "TITUS 2:11": {
        "text": "For the grace of God has appeared, bringing salvation to all men.",
        "reference": "Titus 2:11",
        "translation": "WEB"
    },
    # Divine Purpose & Calling
    "JEREMIAH 29:11": {
        "text": "For I know the thoughts that I think toward you, says Yahweh, thoughts of peace, and not of evil, to give you hope and a future.",
        "reference": "Jeremiah 29:11",
        "translation": "WEB"
    },
    "ROMANS 8:28": {
        "text": "We know that all things work together for good for those who love God, for those who are called according to his purpose.",
        "reference": "Romans 8:28",
        "translation": "WEB"
    },
    "2 TIMOTHY 1:9": {
        "text": "Who saved us and called us with a holy calling, not according to our works, but according to his own purpose and grace, which was given to us in Christ Jesus before times eternal.",
        "reference": "2 Timothy 1:9",
        "translation": "WEB"
    },
    # Peace, Stillness & Comfort
    "PSALM 46:10": {
        "text": "Be still, and know that I am God. I will be exalted among the nations. I will be exalted in the earth.",
        "reference": "Psalm 46:10",
        "translation": "WEB"
    },
    "JOHN 14:27": {
        "text": "Peace I leave with you. My peace I give to you; not as the world gives, give I to you. Don't let your heart be troubled, neither let it be fearful.",
        "reference": "John 14:27",
        "translation": "WEB"
    },
    "PHILIPPIANS 4:6-7": {
        "text": "In nothing be anxious, but in everything, by prayer and petition with thanksgiving, let your requests be made known to God. And the peace of God, which surpasses all understanding, will guard your hearts and your thoughts in Christ Jesus.",
        "reference": "Philippians 4:6-7",
        "translation": "WEB"
    },
    # Word of God & Guidance
    "PSALM 119:105": {
        "text": "Your word is a lamp to my feet, and a light for my path.",
        "reference": "Psalm 119:105",
        "translation": "WEB"
    },
    "HEBREWS 4:12": {
        "text": "For the word of God is living and active, and sharper than any two-edged sword, piercing even to the dividing of soul and spirit, of both joints and marrow, and is able to discern the thoughts and intentions of the heart.",
        "reference": "Hebrews 4:12",
        "translation": "WEB"
    },
    # Praise, Worship & Consecration
    "JOHN 4:24": {
        "text": "God is spirit, and those who worship him must worship in spirit and truth.",
        "reference": "John 4:24",
        "translation": "WEB"
    },
    "PSALM 100:4": {
        "text": "Enter into his gates with thanksgiving, and into his courts with praise. Give thanks to him, and bless his name.",
        "reference": "Psalm 100:4",
        "translation": "WEB"
    },
    "GALATIANS 2:20": {
        "text": "I have been crucified with Christ, and it is no longer I that live, but Christ living in me. That life which I now live in the flesh, I live by faith in the Son of God, who loved me, and gave himself up for me.",
        "reference": "Galatians 2:20",
        "translation": "WEB"
    },
    "ROMANS 8:26": {
        "text": "In the same way, the Spirit also helps our weaknesses, for we don't know how to pray as we ought; but the Spirit himself makes intercession for us with groanings which can't be uttered.",
        "reference": "Romans 8:26",
        "translation": "WEB"
    }
}

THEME_KEYWORD_MAP = [
    (["faith", "trust", "doubt", "believe", "mountain", "impossible"], "HEBREWS 11:1"),
    (["lean", "heart", "straight", "paths", "understanding"], "PROVERBS 3:5-6"),
    (["prayer", "secret", "altar", "pray", "closet", "inner room"], "MATTHEW 6:6"),
    (["wait", "waiting", "weary", "strength", "eagles", "patience"], "ISAIAH 40:31"),
    (["warfare", "stronghold", "weapons", "battle", "fight"], "2 CORINTHIANS 10:4"),
    (["conqueror", "defeat", "victory", "overcome", "triumph"], "ROMANS 8:37"),
    (["grace", "mercy", "throne", "weakness", "sufficient"], "HEBREWS 4:16"),
    (["purpose", "calling", "future", "plans", "destiny"], "JEREMIAH 29:11"),
    (["still", "stillness", "peace", "quiet", "rest", "storm"], "PSALM 46:10"),
    (["word", "scripture", "lamp", "light", "bible", "truth"], "PSALM 119:105"),
    (["worship", "praise", "thanksgiving", "glory", "altar"], "JOHN 4:24"),
    (["cross", "crucified", "die", "surrender", "life"], "GALATIANS 2:20"),
    (["spirit", "intercession", "groaning", "weakness"], "ROMANS 8:26"),
]

def clean_ref_key(ref: str) -> str:
    """Normalizes scripture reference string to clean dictionary key."""
    if not ref:
        return ""
    primary = ref.split("•")[0].split(";")[0].split("[")[0].strip().upper()
    return re.sub(r"\s+", " ", primary)

def validate_canonical_reference(ref: str) -> Tuple[bool, str]:
    """Validates reference against the 66 canonical books of the Bible."""
    if not ref:
        return False, ""
    clean = ref.strip()
    match = re.match(r"^(\d?\s*[A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?", clean)
    if not match:
        return False, ""
    book_raw = match.group(1).strip()
    book_lower = book_raw.lower()

    # Check direct canonical list and common aliases
    if book_lower in CANONICAL_ALIASES:
        canonical_name = CANONICAL_ALIASES[book_lower]
        return True, f"{canonical_name} {clean[len(book_raw):].strip()}"

    for canonical in CANONICAL_BOOKS:
        c_low = canonical.lower()
        if c_low == book_lower or c_low.replace(" ", "") == book_lower.replace(" ", "") or (c_low.endswith("s") and c_low[:-1] == book_lower):
            return True, f"{canonical} {clean[len(book_raw):].strip()}"
    return False, ""

def fetch_online_scripture(reference: str, translation: str = "web") -> Optional[Dict]:
    """Fetches verbatim scripture text via bible-api.com with timeout protection."""
    try:
        clean_ref = reference.split("•")[0].split(";")[0].split("[")[0].strip()
        encoded = urllib.parse.quote(clean_ref)
        url = f"https://bible-api.com/{encoded}?translation={translation}"
        req = urllib.request.Request(url, headers={"User-Agent": "KingdomJournal/4.0 (Autonomous Scripture Engine)"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data.get("text", "").strip().replace("\n", " ")
            ref_clean = data.get("reference", clean_ref)
            if text:
                return {
                    "text": text,
                    "reference": ref_clean,
                    "translation": translation.upper()
                }
    except Exception as e:
        logger.debug(f"Online scripture fetch skipped for {reference}: {e}")
    return None

def get_scripture_for_theme(
    theme: str = "",
    quote_text: str = "",
    preferred_ref: Optional[str] = None
) -> Dict:
    """
    Selects verified Scripture text dynamically:
    1. If preferred_ref is valid and provided, uses it.
    2. Else matches sermon theme and quote tokens against theological map.
    3. Guarantees diversity: NEVER defaults to a single monoculture verse.
    """
    # 1. Preferred reference check
    if preferred_ref:
        is_valid, canon_ref = validate_canonical_reference(preferred_ref)
        if is_valid:
            key = clean_ref_key(canon_ref)
            if key in VERIFIED_SCRIPTURES:
                return VERIFIED_SCRIPTURES[key]
            # Try fetching online
            online = fetch_online_scripture(canon_ref)
            if online:
                return online

    # 2. Semantic matching against theme & quote
    corpus = f"{theme} {quote_text}".lower()
    for keywords, target_key in THEME_KEYWORD_MAP:
        if any(kw in corpus for kw in keywords):
            if target_key in VERIFIED_SCRIPTURES:
                return VERIFIED_SCRIPTURES[target_key]

    # 3. Deterministic rotation across foundational library based on text hash
    keys = list(VERIFIED_SCRIPTURES.keys())
    diverse_keys = [k for k in keys if k != "ROMANS 8:26"]
    idx = abs(hash(f"{theme}_{quote_text}")) % len(diverse_keys)
    selected_key = diverse_keys[idx]
    return VERIFIED_SCRIPTURES[selected_key]
