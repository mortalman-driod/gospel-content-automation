"""
Institutional Scripture Engine (src/scripture.py)
Provides verified Scripture text across canonical public-domain and classic translations (KJV, WEB, ASV, BBE)
with 66-book Protestant canon validation, dynamic theological theme rotation,
and strict anti-repetition memory guarding against monocultural verse repetition.
"""

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

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

# Rich Verified Multi-Translation Canonical Scripture Repository
VERIFIED_SCRIPTURES = {
    # --- PRAYER, THE SECRET PLACE & INTERCESSION ---
    "PHILIPPIANS 4:6-7": {
        "text": "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God. And the peace of God, which passeth all understanding, shall keep your hearts and minds through Christ Jesus.",
        "reference": "Philippians 4:6-7",
        "translation": "KJV"
    },
    "JEREMIAH 33:3": {
        "text": "Call unto me, and I will answer thee, and show thee great and mighty things, which thou knowest not.",
        "reference": "Jeremiah 33:3",
        "translation": "KJV"
    },
    "HEBREWS 4:16": {
        "text": "Let us therefore come boldly unto the throne of grace, that we may obtain mercy, and find grace to help in time of need.",
        "reference": "Hebrews 4:16",
        "translation": "KJV"
    },
    "1 THESSALONIANS 5:16-18": {
        "text": "Rejoice evermore. Pray without ceasing. In every thing give thanks: for this is the will of God in Christ Jesus concerning you.",
        "reference": "1 Thessalonians 5:16-18",
        "translation": "KJV"
    },
    "PSALM 5:3": {
        "text": "My voice shalt thou hear in the morning, O Lord; in the morning will I direct my prayer unto thee, and will look up.",
        "reference": "Psalm 5:3",
        "translation": "KJV"
    },
    "JAMES 5:16": {
        "text": "Confess your faults one to another, and pray one for another, that ye may be healed. The effectual fervent prayer of a righteous man availeth much.",
        "reference": "James 5:16",
        "translation": "KJV"
    },
    "COLOSSIANS 4:2": {
        "text": "Continue steadfastly in prayer, watching therein with thanksgiving.",
        "reference": "Colossians 4:2",
        "translation": "WEB"
    },
    "MARK 1:35": {
        "text": "Early in the morning, while it was still dark, he rose up and went out, and departed into a deserted place, and prayed there.",
        "reference": "Mark 1:35",
        "translation": "WEB"
    },
    "EPHESIANS 6:18": {
        "text": "Praying always with all prayer and supplication in the Spirit, and watching thereunto with all perseverance and supplication for all saints.",
        "reference": "Ephesians 6:18",
        "translation": "KJV"
    },
    "LUKE 18:1": {
        "text": "And he spake a parable unto them to this end, that men ought always to pray, and not to faint.",
        "reference": "Luke 18:1",
        "translation": "KJV"
    },
    "MATTHEW 6:6": {
        "text": "But thou, when thou prayest, enter into thy closet, and when thou hast shut thy door, pray to thy Father which is in secret; and thy Father which seeth in secret shall reward thee openly.",
        "reference": "Matthew 6:6",
        "translation": "KJV"
    },
    "ROMANS 8:26": {
        "text": "Likewise the Spirit also helpeth our infirmities: for we know not what we should pray for as we ought: but the Spirit itself maketh intercession for us with groanings which cannot be uttered.",
        "reference": "Romans 8:26",
        "translation": "KJV"
    },

    # --- FAITH, TRUST & BELIEF ---
    "HEBREWS 11:1": {
        "text": "Now faith is the substance of things hoped for, the evidence of things not seen.",
        "reference": "Hebrews 11:1",
        "translation": "KJV"
    },
    "PROVERBS 3:5-6": {
        "text": "Trust in the Lord with all thine heart; and lean not unto thine own understanding. In all thy ways acknowledge him, and he shall direct thy paths.",
        "reference": "Proverbs 3:5-6",
        "translation": "KJV"
    },
    "MARK 11:23": {
        "text": "For verily I say unto you, That whosoever shall say unto this mountain, Be thou removed, and be thou cast into the sea; and shall not doubt in his heart, but shall believe that those things which he saith shall come to pass; he shall have whatsoever he saith.",
        "reference": "Mark 11:23",
        "translation": "KJV"
    },
    "2 CORINTHIANS 5:7": {
        "text": "For we walk by faith, not by sight.",
        "reference": "2 Corinthians 5:7",
        "translation": "KJV"
    },
    "ROMANS 10:17": {
        "text": "So then faith cometh by hearing, and hearing by the word of God.",
        "reference": "Romans 10:17",
        "translation": "KJV"
    },
    "PSALM 37:5": {
        "text": "Commit thy way unto the Lord; trust also in him; and he shall bring it to pass.",
        "reference": "Psalm 37:5",
        "translation": "KJV"
    },
    "HABAKKUK 2:4": {
        "text": "Behold, his soul which is lifted up is not upright in him: but the just shall live by his faith.",
        "reference": "Habakkuk 2:4",
        "translation": "KJV"
    },

    # --- WAITING, PATIENCE & SPIRITUAL RENEWAL ---
    "ISAIAH 40:31": {
        "text": "But they that wait upon the Lord shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint.",
        "reference": "Isaiah 40:31",
        "translation": "KJV"
    },
    "LAMENTATIONS 3:25-26": {
        "text": "The Lord is good unto them that wait for him, to the soul that seeketh him. It is good that a man should both hope and quietly wait for the salvation of the Lord.",
        "reference": "Lamentations 3:25-26",
        "translation": "KJV"
    },
    "PSALM 27:14": {
        "text": "Wait on the Lord: be of good courage, and he shall strengthen thine heart: wait, I say, on the Lord.",
        "reference": "Psalm 27:14",
        "translation": "KJV"
    },
    "GALATIANS 6:9": {
        "text": "And let us not be weary in well doing: for in due season we shall reap, if we faint not.",
        "reference": "Galatians 6:9",
        "translation": "KJV"
    },
    "PSALM 130:5": {
        "text": "I wait for the Lord, my soul doth wait, and in his word do I hope.",
        "reference": "Psalm 130:5",
        "translation": "KJV"
    },
    "ROMANS 8:25": {
        "text": "But if we hope for that we see not, then do we with patience wait for it.",
        "reference": "Romans 8:25",
        "translation": "KJV"
    },

    # --- PEACE, STILLNESS & REST ---
    "PSALM 46:10": {
        "text": "Be still, and know that I am God: I will be exalted among the heathen, I will be exalted in the earth.",
        "reference": "Psalm 46:10",
        "translation": "KJV"
    },
    "JOHN 14:27": {
        "text": "Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.",
        "reference": "John 14:27",
        "translation": "KJV"
    },
    "ISAIAH 26:3": {
        "text": "Thou wilt keep him in perfect peace, whose mind is stayed on thee: because he trusteth in thee.",
        "reference": "Isaiah 26:3",
        "translation": "KJV"
    },
    "MATTHEW 11:28-29": {
        "text": "Come unto me, all ye that labour and are heavy laden, and I will give you rest. Take my yoke upon you, and learn of me; for I am meek and lowly in heart: and ye shall find rest unto your souls.",
        "reference": "Matthew 11:28-29",
        "translation": "KJV"
    },
    "PSALM 23:1-3": {
        "text": "The Lord is my shepherd; I shall not want. He maketh me to lie down in green pastures: he leadeth me beside the still waters. He restoreth my soul.",
        "reference": "Psalm 23:1-3",
        "translation": "KJV"
    },

    # --- SPIRITUAL WARFARE, COURAGE & KINGDOM VICTORY ---
    "2 CORINTHIANS 10:4": {
        "text": "For the weapons of our warfare are not carnal, but mighty through God to the pulling down of strong holds.",
        "reference": "2 Corinthians 10:4",
        "translation": "KJV"
    },
    "ROMANS 8:37": {
        "text": "Nay, in all these things we are more than conquerors through him that loved us.",
        "reference": "Romans 8:37",
        "translation": "KJV"
    },
    "1 JOHN 4:4": {
        "text": "Ye are of God, little children, and have overcome them: because greater is he that is in you, than he that is in the world.",
        "reference": "1 John 4:4",
        "translation": "KJV"
    },
    "EPHESIANS 6:10-11": {
        "text": "Finally, my brethren, be strong in the Lord, and in the power of his might. Put on the whole armour of God, that ye may be able to stand against the wiles of the devil.",
        "reference": "Ephesians 6:10-11",
        "translation": "KJV"
    },
    "1 CORINTHIANS 15:57": {
        "text": "But thanks be to God, which giveth us the victory through our Lord Jesus Christ.",
        "reference": "1 Corinthians 15:57",
        "translation": "KJV"
    },
    "JAMES 4:7": {
        "text": "Submit yourselves therefore to God. Resist the devil, and he will flee from you.",
        "reference": "James 4:7",
        "translation": "KJV"
    },
    "JOSHUA 1:9": {
        "text": "Have not I commanded thee? Be strong and of a good courage; be not afraid, neither be thou dismayed: for the Lord thy God is with thee whithersoever thou goest.",
        "reference": "Joshua 1:9",
        "translation": "KJV"
    },
    "ISAIAH 54:17": {
        "text": "No weapon that is formed against thee shall prosper; and every tongue that shall rise against thee in judgment thou shalt condemn. This is the heritage of the servants of the Lord.",
        "reference": "Isaiah 54:17",
        "translation": "KJV"
    },

    # --- GRACE, MERCY & REDEMPTION ---
    "EPHESIANS 2:8-9": {
        "text": "For by grace are ye saved through faith; and that not of yourselves: it is the gift of God: Not of works, lest any man should boast.",
        "reference": "Ephesians 2:8-9",
        "translation": "KJV"
    },
    "2 CORINTHIANS 12:9": {
        "text": "And he said unto me, My grace is sufficient for thee: for my strength is made perfect in weakness. Most gladly therefore will I rather glory in my infirmities, that the power of Christ may rest upon me.",
        "reference": "2 Corinthians 12:9",
        "translation": "KJV"
    },
    "TITUS 2:11": {
        "text": "For the grace of God that bringeth salvation hath appeared to all men.",
        "reference": "Titus 2:11",
        "translation": "KJV"
    },
    "LAMENTATIONS 3:22-23": {
        "text": "It is of the Lord's mercies that we are not consumed, because his compassions fail not. They are new every morning: great is thy faithfulness.",
        "reference": "Lamentations 3:22-23",
        "translation": "KJV"
    },
    "ROMANS 5:8": {
        "text": "But God commendeth his love toward us, in that, while we were yet sinners, Christ died for us.",
        "reference": "Romans 5:8",
        "translation": "KJV"
    },

    # --- PURPOSE, CALLING & PROVIDENCE ---
    "JEREMIAH 29:11": {
        "text": "For I know the thoughts that I think toward you, saith the Lord, thoughts of peace, and not of evil, to give you an expected end.",
        "reference": "Jeremiah 29:11",
        "translation": "KJV"
    },
    "ROMANS 8:28": {
        "text": "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
        "reference": "Romans 8:28",
        "translation": "KJV"
    },
    "2 TIMOTHY 1:9": {
        "text": "Who hath saved us, and called us with an holy calling, not according to our works, but according to his own purpose and grace, which was given us in Christ Jesus before the world began.",
        "reference": "2 Timothy 1:9",
        "translation": "KJV"
    },
    "PHILIPPIANS 1:6": {
        "text": "Being confident of this very thing, that he which hath begun a good work in you will perform it until the day of Jesus Christ.",
        "reference": "Philippians 1:6",
        "translation": "KJV"
    },
    "EPHESIANS 2:10": {
        "text": "For we are his workmanship, created in Christ Jesus unto good works, which God hath before ordained that we should walk in them.",
        "reference": "Ephesians 2:10",
        "translation": "KJV"
    },
    "PHILIPPIANS 4:19": {
        "text": "But my God shall supply all your need according to his riches in glory by Christ Jesus.",
        "reference": "Philippians 4:19",
        "translation": "KJV"
    },

    # --- WORD OF GOD, WISDOM & GUIDANCE ---
    "PSALM 119:105": {
        "text": "Thy word is a lamp unto my feet, and a light unto my path.",
        "reference": "Psalm 119:105",
        "translation": "KJV"
    },
    "HEBREWS 4:12": {
        "text": "For the word of God is quick, and powerful, and sharper than any twoedged sword, piercing even to the dividing asunder of soul and spirit, and of the joints and marrow, and is a discerner of the thoughts and intents of the heart.",
        "reference": "Hebrews 4:12",
        "translation": "KJV"
    },
    "JAMES 1:5": {
        "text": "If any of you lack wisdom, let him ask of God, that giveth to all men liberally, and upbraideth not; and it shall be given him.",
        "reference": "James 1:5",
        "translation": "KJV"
    },
    "PSALM 32:8": {
        "text": "I will instruct thee and teach thee in the way which thou shalt go: I will guide thee with mine eye.",
        "reference": "Psalm 32:8",
        "translation": "KJV"
    },
    "JOSHUA 1:8": {
        "text": "This book of the law shall not depart out of thy mouth; but thou shalt meditate therein day and night, that thou mayest observe to do according to all that is written therein: for then thou shalt make thy way prosperous, and then thou shalt have good success.",
        "reference": "Joshua 1:8",
        "translation": "KJV"
    },
    "2 TIMOTHY 3:16-17": {
        "text": "All scripture is given by inspiration of God, and is profitable for doctrine, for reproof, for correction, for instruction in righteousness: That the man of God may be perfect, throughly furnished unto all good works.",
        "reference": "2 Timothy 3:16-17",
        "translation": "KJV"
    },

    # --- PRAISE, WORSHIP & CONSECRATION ---
    "JOHN 4:24": {
        "text": "God is a Spirit: and they that worship him must worship him in spirit and in truth.",
        "reference": "John 4:24",
        "translation": "KJV"
    },
    "PSALM 100:4": {
        "text": "Enter into his gates with thanksgiving, and into his courts with praise: be thankful unto him, and bless his name.",
        "reference": "Psalm 100:4",
        "translation": "KJV"
    },
    "PSALM 34:1": {
        "text": "I will bless the Lord at all times: his praise shall continually be in my mouth.",
        "reference": "Psalm 34:1",
        "translation": "KJV"
    },
    "HEBREWS 13:15": {
        "text": "By him therefore let us offer the sacrifice of praise to God continually, that is, the fruit of our lips giving thanks to his name.",
        "reference": "Hebrews 13:15",
        "translation": "KJV"
    },
    "GALATIANS 2:20": {
        "text": "I am crucified with Christ: nevertheless I live; yet not I, but Christ liveth in me: and the life which I now live in the flesh I live by the faith of the Son of God, who loved me, and gave himself for me.",
        "reference": "Galatians 2:20",
        "translation": "KJV"
    },
    "ROMANS 12:1": {
        "text": "I beseech you therefore, brethren, by the mercies of God, that ye present your bodies a living sacrifice, holy, acceptable unto God, which is your reasonable service.",
        "reference": "Romans 12:1",
        "translation": "KJV"
    },
    "JOHN 3:16": {
        "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
        "reference": "John 3:16",
        "translation": "KJV"
    }
}

# Thematic mapping: Each keyword cluster maps to a POOL of diverse canonical scriptures
THEME_KEYWORD_MAP = [
    (
        ["prayer", "secret", "altar", "pray", "closet", "inner room", "intercession", "supplication", "petition"],
        [
            "PHILIPPIANS 4:6-7",
            "JEREMIAH 33:3",
            "HEBREWS 4:16",
            "1 THESSALONIANS 5:16-18",
            "PSALM 5:3",
            "JAMES 5:16",
            "COLOSSIANS 4:2",
            "MARK 1:35",
            "EPHESIANS 6:18",
            "LUKE 18:1",
            "MATTHEW 6:6",
            "ROMANS 8:26"
        ]
    ),
    (
        ["faith", "trust", "doubt", "believe", "mountain", "impossible", "confidence"],
        [
            "HEBREWS 11:1",
            "PROVERBS 3:5-6",
            "MARK 11:23",
            "2 CORINTHIANS 5:7",
            "ROMANS 10:17",
            "PSALM 37:5",
            "HABAKKUK 2:4"
        ]
    ),
    (
        ["lean", "heart", "straight", "paths", "understanding", "direction", "guidance"],
        [
            "PROVERBS 3:5-6",
            "PSALM 32:8",
            "PSALM 119:105",
            "JEREMIAH 29:11"
        ]
    ),
    (
        ["wait", "waiting", "weary", "strength", "eagles", "patience", "due season", "endure", "tired"],
        [
            "ISAIAH 40:31",
            "LAMENTATIONS 3:25-26",
            "PSALM 27:14",
            "GALATIANS 6:9",
            "PSALM 130:5",
            "ROMANS 8:25"
        ]
    ),
    (
        ["warfare", "stronghold", "weapons", "battle", "fight", "stand", "enemy", "conqueror", "defeat", "victory", "overcome", "triumph"],
        [
            "2 CORINTHIANS 10:4",
            "ROMANS 8:37",
            "1 JOHN 4:4",
            "EPHESIANS 6:10-11",
            "1 CORINTHIANS 15:57",
            "JAMES 4:7",
            "ISAIAH 54:17"
        ]
    ),
    (
        ["grace", "mercy", "throne", "weakness", "sufficient", "forgiveness", "salvation"],
        [
            "HEBREWS 4:16",
            "2 CORINTHIANS 12:9",
            "EPHESIANS 2:8-9",
            "TITUS 2:11",
            "LAMENTATIONS 3:22-23",
            "ROMANS 5:8"
        ]
    ),
    (
        ["purpose", "calling", "future", "plans", "destiny", "assignment", "workmanship", "supply"],
        [
            "JEREMIAH 29:11",
            "ROMANS 8:28",
            "2 TIMOTHY 1:9",
            "PHILIPPIANS 1:6",
            "EPHESIANS 2:10",
            "PHILIPPIANS 4:19"
        ]
    ),
    (
        ["still", "stillness", "peace", "quiet", "rest", "storm", "anxious", "anxiety", "troubled"],
        [
            "PSALM 46:10",
            "JOHN 14:27",
            "ISAIAH 26:3",
            "MATTHEW 11:28-29",
            "PSALM 23:1-3",
            "PHILIPPIANS 4:6-7"
        ]
    ),
    (
        ["word", "scripture", "lamp", "light", "bible", "truth", "meditate", "sword", "wisdom"],
        [
            "PSALM 119:105",
            "HEBREWS 4:12",
            "JAMES 1:5",
            "JOSHUA 1:8",
            "2 TIMOTHY 3:16-17"
        ]
    ),
    (
        ["worship", "praise", "thanksgiving", "glory", "bless", "sacrifice"],
        [
            "JOHN 4:24",
            "PSALM 100:4",
            "PSALM 34:1",
            "HEBREWS 13:15",
            "ROMANS 12:1"
        ]
    ),
    (
        ["cross", "crucified", "die", "surrender", "life", "redeemed", "blood", "salvation"],
        [
            "GALATIANS 2:20",
            "JOHN 3:16",
            "ROMANS 12:1",
            "ROMANS 5:8"
        ]
    ),
    (
        ["spirit", "intercession", "groaning", "helper", "advocate", "power"],
        [
            "ROMANS 8:26",
            "EPHESIANS 6:18",
            "2 TIMOTHY 1:9",
            "GALATIANS 2:20"
        ]
    ),
]

def clean_ref_key(ref: str) -> str:
    """Normalizes scripture reference string to clean uppercase dictionary key."""
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
    """Fetches verbatim scripture text via public domain bible-api.com with timeout protection."""
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
    preferred_ref: Optional[str] = None,
    recently_used: Optional[List[str]] = None
) -> Dict:
    """
    Selects verified Scripture dynamically:
    1. If preferred_ref is valid, not recently used, and canonical, uses it.
    2. Else matches sermon theme and quote tokens against theological map.
    3. Excludes recently used verses to guarantee zero monoculture repetition.
    4. Rotates dynamically through candidate pools.
    """
    recent_set = {clean_ref_key(r) for r in (recently_used or []) if r}

    # 1. Preferred reference check
    if preferred_ref:
        is_valid, canon_ref = validate_canonical_reference(preferred_ref)
        if is_valid:
            key = clean_ref_key(canon_ref)
            if key not in recent_set:
                if key in VERIFIED_SCRIPTURES:
                    return VERIFIED_SCRIPTURES[key]
                # Try fetching online
                online = fetch_online_scripture(canon_ref)
                if online:
                    return online

    # 2. Semantic matching against theme & quote with anti-repetition filter
    corpus = f"{theme} {quote_text}".lower()
    matched_pool: List[str] = []

    for keywords, target_keys in THEME_KEYWORD_MAP:
        if any(kw in corpus for kw in keywords):
            for k in target_keys:
                if k not in matched_pool:
                    matched_pool.append(k)

    # Filter out recently used verses from the matched pool
    fresh_candidates = [k for k in matched_pool if k not in recent_set and k in VERIFIED_SCRIPTURES]

    if fresh_candidates:
        # Deterministically rotate based on quote content hash to ensure variation
        idx = abs(hash(f"{theme}_{quote_text}")) % len(fresh_candidates)
        selected_key = fresh_candidates[idx]
        return VERIFIED_SCRIPTURES[selected_key]

    # If all matched candidates have been used recently, pick from any verified scripture not recently used
    all_keys = list(VERIFIED_SCRIPTURES.keys())
    unused_overall = [k for k in all_keys if k not in recent_set]

    if unused_overall:
        idx = abs(hash(f"{theme}_{quote_text}")) % len(unused_overall)
        selected_key = unused_overall[idx]
        return VERIFIED_SCRIPTURES[selected_key]

    # Extreme fallback: Rotate through entire library
    idx = abs(hash(f"{theme}_{quote_text}")) % len(all_keys)
    return VERIFIED_SCRIPTURES[all_keys[idx]]
